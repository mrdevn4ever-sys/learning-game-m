import copy

from produkt.werkzeuge.steuerung import Conflict, Controller, Invalid, Lease
from produkt.werkzeuge.steuerung.contracts import sha
from support import (CANDIDATE, TARGET, LocalSink, StoreCase, arm, complete, observation,
                     prepare, start_running)


class JournalTests(StoreCase):
    def test_merge_and_upload_use_same_durable_protocol(self):
        for kind in ("merge", "upload"):
            with self.subTest(kind=kind):
                if kind == "merge":
                    c = self.controller
                else:
                    c = Controller.create(self.folder / "upload.sqlite")
                    c.import_bootstrap(self.raw, sha(self.raw), now=100)
                job = start_running(c)
                job, op = prepare(c, job, kind=kind)
                self.assertEqual(Controller(c.path).effect(op["operation_id"])["state"], "prepared")
                self.assertEqual(op["dispatch_count"], 0)
                op = arm(c, job, op)
                lease = Lease.from_record(op)
                sink = LocalSink(self.folder / f"{kind}-sink.sqlite")
                sink.register(op)
                op = c.begin_dispatch(op["operation_id"], op["revision"], lease=lease, now=100)
                self.assertEqual(Controller(c.path).effect(op["operation_id"])["state"], "unknown")
                proof = sink.apply(op)
                op = c.observe_effect(op["operation_id"], op["revision"], proof, lease=lease, now=100)
                self.assertEqual(op["state"], "confirmed")
                self.assertEqual(sink.count(), 1)
                self.assertEqual(complete(c, job)["state"], "done")
                self.assertEqual(c.integrity()["open_effects"], 0)

    def test_duplicate_operation_id_same_payload_is_idempotent(self):
        c = self.controller
        job, op = prepare(c, start_running(c))
        before = c.show()
        duplicate = c.prepare_effect("A", job["revision"], "op-1", "upload", CANDIDATE,
                                     op["artifact_digest"], TARGET, lease=Lease.from_record(job), now=100)
        self.assertEqual(duplicate["effect"], op)
        self.assertEqual(c.show(), before)

    def test_operation_id_reuse_or_duplicate_build_number_rejected(self):
        c = self.controller
        job, op = prepare(c, start_running(c))
        for operation_id, candidate, target in (
            ("op-1", sha(b"other"), TARGET),
            ("op-2", CANDIDATE, TARGET),
            ("op-1", CANDIDATE, {**TARGET, "build_number": "2"}),
        ):
            with self.subTest(operation_id=operation_id, target=target), self.assertRaises(Conflict):
                c.prepare_effect("A", job["revision"], operation_id, "upload", candidate,
                                 op["artifact_digest"], target, lease=Lease.from_record(job), now=100)
        self.assertEqual(c.integrity()["effects"], 1)

    def test_first_dispatch_requires_prior_claim_and_absence_lookup(self):
        c = self.controller
        job, op = prepare(c, start_running(c))
        with self.assertRaises(Conflict):
            c.begin_dispatch("op-1", op["revision"], lease=Lease.from_record(job), now=100)
        op = c.claim_effect("op-1", op["revision"], job_lease=Lease.from_record(job), ttl=20, now=100)
        with self.assertRaises(Conflict):
            c.begin_dispatch("op-1", op["revision"], lease=Lease.from_record(op), now=100)
        self.assertEqual(c.effect("op-1")["dispatch_count"], 0)

    def test_existing_exact_effect_is_reconciled_without_dispatch(self):
        c = self.controller
        job, op = prepare(c, start_running(c))
        op = c.claim_effect("op-1", op["revision"], job_lease=Lease.from_record(job), ttl=20, now=100)
        op = c.observe_effect("op-1", op["revision"], observation(op, "found"),
                              lease=Lease.from_record(op), now=100)
        self.assertEqual(op["state"], "confirmed")
        self.assertEqual(op["dispatch_count"], 0)
        with self.assertRaises(Conflict):
            c.claim_effect("op-1", op["revision"], job_lease=Lease.from_record(job), ttl=20, now=100)

    def test_unknown_probe_defers_and_cannot_dispatch(self):
        c = self.controller
        job, op = prepare(c, start_running(c))
        op = c.claim_effect("op-1", op["revision"], job_lease=Lease.from_record(job), ttl=20, now=100)
        lease = Lease.from_record(op)
        op = c.observe_effect("op-1", op["revision"], observation(op, "unknown"), lease=lease, now=100)
        self.assertEqual(op["state"], "unknown")
        self.assertEqual(op["next_check_at"], 110)
        with self.assertRaises(Conflict):
            c.claim_effect("op-1", op["revision"], job_lease=Lease.from_record(job), ttl=20, now=109)
        with self.assertRaises(Conflict):
            c.begin_dispatch("op-1", op["revision"], lease=lease, now=100)
        # Vor dem allerersten Versuch ist ein spaeterer eindeutiger Negativfund ausreichend.
        op = arm(c, job, op, now=110)
        self.assertEqual(op["state"], "armed")
        self.assertGreater(op["fencing_token"], lease.token)

    def test_absent_after_dispatch_never_authorizes_retry(self):
        c = self.controller
        job, op = prepare(c, start_running(c))
        op = arm(c, job, op)
        old = Lease.from_record(op)
        op = c.begin_dispatch("op-1", op["revision"], lease=old, now=100)
        op = c.observe_effect("op-1", op["revision"], observation(op, "absent"), lease=old, now=100)
        self.assertEqual(op["state"], "unknown")
        op = c.claim_effect("op-1", op["revision"], job_lease=Lease.from_record(job), ttl=20, now=110)
        current = Lease.from_record(op)
        op = c.observe_effect("op-1", op["revision"], observation(op, "absent"), lease=current, now=110)
        self.assertEqual(op["state"], "unknown")
        self.assertEqual(op["dispatch_count"], 1)
        self.assertEqual(op["next_check_at"], 130)
        with self.assertRaises(Conflict):
            c.begin_dispatch("op-1", op["revision"], lease=current, now=110)

    def test_wrong_candidate_archive_target_or_operation_proof_fails(self):
        c = self.controller
        job, op = prepare(c, start_running(c))
        op = c.claim_effect("op-1", op["revision"], job_lease=Lease.from_record(job), ttl=20, now=100)
        base = observation(op, "found")
        mutations = {"candidate_digest": sha(b"other candidate"), "artifact_digest": sha(b"other archive"),
                     "operation_id": "other-op", "request_digest": sha(b"other request"),
                     "target": {**TARGET, "build_number": "2"}}
        for key, value in mutations.items():
            proof = copy.deepcopy(base)
            proof[key] = value
            with self.subTest(key=key), self.assertRaises(Conflict):
                c.observe_effect("op-1", op["revision"], proof, lease=Lease.from_record(op), now=100)
        self.assertEqual(c.effect("op-1")["state"], "checking")

    def test_stale_effect_lease_cannot_confirm_even_with_current_revision(self):
        c = self.controller
        job, op = prepare(c, start_running(c))
        op = arm(c, job, op, ttl=5)
        old = Lease.from_record(op)
        op = c.begin_dispatch("op-1", op["revision"], lease=old, now=100)
        c.recover_expired(now=105, retry_delay=1)
        op = c.effect("op-1")
        op = c.claim_effect("op-1", op["revision"], job_lease=Lease.from_record(job), ttl=10, now=106)
        self.assertGreater(op["fencing_token"], old.token)
        with self.assertRaises(Conflict):
            c.observe_effect("op-1", op["revision"], observation(op, "found"), lease=old, now=106)
        confirmed = c.observe_effect("op-1", op["revision"], observation(op, "found"),
                                     lease=Lease.from_record(op), now=106)
        self.assertEqual(confirmed["state"], "confirmed")

    def test_parent_lease_expiry_fences_effect_and_reconciliation(self):
        c = self.controller
        job, op = prepare(c, start_running(c, ttl=10))
        op = arm(c, job, op, ttl=100)
        self.assertEqual(op["lease_expires"], job["lease_expires"])
        old = Lease.from_record(op)
        op = c.begin_dispatch("op-1", op["revision"], lease=old, now=100)
        with self.assertRaises(Conflict):
            c.observe_effect("op-1", op["revision"], observation(op, "found"), lease=old, now=110)
        c.recover_expired(now=110, retry_delay=1)
        job = c.job("A")
        self.assertEqual(job["state"], "reconciling")
        with self.assertRaises(Conflict):
            c.transition("A", job["revision"], "running", now=111)
        job = c.claim("A", job["revision"], owner="successor", ttl=100, now=111)
        op = c.effect("op-1")
        op = c.claim_effect("op-1", op["revision"], job_lease=Lease.from_record(job), ttl=20, now=111)
        c.observe_effect("op-1", op["revision"], observation(op, "found"), lease=Lease.from_record(op), now=111)
        job = c.transition("A", job["revision"], "running", lease=Lease.from_record(job), now=111)
        self.assertEqual(complete(c, job, now=111)["state"], "done")

    def test_unresolved_effect_prevents_success_retry_and_supersession(self):
        c = self.controller
        job, op = prepare(c, start_running(c))
        op = arm(c, job, op)
        c.begin_dispatch("op-1", op["revision"], lease=Lease.from_record(op), now=100)
        for state, extra in (("verifying", {}), ("retry_wait", {"next_check_at": 200})):
            with self.subTest(state=state), self.assertRaises(Conflict):
                c.transition("A", job["revision"], state, lease=Lease.from_record(job), now=100, **extra)
        blocked = c.transition("A", job["revision"], "blocked", lease=Lease.from_record(job),
                               reason="extern blockiert", now=100)
        for state in ("planned", "superseded"):
            with self.subTest(state=state), self.assertRaises(Conflict):
                c.transition("A", blocked["revision"], state, reason="abgeloest" if state == "superseded" else None, now=100)
        self.assertEqual(c.transition("A", blocked["revision"], "reconciling", now=100)["state"], "reconciling")

    def test_local_effect_service_rejects_stale_fence(self):
        c = self.controller
        job, op = prepare(c, start_running(c))
        op = arm(c, job, op, ttl=5)
        sink = LocalSink(self.folder / "sink.sqlite")
        sink.register(op)
        old = c.begin_dispatch("op-1", op["revision"], lease=Lease.from_record(op), now=100)
        c.recover_expired(now=105, retry_delay=1)
        current = c.effect("op-1")
        current = c.claim_effect("op-1", current["revision"], job_lease=Lease.from_record(job), ttl=10, now=106)
        sink.register(current)
        with self.assertRaises(Conflict):
            sink.apply(old)
        with self.assertRaises(Conflict):
            sink.register(old)
        self.assertEqual(sink.count(), 0)

    def test_prepare_requires_archived_bytes_not_an_unbacked_digest(self):
        c = self.controller
        job = start_running(c)
        with self.assertRaises(Invalid):
            c.prepare_effect("A", job["revision"], "op-1", "upload", CANDIDATE, sha(b"not stored"),
                             TARGET, lease=Lease.from_record(job), now=100)
        self.assertEqual(c.integrity()["effects"], 0)
