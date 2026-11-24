"""Ein-Datei-Sicherung, Integritaetspruefung und gesperrter Restore."""

import hashlib
import os
import sqlite3
import uuid

from .contracts import (Conflict, Invalid, bootstrap, canonical, digest, integer,
                        parse_json, runtime_path, sha)


def file_digest(path):
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def publish(stage, destination):
    """Atomar ohne Ueberschreiben. Beide Dateien liegen auf demselben Volume."""
    try:
        os.link(stage, destination)
    except FileExistsError as exc:
        raise Conflict("Zieldatei existiert bereits") from exc
    stage.unlink()


class Recovery:
    def integrity(self):
        with self._connection(readonly=True) as db:
            db.execute("BEGIN")
            if [r[0] for r in db.execute("PRAGMA integrity_check")] != ["ok"]:
                raise Invalid("SQLite-Integritaetspruefung fehlgeschlagen")
            if db.execute("PRAGMA foreign_key_check").fetchall():
                raise Invalid("Defekte Fremdschluessel")
            fence = integer(int(self._meta(db, "fence")), "Gespeicherte Berechtigung")
            integer(int(self._meta(db, "clock")), "Gespeicherte Zeit")
            if self._meta(db, "recovery_locked") not in {"0", "1"}:
                raise Invalid("Ungueltige Wiederherstellungssperre")
            imports = db.execute("SELECT * FROM imports").fetchall()
            ids = set()
            if len(imports) > 1:
                raise Invalid("Mehrere Startlisten")
            for source in imports:
                data, value = bootstrap(source["raw"])
                if value != source["digest"]:
                    raise Invalid("Startliste beschaedigt")
                for original in data["auftraege"]:
                    row = self._job(db, original["id"])
                    ids.add(original["id"])
                    expected = {"bootstrap": value, "definition": sha(canonical(original).encode("utf-8"))}
                    if (row["phase"] != data["phase"] or row["title"] != original["titel"]
                            or row["dependencies"] != original["abhaengig"]
                            or row["input_digests"] != expected):
                        raise Invalid("Originaler Auftrag oder Abhaengigkeiten wurden umgeschrieben")
                    if row["fencing_token"] > fence:
                        raise Invalid("Auftragsberechtigung ueber High-Water-Mark")
                    if row["state"] == "done":
                        if not row["results"] or self._open_effects(db, row["id"]):
                            raise Invalid("Abschluss ohne Ergebnis oder mit offener Wirkung")
                        self._dependencies_done(db, row["id"])
                    for result in row["results"]:
                        digest(result)
                        if not db.execute("SELECT 1 FROM job_artifacts WHERE job_id=? AND digest=?",
                                          (row["id"], result)).fetchone():
                            raise Invalid("Ergebnisverweis ohne Artefakt")
            if ids != {r[0] for r in db.execute("SELECT id FROM jobs")}:
                raise Invalid("Auftragsbestand weicht von Startliste ab")
            for artifact in db.execute("SELECT * FROM artifacts"):
                if sha(artifact["data"]) != artifact["digest"] or len(artifact["data"]) != artifact["size"]:
                    raise Invalid("Artefaktbytes stimmen nicht mit Digest ueberein")
            for effect in db.execute("SELECT * FROM effects"):
                request = parse_json(effect["request"])
                self._target(effect["kind"], request["target"])
                digest(effect["candidate_digest"])
                digest(effect["artifact_digest"])
                if (sha(effect["request"].encode("utf-8")) != effect["request_digest"]
                        or effect["request"] != canonical(request)
                        or request != {"kind": effect["kind"], "target": parse_json(effect["target_key"]),
                                       "candidate_digest": effect["candidate_digest"],
                                       "artifact_digest": effect["artifact_digest"]}
                        or effect["fencing_token"] > fence or effect["job_fencing_token"] > fence):
                    raise Invalid("Wirkungsbindung ist beschaedigt")
                if not db.execute("SELECT 1 FROM job_artifacts WHERE job_id=? AND digest=?",
                                  (effect["job_id"], effect["artifact_digest"])).fetchone():
                    raise Invalid("Wirkungsarchiv gehoert nicht zum Auftrag")
                if effect["observation"] is not None:
                    self._observation(effect, parse_json(effect["observation"]))
                if effect["state"] == "confirmed" and (effect["observation"] is None or
                        parse_json(effect["observation"])["outcome"] != "found"):
                    raise Invalid("Bestaetigte Wirkung ohne gebundene Fundbeobachtung")
            for table, key, entity in (("jobs", "id", "job"), ("effects", "operation_id", "effect")):
                for row in db.execute(f"SELECT {key}, revision FROM {table}"):
                    latest = db.execute("SELECT max(revision) FROM audit WHERE entity=? AND entity_id=?",
                                        (entity, row[0])).fetchone()[0]
                    if latest != row[1]:
                        raise Invalid("Revision ohne Auditspur")
            return {"jobs": db.execute("SELECT count(*) FROM jobs").fetchone()[0],
                    "artifacts": db.execute("SELECT count(*) FROM artifacts").fetchone()[0],
                    "effects": db.execute("SELECT count(*) FROM effects").fetchone()[0],
                    "open_effects": db.execute("SELECT count(*) FROM effects WHERE state!='confirmed'").fetchone()[0],
                    "fencing_highwater": fence, "integrity": "ok"}

    def backup(self, destination):
        destination = runtime_path(destination)
        if destination.exists():
            raise Conflict("Sicherung ueberschreibt keine Datei")
        destination.parent.mkdir(parents=True, exist_ok=True)
        stage = destination.with_name(".backup-" + uuid.uuid4().hex + ".sqlite")
        try:
            with stage.open("xb"):
                pass
            target = sqlite3.connect(stage, isolation_level=None)
            try:
                target.execute("PRAGMA synchronous=FULL")
                with self._connection(readonly=True) as source:
                    source.backup(target)
                # Die Sicherung ist eine abgeschlossene Datei, kein WAL-Buendel.
                target.execute("PRAGMA journal_mode=DELETE")
            finally:
                target.close()
            counts = type(self)(stage).integrity()
            value = file_digest(stage)
            publish(stage, destination)
            return {"path": str(destination), "digest": value, **counts}
        finally:
            stage.unlink(missing_ok=True)

    @classmethod
    def restore(cls, source, destination, expected_digest, *, fencing_floor, now):
        """Niemals inplace. Unbestaetigte Wirkungen bleiben zwingend unbekannt."""
        source = runtime_path(source)
        destination = runtime_path(destination)
        digest(expected_digest, "Sicherungsdigest")
        integer(fencing_floor, "Externe Berechtigungsuntergrenze")
        integer(now, "Wiederherstellungszeit")
        if destination.exists():
            raise Conflict("Restore ueberschreibt keinen Bestand")
        destination.parent.mkdir(parents=True, exist_ok=True)
        stage = destination.with_name(".restore-" + uuid.uuid4().hex + ".sqlite")
        try:
            value = hashlib.sha256()
            with source.open("rb") as reader, stage.open("xb") as writer:
                for chunk in iter(lambda: reader.read(1024 * 1024), b""):
                    writer.write(chunk)
                    value.update(chunk)
                writer.flush()
                os.fsync(writer.fileno())
            if value.hexdigest() != expected_digest:
                raise Conflict("Sicherung entspricht nicht dem erwarteten Digest")
            restored = cls(stage)
            counts = restored.integrity()
            if fencing_floor < counts["fencing_highwater"]:
                raise Conflict("Berechtigungsuntergrenze ist kleiner als die Sicherung")
            with restored._transaction(now, allow_recovery=True) as db:
                old_epoch = restored._meta(db, "epoch")
                restored._set_meta(db, "epoch", uuid.uuid4().hex)
                restored._set_meta(db, "fence", fencing_floor)
                restored._set_meta(db, "recovery_locked", "1")
                for raw in db.execute("SELECT * FROM effects ORDER BY operation_id").fetchall():
                    op = dict(raw)
                    changes = {"lease_owner": None, "lease_expires": None, "next_check_at": now}
                    if op["state"] != "confirmed":
                        changes.update(state="unknown", uncertain=1)
                    restored._save_effect(db, op, now, "restore", **changes)
                for raw in db.execute("SELECT * FROM jobs ORDER BY id").fetchall():
                    job = dict(raw)
                    state = job["state"]
                    if state not in {"blocked", "done", "superseded"}:
                        if restored._open_effects(db, job["id"]):
                            state = "reconciling"
                        elif job["lease_owner"] is not None:
                            state = "retry_wait"
                    restored._save_job(db, job, now, "restore", state=state,
                                       lease_owner=None, lease_expires=None, next_check_at=now)
                restored._audit(db, "store", "restore", 1, "quarantine", now,
                                {"source_digest": expected_digest, "source_epoch": old_epoch,
                                 "fencing_floor": fencing_floor})
            restored.integrity()
            # Kein WAL bleibt hinter dem atomar veroeffentlichten Namen zurueck.
            with restored._connection() as db:
                db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                db.execute("PRAGMA journal_mode=DELETE")
            publish(stage, destination)
            return cls(destination)
        finally:
            stage.unlink(missing_ok=True)

    def activate_local_recovery(self, expected_epoch, *, fencing_floor, source_retired,
                                inventory_reconciled, now):
        """Nur Betriebsprobe. Keine authentisierte Produktionsfreigabe.

        Bei echter Wirkung sind ein separater Fencing-Dienst, Stilllegung der
        Quelle und ein vollstaendiger externer Abgleich Voraussetzung. Diese
        lokale API kann das nicht beweisen; die CLI bietet keine Aktivierung.
        """
        if source_retired is not True or inventory_reconciled is not True:
            raise Invalid("Quellstilllegung und vollstaendiger Abgleich sind erforderlich")
        integer(fencing_floor, "Berechtigungsuntergrenze")
        with self._transaction(now, allow_recovery=True) as db:
            if self._meta(db, "recovery_locked") != "1" or self._meta(db, "epoch") != expected_epoch:
                raise Conflict("Nicht die erwartete gesperrte Wiederherstellung")
            if fencing_floor < int(self._meta(db, "fence")):
                raise Conflict("Berechtigungsuntergrenze darf nie fallen")
            self._set_meta(db, "fence", fencing_floor)
            self._set_meta(db, "recovery_locked", "0")
            self._audit(db, "store", "restore", 2, "local_simulation_only", now,
                        {"fencing_floor": fencing_floor, "source_retired": True,
                         "inventory_reconciled": True, "release_authorized": False})
        return self.show()
