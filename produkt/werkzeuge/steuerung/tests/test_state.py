import copy
import sqlite3

from produkt.werkzeuge.steuerung import Conflict, Controller, Invalid, Lease
from produkt.werkzeuge.steuerung.contracts import bootstrap, canonical, parse_json, sha, STATES
from support import StoreCase, complete, start_bytes, start_running


class StateTests(StoreCase):
    def test_normal_path_requires_dependencies_and_results(self):
        c = self.controller
        with self.assertRaises(Conflict):
            c.transition("B", 1, "ready", now=100)
        job = start_running(c)
        with self.assertRaises(Invalid):
            c.transition("A", job["revision"], "done", lease=Lease.from_record(job), results=[], now=100)
        done = complete(c, job)
        self.assertEqual(done["state"], "done")
        self.assertIsNone(done["lease_owner"])
        self.assertTrue(done["results"])
        self.assertEqual(c.transition("B", 1, "ready", now=100)["state"], "ready")
        with self.assertRaises(Invalid):
            c.transition("A", done["revision"], "planned", now=100)
        self.assertEqual(c.integrity()["jobs"], 2)

    def test_all_prescribed_states_are_declared(self):
        self.assertEqual(STATES, {"planned", "ready", "leased", "running", "verifying", "done",
                                  "retry_wait", "reconciling", "blocked", "superseded"})

    def test_compare_and_swap_rejects_old_revision_atomically(self):
        c = self.controller
        leased = c.claim("A", 1, owner="worker", ttl=10, now=100)
        before = c.show()
        with self.assertRaises(Conflict):
            c.transition("A", 1, "running", lease=Lease.from_record(leased), now=101)
        self.assertEqual(c.show(), before)
        self.assertEqual(len(c.audit()), 3)

    def test_skip_steps_and_direct_leased_transition_are_rejected(self):
        c = self.controller
        for target in ("leased", "running", "verifying", "done", "reconciling", "retry_wait"):
            with self.subTest(target=target), self.assertRaises(Invalid):
                c.transition("A", 1, target, now=100)
        with self.assertRaises(Conflict):
            c.claim("B", 1, owner="worker", ttl=10, now=100)

    def test_block_requires_reason_and_does_not_complete_dependency(self):
        c = self.controller
        with self.assertRaises(Invalid):
            c.transition("A", 1, "blocked", now=100, reason=" ")
        blocked = c.transition("A", 1, "blocked", now=100, reason="extern blockiert")
        self.assertEqual(blocked["blocked_reason"], "extern blockiert")
        with self.assertRaises(Conflict):
            c.transition("B", 1, "ready", now=100)
        planned = c.transition("A", blocked["revision"], "planned", now=100)
        self.assertIsNone(planned["blocked_reason"])
        ready = c.transition("A", planned["revision"], "ready", now=100)
        self.assertGreater(ready["revision"], blocked["revision"])

    def test_superseded_is_terminal_and_not_success(self):
        c = self.controller
        with self.assertRaises(Invalid):
            c.transition("A", 1, "superseded", now=100)
        job = c.transition("A", 1, "superseded", reason="Synthetischer Ersatzauftrag", now=100)
        self.assertEqual(job["state"], "superseded")
        with self.assertRaises(Conflict):
            c.transition("B", 1, "ready", now=100)
        with self.assertRaises(Conflict):
            c.claim("A", job["revision"], owner="worker", ttl=10, now=100)

    def test_retry_deadline_survives_reopen(self):
        c = self.controller
        job = start_running(c)
        retry = c.transition("A", job["revision"], "retry_wait", next_check_at=120,
                             lease=Lease.from_record(job), now=100)
        c = Controller(c.path)
        with self.assertRaises(Conflict):
            c.claim("A", retry["revision"], owner="second", ttl=10, now=119)
        leased = c.claim("A", retry["revision"], owner="second", ttl=10, now=120)
        self.assertEqual(leased["attempts"], 2)
        self.assertGreater(leased["fencing_token"], job["fencing_token"])

    def test_expiry_boundary_stale_worker_and_renewal(self):
        c = self.controller
        job = start_running(c, ttl=10)
        old = Lease.from_record(job)
        with self.assertRaises(Conflict):
            c.renew("A", job["revision"], lease=old, ttl=20, now=110)
        changed = c.recover_expired(now=110, retry_delay=2)
        self.assertEqual(len(changed), 1)
        self.assertEqual(changed[0]["state"], "retry_wait")
        leased = c.claim("A", changed[0]["revision"], owner="worker", ttl=10, now=112)
        with self.assertRaises(Conflict):
            c.transition("A", leased["revision"], "running", lease=old, now=112)
        self.assertGreater(leased["fencing_token"], old.token)
        renewed = c.renew("A", leased["revision"], lease=Lease.from_record(leased), ttl=20, now=113)
        self.assertEqual(renewed["lease_expires"], 133)
        self.assertEqual(c.recover_expired(now=132), [])
        self.assertEqual(len(c.recover_expired(now=133)), 1)

    def test_wrong_owner_token_epoch_and_absent_lease(self):
        c = self.controller
        job = start_running(c)
        valid = Lease.from_record(job)
        bad = [None, Lease(valid.epoch, "other", valid.token),
               Lease(valid.epoch, valid.owner, valid.token + 1),
               Lease("old-epoch", valid.owner, valid.token)]
        for lease in bad:
            with self.subTest(lease=lease), self.assertRaises(Conflict):
                c.transition("A", job["revision"], "verifying", now=100, lease=lease)

    def test_clock_rollback_rejected_across_instances(self):
        c = self.controller
        job = c.claim("A", 1, owner="worker", ttl=10, now=105)
        with self.assertRaises(Conflict):
            Controller(c.path).transition("A", job["revision"], "running", now=104,
                                          lease=Lease.from_record(job))
        self.assertEqual(c.job("A")["state"], "leased")
        self.assertEqual(c.show()["meta"]["clock"], "105")

    def test_strict_integer_fields_reject_boolean_and_float(self):
        c = self.controller
        for value in (True, 1.0, "1", -1):
            with self.subTest(value=value), self.assertRaises(Invalid):
                c.claim("A", value, owner="worker", ttl=1, now=100)
        for value in (True, 1.0, 0, -1):
            with self.subTest(ttl=value), self.assertRaises(Invalid):
                c.claim("A", 1, owner="worker", ttl=value, now=100)

    def test_results_must_reference_owned_artifacts(self):
        c = self.controller
        job = start_running(c)
        lease = Lease.from_record(job)
        job = c.transition("A", job["revision"], "verifying", lease=lease, now=100)
        for results in (None, [], [[]], [sha(b"missing")], [sha(b"x"), sha(b"x")]):
            with self.subTest(results=results), self.assertRaises(Invalid):
                c.transition("A", job["revision"], "done", results=results, lease=lease, now=100)
        job, value = c.record_artifact("A", job["revision"], b"local result", role="result", lease=lease, now=100)
        self.assertEqual(c.artifact(value), b"local result")
        self.assertEqual(c.transition("A", job["revision"], "done", results=[value], lease=lease, now=100)["state"], "done")

    def test_audit_is_append_only(self):
        with self.controller._connection() as db:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("DELETE FROM audit")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE audit SET action='changed'")
        self.assertEqual(len(self.controller.audit()), 2)

    def test_deterministic_replay_except_store_epoch(self):
        other = Controller.create(self.folder / "other.sqlite")
        other.import_bootstrap(self.raw, sha(self.raw), now=100)
        for controller in (self.controller, other):
            complete(controller, start_running(controller))
            controller.transition("B", 1, "ready", now=100)
        first, second = self.controller.show(), other.show()
        for result in (first, second):
            del result["meta"]["epoch"]
            for row in result["jobs"]:
                del row["epoch"]
        self.assertEqual(first, second)
        self.assertEqual(self.controller.audit(), other.audit())


