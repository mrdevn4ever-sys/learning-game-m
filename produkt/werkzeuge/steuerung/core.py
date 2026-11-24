"""Transaktionaler Kern. Jede Uhrzeit ist explizit (UTC-Sekunden).

Die Bibliothek ist kein Berechtigungsdienst: Dateirechte/Identitaetstrennung
muessen ausserhalb dieses lokalen Kerns durchgesetzt werden.
"""

from contextlib import contextmanager
import sqlite3
import uuid

from .contracts import (Conflict, Invalid, Lease, StoreError, bootstrap, canonical,
                        digest, identifier, integer, parse_json, runtime_path, sha,
                        text)
from .schema import SCHEMA, SCHEMA_VERSION
from .journal import Effects
from .recovery import Recovery


TRANSITIONS = {
    "planned": {"ready", "blocked", "superseded"},
    "ready": {"blocked", "superseded"},
    "leased": {"running", "retry_wait", "blocked"},
    "running": {"verifying", "retry_wait", "reconciling", "blocked"},
    "verifying": {"done", "retry_wait", "blocked"},
    "retry_wait": {"ready", "blocked", "superseded"},
    "reconciling": {"running", "verifying", "blocked"},
    "blocked": {"planned", "reconciling", "superseded"},
    "done": set(),
    "superseded": set(),
}


