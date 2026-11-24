"""Oeffentliche R-01-Regressionen: Fristerhalt ist keine Wirkungsfreigabe."""

from produkt.werkzeuge.steuerung import Conflict, Controller, Lease
from produkt.werkzeuge.steuerung.contracts import parse_json, sha
from produkt.werkzeuge.steuerung.recovery import file_digest
from support import StoreCase, arm, complete, observation, prepare, start_running


class RestoreDeadlineTests(StoreCase):
    def assert_rejected_unchanged(self, controller, action):
        before = controller.show(), controller.audit()
        with self.assertRaises(Conflict):
            action()
        self.assertEqual((controller.show(), controller.audit()), before)

    def restore_copy(self, source, now, name="restored"):
        before = source.show(), source.audit()
        backup = source.backup(self.folder / (name + "-backup.sqlite"))
        # Simuliert einen unabhaengig gelieferten, hoeheren Fencing-Stand.
        floor = backup["fencing_highwater"] + 20
        restored = Controller.restore(backup["path"], self.folder / (name + ".sqlite"),
                                      backup["digest"], fencing_floor=floor, now=now)
        self.assertEqual((source.show(), source.audit()), before)
        self.assertEqual(file_digest(Controller(backup["path"]).path), backup["digest"])
        self.assertEqual(restored.integrity()["integrity"], "ok")
        meta = restored.show()["meta"]
        self.assertEqual(meta["recovery_locked"], "1")
        self.assertEqual(int(meta["fence"]), floor)
        self.assertNotEqual(meta["epoch"], before[0]["meta"]["epoch"])
        # Audit und Daten muessen dieselbe pro Datensatz bewahrte Frist tragen.
        for entity, records, key in (("job", before[0]["jobs"], "id"),
                                     ("effect", before[0]["effects"], "operation_id")):
            for saved in records:
                row = (restored.job if entity == "job" else restored.effect)(saved[key])
                self.assertEqual(row["next_check_at"], max(saved["next_check_at"], now))
                self.assertEqual(row["attempts"], saved["attempts"])
                self.assertEqual(row["revision"], saved["revision"] + 1)
                self.assertIsNone(row["lease_owner"])
                self.assertIsNone(row["lease_expires"])
                audit = [entry for entry in restored.audit()
                         if entry["entity"] == entity and entry["entity_id"] == saved[key]
                         and entry["revision"] == row["revision"] and entry["action"] == "restore"]
                self.assertEqual(len(audit), 1)
                self.assertEqual(parse_json(audit[0]["details"])["next_check_at"], row["next_check_at"])
        return restored

    def activate_local(self, restored, now):
        meta = restored.show()["meta"]
        # Nur synthetische Aktivierung, kein Nachweis echter Quellstilllegung.
        restored.activate_local_recovery(meta["epoch"], fencing_floor=int(meta["fence"]),
                                         source_retired=True, inventory_reconciled=True, now=now)
        self.assertEqual(restored.show()["meta"]["recovery_locked"], "0")
        self.assertFalse(parse_json(restored.audit()[-1]["details"])["release_authorized"])

    def retry_snapshot(self, deadline=1000):
        job = start_running(self.controller)
        old = Lease.from_record(job)
        retry = self.controller.transition("A", job["revision"], "retry_wait", now=100,
                                           next_check_at=deadline, lease=old)
        return retry, old

    def effect_snapshot(self, dispatched=True, ttl=1000):
        job, op = prepare(self.controller, start_running(self.controller, ttl=ttl))
        if dispatched:
            op = arm(self.controller, job, op, ttl=ttl)
        else:
            op = self.controller.claim_effect("op-1", op["revision"],
                                              job_lease=Lease.from_record(job), ttl=ttl, now=100)
        old_effect = Lease.from_record(op)
        if dispatched:
            op = self.controller.begin_dispatch("op-1", op["revision"], lease=old_effect, now=100)
        op = self.controller.observe_effect("op-1", op["revision"], observation(op, "unknown"),
                                            lease=old_effect, now=100)
        self.assertEqual(op["next_check_at"], 110)
        return job, op, old_effect

    def claim_job(self, restored, now):
        job = restored.job("A")
        floor = int(restored.show()["meta"]["fence"])
        fresh = restored.claim("A", job["revision"], owner="restored-worker", ttl=1000, now=now)
        self.assertGreater(fresh["fencing_token"], floor)
        self.assertEqual(fresh["attempts"], job["attempts"] + 1)
        return fresh

    def claim_effect(self, restored, job, now):
        op = restored.effect("op-1")
        floor = int(restored.show()["meta"]["fence"])
        fresh = restored.claim_effect("op-1", op["revision"], job_lease=Lease.from_record(job),
                                      ttl=100, now=now)
        self.assertGreater(fresh["fencing_token"], floor)
        self.assertEqual(fresh["attempts"], op["attempts"] + 1)
        self.assertEqual((fresh["state"], fresh["uncertain"]), ("checking", 1))
        self.assertEqual(fresh["dispatch_count"], op["dispatch_count"])
        # Auch ein fristgerechter, frisch gefenceter Claim ist kein Dispatchrecht.
        self.assert_rejected_unchanged(restored, lambda: restored.begin_dispatch(
            "op-1", fresh["revision"], lease=Lease.from_record(fresh), now=now))
        return fresh

    def test_future_retry_deadline_blocks_claim_and_ready_after_activation(self):
        saved, _ = self.retry_snapshot()
        restored = self.restore_copy(self.controller, 105)
        self.activate_local(restored, 105)
        restored = Controller(restored.path)
        row = restored.job("A")
        self.assertEqual((row["state"], row["next_check_at"]), ("retry_wait", 1000))
        for now in (105, 999):
            with self.subTest(now=now):
                self.assert_rejected_unchanged(restored, lambda: restored.claim(
                    "A", row["revision"], owner="restored-worker", ttl=10, now=now))
                self.assert_rejected_unchanged(restored, lambda: restored.transition(
                    "A", row["revision"], "ready", now=now))
        self.assertEqual(restored.job("A")["attempts"], saved["attempts"])

    def test_future_retry_is_claimable_exactly_at_deadline_not_permanently_blocked(self):
        _, old = self.retry_snapshot()
        restored = self.restore_copy(self.controller, 105)
        self.activate_local(restored, 105)
        fresh = self.claim_job(restored, 1000)
        self.assertEqual(fresh["state"], "leased")
        self.assert_rejected_unchanged(restored, lambda: restored.transition(
            "A", fresh["revision"], "running", lease=old, now=1000))
        fresh = restored.transition("A", fresh["revision"], "running",
                                    lease=Lease.from_record(fresh), now=1000)
        self.assertEqual(complete(restored, fresh, now=1000)["state"], "done")

    def test_retry_restore_equal_to_deadline_is_due(self):
        self.retry_snapshot(deadline=120)
        restored = self.restore_copy(self.controller, 120)
        self.activate_local(restored, 120)
        self.assertEqual(restored.job("A")["next_check_at"], 120)
        self.assertEqual(self.claim_job(restored, 120)["state"], "leased")

    def test_retry_restore_after_deadline_uses_restore_time_without_extra_delay(self):
        self.retry_snapshot(deadline=120)
        restored = self.restore_copy(self.controller, 121)
        self.activate_local(restored, 121)
        self.assertEqual(restored.job("A")["next_check_at"], 121)
        self.assertEqual(self.claim_job(restored, 121)["state"], "leased")

    def test_future_effect_deadline_blocks_claim_with_valid_parent_lease(self):
        self.effect_snapshot()
        restored = self.restore_copy(self.controller, 101)
        self.activate_local(restored, 101)
        restored = Controller(restored.path)
        fresh = self.claim_job(restored, 101)
        op = restored.effect("op-1")
        self.assertEqual((op["next_check_at"], op["dispatch_count"], op["uncertain"]), (110, 1, 1))
        for now in (101, 109):
            with self.subTest(now=now):
                self.assert_rejected_unchanged(restored, lambda: restored.claim_effect(
                    "op-1", op["revision"], job_lease=Lease.from_record(fresh), ttl=10, now=now))

    def test_future_effect_is_found_at_deadline_without_resending(self):
        old_job, saved, old_effect = self.effect_snapshot()
        restored = self.restore_copy(self.controller, 101)
        self.activate_local(restored, 101)
        fresh = self.claim_job(restored, 101)
        op = self.claim_effect(restored, fresh, 110)
        self.assert_rejected_unchanged(restored, lambda: restored.renew(
            "A", fresh["revision"], lease=Lease.from_record(old_job), ttl=1000, now=110))
        self.assert_rejected_unchanged(restored, lambda: restored.observe_effect(
            "op-1", op["revision"], observation(op, "found"), lease=old_effect, now=110))
        self.assertEqual(op["request_digest"], saved["request_digest"])
        op = restored.observe_effect("op-1", op["revision"], observation(op, "found"),
                                     lease=Lease.from_record(op), now=110)
        self.assertEqual((op["state"], op["dispatch_count"]), ("confirmed", 1))
        self.assertEqual(complete(restored, fresh, now=110)["state"], "done")
        self.assertEqual(restored.integrity()["open_effects"], 0)

    def test_effect_restore_equal_to_deadline_is_due(self):
        self.effect_snapshot()
        restored = self.restore_copy(self.controller, 110)
        self.activate_local(restored, 110)
        fresh = self.claim_job(restored, 110)
        self.assertEqual(self.claim_effect(restored, fresh, 110)["next_check_at"], 110)

    def test_effect_restore_after_deadline_uses_restore_time_without_extra_delay(self):
        self.effect_snapshot()
        restored = self.restore_copy(self.controller, 111)
        self.activate_local(restored, 111)
        fresh = self.claim_job(restored, 111)
        self.assertEqual(self.claim_effect(restored, fresh, 111)["next_check_at"], 111)

    def test_repeated_restores_keep_both_deadlines_attempts_and_uncertainty(self):
        _, saved, _ = self.effect_snapshot(ttl=1)
        rows = self.controller.recover_expired(now=101, retry_delay=49)
        self.assertEqual((rows[0]["state"], rows[0]["next_check_at"]), ("reconciling", 150))
        first = self.restore_copy(self.controller, 102, "first")
        self.activate_local(first, 102)
        restored = self.restore_copy(Controller(first.path), 109, "second")
        self.activate_local(restored, 109)
        job, op = restored.job("A"), restored.effect("op-1")
        self.assertEqual((job["next_check_at"], op["next_check_at"]), (150, 110))
        self.assertEqual((op["attempts"], op["dispatch_count"], op["uncertain"]),
                         (saved["attempts"], 1, 1))
        self.assert_rejected_unchanged(restored, lambda: restored.claim(
            "A", job["revision"], owner="restored-worker", ttl=1000, now=149))
        fresh = self.claim_job(restored, 150)
        op = self.claim_effect(restored, fresh, 150)
        op = restored.observe_effect("op-1", op["revision"], observation(op, "unknown"),
                                     lease=Lease.from_record(op), now=150)
        # Zweiter Abgleich: Backoff waechst weiter, kein Reset der Versuchszahl.
        self.assertEqual((op["attempts"], op["next_check_at"]), (2, 170))

    def test_job_and_effect_deadlines_are_separate_after_restore(self):
        self.effect_snapshot(ttl=1)
        self.controller.recover_expired(now=101, retry_delay=4)
        restored = self.restore_copy(self.controller, 102)
        self.activate_local(restored, 102)
        job, op = restored.job("A"), restored.effect("op-1")
        self.assertEqual((job["next_check_at"], op["next_check_at"]), (105, 110))
        self.assert_rejected_unchanged(restored, lambda: restored.claim(
            "A", job["revision"], owner="restored-worker", ttl=1000, now=104))
        fresh = self.claim_job(restored, 105)
        self.assert_rejected_unchanged(restored, lambda: restored.claim_effect(
            "op-1", op["revision"], job_lease=Lease.from_record(fresh), ttl=10, now=109))
        self.claim_effect(restored, fresh, 110)

    def test_due_deadlines_do_not_bypass_quarantine_or_old_epoch(self):
        job, _, old_effect = self.effect_snapshot()
        restored = self.restore_copy(self.controller, 110)
        row, op = restored.job("A"), restored.effect("op-1")
        self.assert_rejected_unchanged(restored, lambda: restored.claim(
            "A", row["revision"], owner="restored-worker", ttl=1000, now=110))
        self.assert_rejected_unchanged(restored, lambda: restored.claim_effect(
            "op-1", op["revision"], job_lease=Lease.from_record(job), ttl=10, now=110))
        self.activate_local(restored, 110)
        fresh = self.claim_job(restored, 110)
        op = self.claim_effect(restored, fresh, 110)
        forged_epoch = Lease(job["epoch"], fresh["lease_owner"], fresh["fencing_token"])
        self.assert_rejected_unchanged(restored, lambda: restored.renew(
            "A", fresh["revision"], lease=forged_epoch, ttl=1000, now=110))
        forged_effect = Lease(old_effect.epoch, op["lease_owner"], op["fencing_token"],
                              op["job_fencing_token"])
        self.assert_rejected_unchanged(restored, lambda: restored.observe_effect(
            "op-1", op["revision"], observation(op, "found"), lease=forged_effect, now=110))

    def test_absent_after_due_restore_remains_unknown_before_and_after_dispatch(self):
        for dispatched in (False, True):
            with self.subTest(dispatched=dispatched):
                if dispatched:
                    self.controller = Controller.create(self.folder / "second-source.sqlite")
                    self.controller.import_bootstrap(self.raw, sha(self.raw), now=100)
                self.effect_snapshot(dispatched=dispatched)
                restored = self.restore_copy(self.controller, 101, "dispatch-" + str(dispatched))
                self.activate_local(restored, 101)
                fresh = self.claim_job(restored, 101)
                op = self.claim_effect(restored, fresh, 110)
                lease = Lease.from_record(op)
                op = restored.observe_effect("op-1", op["revision"], observation(op, "absent"),
                                             lease=lease, now=110)
                self.assertEqual((op["state"], op["uncertain"], op["dispatch_count"]),
                                 ("unknown", 1, int(dispatched)))
                self.assertEqual(op["next_check_at"], 130)
                self.assert_rejected_unchanged(restored, lambda: restored.begin_dispatch(
                    "op-1", op["revision"], lease=lease, now=110))
                for target in ("running", "verifying"):
                    self.assert_rejected_unchanged(restored, lambda: restored.transition(
                        "A", fresh["revision"], target, lease=Lease.from_record(fresh), now=110))
                self.assertEqual(restored.integrity()["open_effects"], 1)