class BootstrapTests(StoreCase):
    def test_idempotent_import_never_resets_progress(self):
        job = start_running(self.controller)
        before = self.controller.show()
        result = self.controller.import_bootstrap(self.raw, sha(self.raw), now=100)
        self.assertFalse(result["imported"])
        self.assertEqual(self.controller.show(), before)
        self.assertEqual(self.controller.job("A")["revision"], job["revision"])

    def test_changed_source_and_wrong_digest_rejected(self):
        with self.assertRaises(Conflict):
            self.controller.import_bootstrap(self.raw, sha(b"wrong"), now=100)
        altered = self.raw + b"\n"
        with self.assertRaises(Conflict):
            self.controller.import_bootstrap(altered, sha(altered), now=100)
        self.assertEqual(self.controller.integrity()["jobs"], 2)

    def test_invalid_graphs_and_active_bootstrap_states(self):
        base = parse_json(self.raw)
        variants = []
        for state in ("done", "leased", "running", "blocked", "unknown"):
            value = copy.deepcopy(base)
            value["auftraege"][0]["zustand"] = state
            variants.append(value)
        for deps in (["missing"], ["A"], ["B", "B"], ["B"]):
            value = copy.deepcopy(base)
            value["auftraege"][0]["zustand"] = "planned"
            value["auftraege"][0]["abhaengig"] = deps
            variants.append(value)
        duplicate = copy.deepcopy(base)
        duplicate["auftraege"].append(duplicate["auftraege"][0])
        variants.append(duplicate)
        ready_with_dependency = copy.deepcopy(base)
        ready_with_dependency["auftraege"][1]["zustand"] = "ready"
        variants.append(ready_with_dependency)
        for value in variants:
            with self.subTest(value=value), self.assertRaises(Invalid):
                bootstrap(canonical(value).encode("utf-8"))

    def test_duplicate_json_keys_and_nonfinite_values_rejected(self):
        for raw in (b'{"phase":0,"phase":1}', b'{"phase":NaN}', b'\xff', b'[]'):
            with self.subTest(raw=raw), self.assertRaises(Invalid):
                bootstrap(raw)

    def test_malformed_state_utf16_and_escaping_paths_fail_closed(self):
        for state in ([], {}, True, None):
            data = parse_json(self.raw)
            data["auftraege"][0]["zustand"] = state
            with self.subTest(state=state), self.assertRaises(Invalid):
                bootstrap(canonical(data).encode("utf-8"))
        with self.assertRaises(Invalid):
            bootstrap(self.raw.decode("utf-8").encode("utf-16"))
        with self.assertRaises(Invalid):
            Controller.create("F:/ChnobelRuntime/steuerung/../outside.sqlite")

    def test_database_creation_is_explicit_and_never_overwrites(self):
        with self.assertRaises(Conflict):
            Controller.create(self.controller.path)
        with self.assertRaises(Invalid):
            Controller(self.folder / "missing.sqlite")
        self.assertFalse((self.folder / "missing.sqlite").exists())
        with self.assertRaises(Invalid):
            Controller.create("C:/not-allowed.sqlite")