class Controller(Effects, Recovery):
    def __init__(self, path):
        self.path = runtime_path(path)
        if not self.path.is_file():
            raise Invalid("Datenbank fehlt; explizite Anlage erforderlich")
        with self._connection(readonly=True) as db:
            if db.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
                raise Invalid("Unbekannte Datenbankversion")
            meta = dict(db.execute("SELECT key, value FROM meta"))
            if not {"epoch", "fence", "clock", "recovery_locked"} <= meta.keys():
                raise Invalid("Unvollstaendige Steuerungsdatenbank")

    @classmethod
    def create(cls, path):
        path = runtime_path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("xb"):
                pass
        except FileExistsError as exc:
            raise Conflict("Datenbank existiert bereits") from exc
        db = None
        try:
            db = sqlite3.connect(path, isolation_level=None)
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA synchronous=FULL")
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("PRAGMA temp_store=MEMORY")
            db.executescript(SCHEMA)
            db.execute("BEGIN IMMEDIATE")
            db.executemany("INSERT INTO meta VALUES (?, ?)", [
                ("epoch", uuid.uuid4().hex), ("fence", "0"), ("clock", "0"),
                ("recovery_locked", "0"),
            ])
            db.commit()
        except BaseException:
            if db is not None:
                db.close()
                db = None
            # Nur die gerade exklusiv erstellte, unvollstaendige Datei entfernen.
            path.unlink(missing_ok=True)
            raise
        finally:
            if db is not None:
                db.close()
        return cls(path)

    @contextmanager
    def _connection(self, readonly=False):
        uri = self.path.as_uri() + ("?mode=ro" if readonly else "?mode=rw")
        db = sqlite3.connect(uri, uri=True, timeout=15, isolation_level=None)
        db.row_factory = sqlite3.Row
        try:
            db.execute("PRAGMA busy_timeout=15000")
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("PRAGMA temp_store=MEMORY")
            if readonly:
                db.execute("PRAGMA query_only=ON")
            else:
                db.execute("PRAGMA synchronous=FULL")
            yield db
        finally:
            db.close()

    @staticmethod
    def _meta(db, key):
        return db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()[0]

    @staticmethod
    def _set_meta(db, key, value):
        db.execute("UPDATE meta SET value=? WHERE key=?", (str(value), key))

    @contextmanager
    def _transaction(self, now, allow_recovery=False):
        integer(now, "Zeit")
        with self._connection() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                if self._meta(db, "recovery_locked") == "1" and not allow_recovery:
                    raise Conflict("Wiederherstellung ist gesperrt; externer Abgleich fehlt")
                if now < int(self._meta(db, "clock")):
                    raise Conflict("Ruecklaeufige Steuerungszeit")
                self._set_meta(db, "clock", now)
                yield db
                db.commit()
            except BaseException:
                db.rollback()
                raise

    def _token(self, db):
        token = integer(int(self._meta(db, "fence")) + 1, "Berechtigungsnummer", 1)
        self._set_meta(db, "fence", token)
        return token

    @staticmethod
    def _audit(db, entity, key, revision, action, now, details):
        db.execute("INSERT INTO audit(entity, entity_id, revision, action, at, details) "
                   "VALUES (?, ?, ?, ?, ?, ?)",
                   (entity, key, revision, action, now, canonical(details)))

    @staticmethod
    def _row(db, table, key):
        column = "id" if table == "jobs" else "operation_id"
        if table not in {"jobs", "effects"}:
            raise Invalid("Interne Tabelle ungueltig")
        row = db.execute(f"SELECT * FROM {table} WHERE {column}=?", (key,)).fetchone()
        if row is None:
            raise Invalid("Unbekannter Auftrag/Vorgang")
        return dict(row)

    @staticmethod
    def _cas(row, revision):
        integer(revision, "Revision", 1)
        if row["revision"] != revision:
            raise Conflict("Veraltete Revision")

    def _job(self, db, key):
        row = self._row(db, "jobs", key)
        row["input_digests"] = parse_json(row["input_digests"])
        row["results"] = parse_json(row["results"])
        row["dependencies"] = [r[0] for r in db.execute(
            "SELECT dependency_id FROM dependencies WHERE job_id=? ORDER BY position", (key,))]
        row["artifacts"] = [dict(r) for r in db.execute(
            "SELECT digest,role FROM job_artifacts WHERE job_id=? ORDER BY digest,role", (key,))]
        row["epoch"] = self._meta(db, "epoch")
        return row

    def _save_job(self, db, row, now, action, **changes):
        changes["revision"] = row["revision"] + 1
        columns = ",".join(f"{key}=?" for key in changes)
        count = db.execute(f"UPDATE jobs SET {columns} WHERE id=? AND revision=?",
                           (*changes.values(), row["id"], row["revision"])).rowcount
        if count != 1:
            raise Conflict("Revision beim Schreiben verloren")
        self._audit(db, "job", row["id"], changes["revision"], action, now, changes)
        return self._job(db, row["id"])

    def _guard_job(self, db, row, lease, now):
        if not isinstance(lease, Lease) or lease.epoch != self._meta(db, "epoch"):
            raise Conflict("Fremde oder alte Lease-Epoche")
        integer(lease.token, "Berechtigungsnummer", 1)
        if (row["lease_owner"] != lease.owner or row["fencing_token"] != lease.token
                or row["lease_expires"] is None or row["lease_expires"] <= now):
            raise Conflict("Lease abgelaufen oder Worker ausgezaeunt")

    @staticmethod
    def _dependencies_done(db, key):
        pending = db.execute("SELECT d.dependency_id FROM dependencies d "
                             "JOIN jobs j ON j.id=d.dependency_id "
                             "WHERE d.job_id=? AND j.state!='done' ORDER BY d.position", (key,)).fetchall()
        if pending:
            raise Conflict("Offene Abhaengigkeiten: " + ", ".join(r[0] for r in pending))

    @staticmethod
    def _open_effects(db, key):
        return db.execute("SELECT * FROM effects WHERE job_id=? AND state!='confirmed' "
                          "ORDER BY operation_id", (key,)).fetchall()

    @staticmethod
    def _uncertain(db, key):
        return db.execute("SELECT 1 FROM effects WHERE job_id=? AND state!='confirmed' "
                          "AND (dispatch_count>0 OR uncertain=1) LIMIT 1", (key,)).fetchone() is not None

    def import_bootstrap(self, raw, expected_digest, *, now):
        data, source = bootstrap(raw)
        if digest(expected_digest) != source:
            raise Conflict("Startlistendigest stimmt nicht")
        with self._transaction(now) as db:
            prior = db.execute("SELECT digest FROM imports").fetchall()
            if prior:
                if len(prior) == 1 and prior[0][0] == source:
                    return {"digest": source, "count": len(data["auftraege"]), "imported": False}
                raise Conflict("Bestehende Startliste wird nicht ersetzt oder ergaenzt")
            if db.execute("SELECT 1 FROM jobs LIMIT 1").fetchone():
                raise Conflict("Import verlangt einen leeren Auftragsbestand")
            db.execute("INSERT INTO imports VALUES (?, ?, ?)", (source, raw, now))
            for task in data["auftraege"]:
                inputs = {"bootstrap": source, "definition": sha(canonical(task).encode("utf-8"))}
                db.execute("INSERT INTO jobs(id,revision,phase,title,state,input_digests) "
                           "VALUES (?,1,?,?,?,?)", (task["id"], data["phase"], task["titel"],
                                                    task["zustand"], canonical(inputs)))
                self._audit(db, "job", task["id"], 1, "import", now, task)
            for task in data["auftraege"]:
                db.executemany("INSERT INTO dependencies VALUES (?, ?, ?)",
                               [(task["id"], dep, index) for index, dep in enumerate(task["abhaengig"])])
            return {"digest": source, "count": len(data["auftraege"]), "imported": True}

    def show(self):
        with self._connection(readonly=True) as db:
            db.execute("BEGIN")
            return {"meta": dict(db.execute("SELECT key,value FROM meta")),
                    "jobs": [self._job(db, r[0]) for r in db.execute("SELECT id FROM jobs ORDER BY id")],
                    "effects": [self._effect(db, r[0]) for r in db.execute(
                        "SELECT operation_id FROM effects ORDER BY operation_id")]}

    def job(self, key):
        with self._connection(readonly=True) as db:
            db.execute("BEGIN")
            return self._job(db, identifier(key))

    def audit(self):
        with self._connection(readonly=True) as db:
            return [dict(r) for r in db.execute("SELECT * FROM audit ORDER BY sequence")]

    def claim(self, key, revision, *, owner, ttl, now):
        integer(now, "Zeit")
        identifier(owner, "Worker")
        integer(ttl, "Lease-Dauer", 1)
        expires = integer(now + ttl, "Lease-Ablauf", 1)
        with self._transaction(now) as db:
            row = self._row(db, "jobs", key)
            self._cas(row, revision)
            if row["state"] not in {"ready", "retry_wait", "reconciling"}:
                raise Conflict("Auftrag ist nicht uebernehmbar")
            if row["lease_owner"] is not None:
                raise Conflict("Lease zuerst explizit wiederherstellen")
            if now < row["next_check_at"]:
                raise Conflict("Naechster Pruefzeitpunkt noch nicht erreicht")
            self._dependencies_done(db, key)
            return self._save_job(db, row, now, "claim",
                                  state="reconciling" if row["state"] == "reconciling" else "leased",
                                  lease_owner=owner, lease_expires=expires,
                                  fencing_token=self._token(db), attempts=row["attempts"] + 1)

    def renew(self, key, revision, *, lease, ttl, now):
        integer(now, "Zeit")
        integer(ttl, "Lease-Dauer", 1)
        expires = integer(now + ttl, "Lease-Ablauf", 1)
        with self._transaction(now) as db:
            row = self._row(db, "jobs", key)
            self._cas(row, revision)
            self._guard_job(db, row, lease, now)
            return self._save_job(db, row, now, "renew",
                                  lease_expires=max(row["lease_expires"], expires))

    def transition(self, key, revision, state, *, now, lease=None, reason=None,
                   results=None, next_check_at=None):
        if not isinstance(state, str):
            raise Invalid("Zustand muss ein exakter Text sein")
        if isinstance(results, list):
            results = results.copy()
        with self._transaction(now) as db:
            row = self._row(db, "jobs", key)
            self._cas(row, revision)
            if state not in TRANSITIONS[row["state"]]:
                raise Invalid("Unzulaessiger Zustandsuebergang")
            if row["lease_owner"] is not None:
                self._guard_job(db, row, lease, now)
            elif lease is not None:
                raise Conflict("Keine aktive Lease")
            if state in {"running", "verifying", "done"} and row["lease_owner"] is None:
                raise Conflict("Aktiver Worker erforderlich")
            if state in {"ready", "running", "verifying", "done"}:
                self._dependencies_done(db, key)
            if state == "ready" and now < row["next_check_at"]:
                raise Conflict("Wartezeit laeuft")
            uncertain = self._uncertain(db, key)
            if state in {"planned", "ready", "running", "retry_wait", "superseded"} and uncertain:
                raise Conflict("Unbekannte Wirkung muss zuerst abgeglichen werden")
            if state in {"verifying", "done", "superseded"} and self._open_effects(db, key):
                raise Conflict("Offene Wirkungen sperren diesen Uebergang")
            if state == "reconciling" and not self._open_effects(db, key):
                raise Invalid("Kein offener Vorgang fuer Abgleich")
            changes = {"state": state, "blocked_reason": None}
            if state == "blocked":
                changes["blocked_reason"] = text(reason, "blocked-Grund")
            elif reason is not None and state != "superseded":
                raise Invalid("Grund ist nur bei blocked/superseded zulaessig")
            if state == "superseded":
                text(reason, "Abloesegrund")
            if state == "retry_wait":
                integer(next_check_at, "Naechster Pruefzeitpunkt")
                if next_check_at <= now:
                    raise Invalid("Wiederholungspruefung muss in der Zukunft liegen")
                changes["next_check_at"] = next_check_at
            elif next_check_at is not None:
                raise Invalid("Pruefzeit ist nur fuer retry_wait direkt setzbar")
            else:
                changes["next_check_at"] = now
            if state not in {"leased", "running", "verifying", "reconciling"}:
                changes.update(lease_owner=None, lease_expires=None)
            if state == "done":
                if not isinstance(results, list) or not results:
                    raise Invalid("Abschluss braucht eindeutige Ergebnisartefakte")
                for value in results:
                    digest(value)
                    if not db.execute("SELECT 1 FROM job_artifacts WHERE job_id=? AND digest=?",
                                      (key, value)).fetchone():
                        raise Invalid("Ergebnisartefakt gehoert nicht zum Auftrag")
                if len(results) != len(set(results)):
                    raise Invalid("Doppelte Ergebnisartefakte")
                changes["results"] = canonical(results)
            elif results is not None:
                raise Invalid("Ergebnisse nur bei done")
            result = self._save_job(db, row, now, "transition", **changes)
            if state == "superseded":
                self._audit(db, "job", key, result["revision"], "superseded_reason", now, {"reason": reason})
            return result

    def record_artifact(self, key, revision, data, *, role, lease, now):
        if not isinstance(data, bytes) or len(data) > 16 * 1024 * 1024:
            raise Invalid("Artefakt muss bytes sein, hoechstens 16 MiB")
        identifier(role, "Artefaktrolle")
        value = sha(data)
        with self._transaction(now) as db:
            row = self._row(db, "jobs", key)
            self._cas(row, revision)
            self._guard_job(db, row, lease, now)
            if row["state"] not in {"running", "verifying", "reconciling"}:
                raise Conflict("Artefakt in diesem Zustand nicht schreibbar")
            prior = db.execute("SELECT data FROM artifacts WHERE digest=?", (value,)).fetchone()
            if prior is not None and prior[0] != data:
                raise Conflict("Artefaktdigest kollidiert")
            db.execute("INSERT OR IGNORE INTO artifacts VALUES (?, ?, ?)", (value, data, len(data)))
            db.execute("INSERT OR IGNORE INTO job_artifacts VALUES (?, ?, ?)", (key, value, role))
            result = self._save_job(db, row, now, "artifact")
            self._audit(db, "job", key, result["revision"], "artifact_reference", now,
                        {"digest": value, "role": role})
            return result, value

    def artifact(self, value):
        digest(value)
        with self._connection(readonly=True) as db:
            row = db.execute("SELECT data FROM artifacts WHERE digest=?", (value,)).fetchone()
            if row is None or sha(row[0]) != value:
                raise Invalid("Artefakt fehlt oder ist beschaedigt")
            return row[0]

    def recover_expired(self, *, now, retry_delay=10):
        integer(now, "Zeit")
        integer(retry_delay, "Wiederanlaufpause", 1)
        integer(now + retry_delay, "Naechster Pruefzeitpunkt")
        changed = []
        with self._transaction(now) as db:
            rows = db.execute("SELECT * FROM jobs WHERE lease_expires<=? ORDER BY id", (now,)).fetchall()
            for raw in rows:
                row = dict(raw)
                state = "reconciling" if self._uncertain(db, row["id"]) else "retry_wait"
                changed.append(self._save_job(db, row, now, "lease_expired", state=state,
                                             lease_owner=None, lease_expires=None,
                                             next_check_at=now + retry_delay))
            # Ein Auftrag kann auch kontrolliert blockiert worden sein. Dann
            # darf dessen alter Wirkungsinhaber ebenfalls nichts bestaetigen.
            ops = db.execute("SELECT e.* FROM effects e JOIN jobs j ON j.id=e.job_id "
                             "WHERE e.lease_owner IS NOT NULL AND (e.lease_expires<=? "
                             "OR j.lease_owner IS NULL OR e.job_fencing_token!=j.fencing_token) "
                             "ORDER BY e.operation_id", (now,)).fetchall()
            for raw in ops:
                op = dict(raw)
                uncertain = op["uncertain"] or op["dispatch_count"] > 0
                self._save_effect(db, op, now, "lease_expired",
                                  state="unknown" if uncertain else "prepared",
                                  lease_owner=None, lease_expires=None,
                                  next_check_at=max(op["next_check_at"], now + retry_delay))
        return changed
