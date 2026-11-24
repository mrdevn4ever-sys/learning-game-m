"""Wirkungsjournal ohne Netzwerk-, Merge- oder Uploadadapter.

begin_dispatch speichert nur eine Absicht. Ein spaeterer Dienst muss seine
externen Schreibrechte selbst an Lease, Epoche und Operations-ID binden.
"""

import re
import sqlite3

from .contracts import (Conflict, Invalid, Lease, canonical, digest, fields,
                        identifier, integer, parse_json, sha, text)


class Effects:
    def _effect(self, db, key):
        row = self._row(db, "effects", key)
        row["request"] = parse_json(row["request"])
        if row["observation"] is not None:
            row["observation"] = parse_json(row["observation"])
        row["epoch"] = self._meta(db, "epoch")
        return row

    def effect(self, key):
        with self._connection(readonly=True) as db:
            db.execute("BEGIN")
            return self._effect(db, identifier(key, "Operations-ID"))

    def _save_effect(self, db, row, now, action, **changes):
        changes["revision"] = row["revision"] + 1
        columns = ",".join(f"{key}=?" for key in changes)
        count = db.execute(f"UPDATE effects SET {columns} WHERE operation_id=? AND revision=?",
                           (*changes.values(), row["operation_id"], row["revision"])).rowcount
        if count != 1:
            raise Conflict("Veraltete Wirkungsrevision")
        self._audit(db, "effect", row["operation_id"], changes["revision"], action, now, changes)
        return self._effect(db, row["operation_id"])

    @staticmethod
    def _target(kind, target):
        if kind == "upload":
            fields(target, {"app_id", "version", "build_number"})
            for name in target:
                text(target[name], name)
            if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){0,2}", target["build_number"]):
                raise Invalid("Buildnummer hat kein gueltiges exaktes Format")
        elif kind == "merge":
            fields(target, {"repository", "branch", "commit"})
            for name in target:
                text(target[name], name)
            if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", target["commit"]):
                raise Invalid("Merge braucht einen exakten Commitdigest")
        else:
            raise Invalid("Nur merge/upload werden journalisiert")

    def prepare_effect(self, key, revision, operation_id, kind, candidate_digest,
                       artifact_digest, target, *, lease, now):
        identifier(operation_id, "Operations-ID")
        digest(candidate_digest, "Kandidatendigest")
        digest(artifact_digest, "Archivdigest")
        target = parse_json(canonical(target))
        self._target(kind, target)
        request = {"kind": kind, "candidate_digest": candidate_digest,
                   "artifact_digest": artifact_digest, "target": target}
        raw = canonical(request)
        with self._transaction(now) as db:
            job = self._row(db, "jobs", key)
            self._cas(job, revision)
            self._guard_job(db, job, lease, now)
            if job["state"] != "running":
                raise Conflict("Neue Wirkungsabsicht nur im laufenden Auftrag")
            if not db.execute("SELECT 1 FROM job_artifacts WHERE job_id=? AND digest=?",
                              (key, artifact_digest)).fetchone():
                raise Invalid("Archiv ist nicht als Auftragsartefakt gespeichert")
            old = db.execute("SELECT * FROM effects WHERE operation_id=?", (operation_id,)).fetchone()
            if old is not None:
                if old["job_id"] != key or old["request"] != raw:
                    raise Conflict("Operations-ID wurde mit anderem Inhalt verwendet")
                return {"job": self._job(db, key), "effect": self._effect(db, operation_id)}
            try:
                db.execute("INSERT INTO effects(operation_id,job_id,kind,revision,state,request,"
                           "request_digest,target_key,candidate_digest,artifact_digest) "
                           "VALUES (?,?,?,1,'prepared',?,?,?,?,?)",
                           (operation_id, key, kind, raw, sha(raw.encode("utf-8")),
                            canonical(target), candidate_digest, artifact_digest))
            except sqlite3.IntegrityError as exc:
                raise Conflict("Ziel/Buildnummer besitzt bereits eine Operations-ID") from exc
            self._audit(db, "effect", operation_id, 1, "prepare", now, request)
            job = self._save_job(db, job, now, "effect_prepared")
            return {"job": job, "effect": self._effect(db, operation_id)}

    def claim_effect(self, operation_id, revision, *, job_lease, ttl, now):
        integer(now, "Zeit")
        integer(ttl, "Wirkungslease-Dauer", 1)
        integer(now + ttl, "Wirkungslease-Ablauf", 1)
        with self._transaction(now) as db:
            op = self._row(db, "effects", operation_id)
            self._cas(op, revision)
            job = self._row(db, "jobs", op["job_id"])
            self._guard_job(db, job, job_lease, now)
            if job["state"] not in {"running", "reconciling"}:
                raise Conflict("Auftrag laeuft nicht oder gleicht nicht ab")
            if op["state"] == "confirmed" or now < op["next_check_at"]:
                raise Conflict("Vorgang bestaetigt oder noch nicht zur Pruefung faellig")
            if (op["lease_owner"] is not None and op["lease_expires"] > now
                    and op["job_fencing_token"] == job["fencing_token"]):
                raise Conflict("Wirkung ist bereits exklusiv vergeben")
            return self._save_effect(db, op, now, "claim", state="checking",
                                     lease_owner=job_lease.owner,
                                     lease_expires=min(job["lease_expires"], now + ttl),
                                     fencing_token=self._token(db),
                                     job_fencing_token=job["fencing_token"],
                                     attempts=op["attempts"] + 1)

    def _guard_effect(self, db, op, lease, now):
        if (not isinstance(lease, Lease) or lease.epoch != self._meta(db, "epoch")
                or lease.job_token == 0):
            raise Conflict("Fremde, alte oder nicht wirkungsgebundene Lease")
        integer(lease.token, "Wirkungsberechtigung", 1)
        integer(lease.job_token, "Auftragsberechtigung", 1)
        if (op["lease_owner"] != lease.owner or op["fencing_token"] != lease.token
                or op["job_fencing_token"] != lease.job_token or op["lease_expires"] is None
                or op["lease_expires"] <= now):
            raise Conflict("Wirkungslease abgelaufen oder ausgezaeunt")
        job = self._row(db, "jobs", op["job_id"])
        self._guard_job(db, job, Lease(lease.epoch, lease.owner, lease.job_token), now)
        if job["state"] not in {"running", "reconciling"}:
            raise Conflict("Auftrag erlaubt keine Wirkung")
        return job

    @staticmethod
    def _observation(op, observation):
        fields(observation, {"outcome", "operation_id", "request_digest", "candidate_digest",
                             "artifact_digest", "target"}, {"external_id", "reason"})
        request = parse_json(op["request"])
        for name in ("operation_id", "request_digest", "candidate_digest", "artifact_digest"):
            if observation[name] != op[name]:
                raise Conflict("Abgleich gehoert zu anderem Vorgang/Kandidaten/Archiv")
        for name in ("request_digest", "candidate_digest", "artifact_digest"):
            digest(observation[name], name)
        if canonical(observation["target"]) != canonical(request["target"]):
            raise Conflict("Abgleich gehoert zu anderer Buildnummer oder anderem Mergeziel")
        if (not isinstance(observation["outcome"], str)
                or observation["outcome"] not in {"found", "absent", "unknown"}):
            raise Invalid("Unbekanntes Abgleichergebnis")
        if observation["outcome"] == "found":
            text(observation.get("external_id"), "Externe Vorgangs-ID")
        elif "external_id" in observation:
            raise Invalid("Keine externe ID ohne bestaetigten Fund")
        if observation["outcome"] == "unknown":
            text(observation.get("reason"), "Ausstehender Abgleichgrund")

    def observe_effect(self, operation_id, revision, observation, *, lease, now):
        """Gebundene Lesebeobachtung; kein behaupteter authentisierter Beleg."""
        observation = parse_json(canonical(observation))
        with self._transaction(now) as db:
            op = self._row(db, "effects", operation_id)
            self._cas(op, revision)
            self._guard_effect(db, op, lease, now)
            if op["state"] not in {"checking", "unknown"}:
                raise Conflict("Kein beanspruchter Abgleich offen")
            self._observation(op, observation)
            outcome = observation["outcome"]
            changes = {"observation": canonical(observation)}
            if outcome == "found":
                changes.update(state="confirmed", lease_owner=None, lease_expires=None,
                               next_check_at=now)
            elif outcome == "absent" and op["dispatch_count"] == 0 and not op["uncertain"]:
                changes.update(state="armed", next_check_at=now)
            else:
                delay = min(3600, 5 * 2 ** min(op["attempts"], 10))
                changes.update(state="unknown", lease_owner=None, lease_expires=None,
                               next_check_at=integer(now + delay, "Naechster Abgleich"))
            return self._save_effect(db, op, now, "observe", **changes)

    def begin_dispatch(self, operation_id, revision, *, lease, now):
        """Vorabspeicherung unmittelbar VOR einer lokalen simulierten Wirkung.

        Nach dieser Transaktion gibt es absichtlich keinen Wiederholungsweg.
        Auch ein spaeteres 'absent' ist wegen moeglicher Verzoegerung kein
        Beweis, dass eine bereits begonnene Wirkung nie stattfand.
        """
        with self._transaction(now) as db:
            op = self._row(db, "effects", operation_id)
            self._cas(op, revision)
            job = self._guard_effect(db, op, lease, now)
            if (op["state"] != "armed" or op["dispatch_count"] != 0 or op["uncertain"]
                    or job["state"] != "running"):
                raise Conflict("Kein sicherer erster Wirkungsversuch erlaubt")
            return self._save_effect(db, op, now, "dispatch_intent", state="unknown",
                                     dispatch_count=1, uncertain=1, next_check_at=now)
