from concurrent.futures import ThreadPoolExecutor
import threading

from produkt.werkzeuge.steuerung import Conflict, Controller, Invalid, Lease
from produkt.werkzeuge.steuerung.recovery import file_digest
from support import StoreCase, arm, complete, observation, prepare, start_running


class RecoveryTests(StoreCase):
    def backup(self, name="backup.sqlite"):
        return self.controller.backup(self.folder / name)

    def restore(self, backup, name="restored.sqlite", floor=None, now=200):
        if floor is None:
            floor = backup["fencing_highwater"]
        return Controller.restore(backup["path"], self.folder / name, backup["digest"],
                                  fencing_floor=floor, now=now)

    def activate(self, restored, now=200, floor=None):
        snapshot = restored.show()
        restored.activate_local_recovery(snapshot["meta"]["epoch"],
                                         fencing_floor=int(snapshot["meta"]["fence"]) if floor is None else floor,
                                         source_retired=True, inventory_reconciled=True, now=now)

    def test_backup_restore_includes_jobs_artifact_bytes_and_open_effects(self):
        c = self.controller
        first = complete(c, start_running(c))
        c.transition("B", 1, "ready", now=100)
        job, op = prepare(c, start_running(c, key="B"))
        op = arm(c, job, op)
        op = c.begin_dispatch("op-1", op["revision"], lease=Lease.from_record(op), now=100)
        backup = self.backup()
        self.assertEqual((backup["jobs"], backup["artifacts"], backup["effects"], backup["open_effects"]),
                         (2, 2, 1, 1))
        restored = self.restore(backup)
        self.assertEqual(restored.job("A")["state"], "done")
        self.assertEqual(restored.job("A")["results"], first["results"])
        self.assertEqual(restored.artifact(first["results"][0]), b"synthetic result")
        self.assertEqual(restored.artifact(op["artifact_digest"]), b"synthetic archive")
        self.assertEqual(restored.job("B")["dependencies"], ["A"])
        self.assertEqual(restored.job("B")["input_digests"], job["input_digests"])
        self.assertEqual(restored.job("B")["state"], "reconciling")
        self.assertEqual(restored.effect("op-1")["request"], op["request"])
        self.assertEqual(restored.effect("op-1")["dispatch_count"], 1)
        self.assertEqual(restored.integrity()["open_effects"], 1)

    def test_restore_quarantine_prevents_split_brain_and_old_epoch(self):
        job = start_running(self.controller, ttl=10)
        old = Lease.from_record(job)
        backup = self.backup()
        self.controller.recover_expired(now=110, retry_delay=1)
        current = self.controller.job("A")
        current = self.controller.claim("A", current["revision"], owner=old.owner, ttl=10, now=111)
        highwater = current["fencing_token"]
        restored = self.restore(backup, floor=highwater)
        record = restored.job("A")
        self.assertEqual(restored.show()["meta"]["recovery_locked"], "1")
        with self.assertRaises(Conflict):
            restored.claim("A", record["revision"], owner=old.owner, ttl=10, now=200)
        with self.assertRaises(Invalid):
            restored.activate_local_recovery(record["epoch"], fencing_floor=highwater,
                                              source_retired=False, inventory_reconciled=True, now=200)
        self.activate(restored, floor=highwater)
        fresh = restored.claim("A", record["revision"], owner=old.owner, ttl=10, now=200)
        self.assertGreater(fresh["fencing_token"], highwater)
        self.assertNotEqual(fresh["epoch"], old.epoch)
        with self.assertRaises(Conflict):
            restored.transition("A", fresh["revision"], "running", lease=old, now=200)
        # Auch Kenntnis der neuen Nummer macht eine alte Epoche nicht gueltig.
        with self.assertRaises(Conflict):
            restored.transition("A", fresh["revision"], "running",
                                lease=Lease(old.epoch, old.owner, fresh["fencing_token"]), now=200)
        fresh = restored.transition("A", fresh["revision"], "running", lease=Lease.from_record(fresh), now=200)
        self.assertEqual(complete(restored, fresh, now=200)["state"], "done")

    def test_even_prepared_snapshot_is_uncertain_after_restore(self):
        job, _ = prepare(self.controller, start_running(self.controller))
        backup = self.backup()
        restored = self.restore(backup)
        self.activate(restored)
        job = restored.job("A")
        job = restored.claim("A", job["revision"], owner="restored-worker", ttl=100, now=200)
        op = restored.effect("op-1")
        self.assertEqual(op["uncertain"], 1)
        self.assertEqual(op["dispatch_count"], 0)
        op = restored.claim_effect("op-1", op["revision"], job_lease=Lease.from_record(job), ttl=50, now=200)
        lease = Lease.from_record(op)
        op = restored.observe_effect("op-1", op["revision"], observation(op, "absent"), lease=lease, now=200)
        self.assertEqual(op["state"], "unknown")
        with self.assertRaises(Conflict):
            restored.begin_dispatch("op-1", op["revision"], lease=lease, now=200)

    def test_restored_unknown_effect_can_be_found_without_resending(self):
        c = self.controller
        job, op = prepare(c, start_running(c))
        op = arm(c, job, op)
        c.begin_dispatch("op-1", op["revision"], lease=Lease.from_record(op), now=100)
        restored = self.restore(self.backup())
        self.activate(restored)
        job = restored.job("A")
        job = restored.claim("A", job["revision"], owner="restored-worker", ttl=100, now=200)
        op = restored.effect("op-1")
        op = restored.claim_effect("op-1", op["revision"], job_lease=Lease.from_record(job), ttl=50, now=200)
        op = restored.observe_effect("op-1", op["revision"], observation(op, "found"), lease=Lease.from_record(op), now=200)
        self.assertEqual(op["state"], "confirmed")
        self.assertEqual(op["dispatch_count"], 1)
        job = restored.transition("A", job["revision"], "verifying", lease=Lease.from_record(job), now=200)
        job, result = restored.record_artifact("A", job["revision"], b"recovered result", role="result",
                                               lease=Lease.from_record(job), now=200)
        self.assertEqual(restored.transition("A", job["revision"], "done", results=[result],
                                              lease=Lease.from_record(job), now=200)["state"], "done")

    def test_backup_is_consistent_during_real_concurrent_artifact_writes(self):
        c = self.controller
        job = start_running(c)
        barrier = threading.Barrier(2)

        def write_artifacts():
            current = job
            barrier.wait(timeout=10)
            for number in range(30):
                current, _ = c.record_artifact("A", current["revision"], f"artifact-{number}".encode(),
                                                role="result", lease=Lease.from_record(current), now=100)
            return current

        def snapshot():
            barrier.wait(timeout=10)
            return self.backup()

        with ThreadPoolExecutor(max_workers=2) as workers:
            writer, reader = workers.submit(write_artifacts), workers.submit(snapshot)
            final, backup = writer.result(30), reader.result(30)
        saved = Controller(backup["path"])
        counts = saved.integrity()
        self.assertLessEqual(counts["artifacts"], 30)
        self.assertEqual(saved.job("A")["revision"], job["revision"] + counts["artifacts"])
        self.assertEqual(final["revision"], job["revision"] + 30)
        self.assertEqual(c.integrity()["artifacts"], 30)
        self.assertEqual(file_digest(saved.path), backup["digest"])

    def test_restore_rejects_bad_digest_floor_clock_and_existing_target(self):
        start_running(self.controller)
        backup = self.backup()
        with self.assertRaises(Conflict):
            self.restore(backup, floor=0)
        with self.assertRaises(Conflict):
            self.restore(backup, now=99)
        wrong = {**backup, "digest": "0" * 64}
        with self.assertRaises(Conflict):
            self.restore(wrong)
        self.assertFalse((self.folder / "restored.sqlite").exists())
        restored = self.restore(backup)
        before = restored.show()
        with self.assertRaises(Conflict):
            self.restore(backup)
        self.assertEqual(restored.show(), before)
        with self.assertRaises(Conflict):
            self.backup()

    def test_hash_verified_restore_still_checks_artifact_integrity(self):
        job = start_running(self.controller)
        self.controller.record_artifact("A", job["revision"], b"synthetic", role="result",
                                         lease=Lease.from_record(job), now=100)
        backup = self.backup()
        saved = Controller(backup["path"])
        # Nur synthetische Sicherung: Konsistenzverletzung bei weiterhin gueltiger SQL-Struktur.
        with saved._connection() as db:
            db.execute("UPDATE artifacts SET data=?", (b"corrupted",))
        backup["digest"] = file_digest(saved.path)
        with self.assertRaises(Invalid):
            self.restore(backup)
        self.assertFalse((self.folder / "restored.sqlite").exists())

    def test_backup_does_not_mutate_live_jobs_or_audit(self):
        start_running(self.controller)
        before = self.controller.show()
        audit = self.controller.audit()
        backup = self.backup()
        self.assertEqual(self.controller.show(), before)
        self.assertEqual(self.controller.audit(), audit)
        self.assertEqual(Controller(backup["path"]).show(), before)
        self.assertFalse(any(path.name.endswith(("-wal", "-shm")) for path in self.folder.iterdir()
                             if path.name.startswith("backup")))
