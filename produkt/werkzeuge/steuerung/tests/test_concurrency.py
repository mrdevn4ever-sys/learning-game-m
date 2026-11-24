from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import threading

from produkt.werkzeuge.steuerung import Conflict, Controller, Lease
from support import (LocalSink, StoreCase, arm, claim_process, crash_worker, effect_process,
                     interrupted_transaction, observation, prepare, start_running)


class ConcurrencyTests(StoreCase):
    def test_eight_parallel_threads_only_one_job_claim(self):
        barrier = threading.Barrier(8)

        def contender(index):
            c = Controller(self.controller.path)
            barrier.wait(timeout=10)
            try:
                return c.claim("A", 1, owner=f"thread-{index}", ttl=10, now=100)
            except Conflict:
                return None

        with ThreadPoolExecutor(max_workers=8) as workers:
            results = list(workers.map(contender, range(8)))
        winners = [row for row in results if row is not None]
        self.assertEqual(len(winners), 1)
        self.assertEqual(winners[0]["attempts"], 1)
        self.assertEqual(winners[0]["fencing_token"], 1)
        self.assertEqual(self.controller.job("A")["revision"], 2)

    def test_four_spawned_processes_only_one_job_claim(self):
        context = multiprocessing.get_context("spawn")
        barrier = context.Barrier(4)
        output = context.Queue()
        processes = [context.Process(target=claim_process,
                                     args=(str(self.controller.path), barrier, output, f"process-{i}"))
                     for i in range(4)]
        try:
            for process in processes:
                process.start()
            results = [output.get(timeout=30) for _ in processes]
            for process in processes:
                process.join(20)
                self.assertEqual(process.exitcode, 0)
            self.assertEqual([r[0] for r in results].count("won"), 1)
            self.assertEqual([r[0] for r in results].count("conflict"), 3)
            self.assertEqual(self.controller.job("A")["attempts"], 1)
        finally:
            for process in processes:
                if process.is_alive():
                    process.terminate()
                process.join(10)
                process.close()
            output.close()
            output.join_thread()

    def test_parallel_effect_claim_and_confirmation_have_one_winner(self):
        c = self.controller
        job, op = prepare(c, start_running(c))
        barrier = threading.Barrier(2)

        def claim(_):
            barrier.wait(timeout=10)
            try:
                return Controller(c.path).claim_effect("op-1", op["revision"],
                                                       job_lease=Lease.from_record(job), ttl=20, now=100)
            except Conflict:
                return None

        with ThreadPoolExecutor(max_workers=2) as workers:
            claims = list(workers.map(claim, range(2)))
        winners = [value for value in claims if value is not None]
        self.assertEqual(len(winners), 1)
        op = winners[0]
        op = c.observe_effect("op-1", op["revision"], observation(op, "absent"),
                              lease=Lease.from_record(op), now=100)
        lease = Lease.from_record(op)
        op = c.begin_dispatch("op-1", op["revision"], lease=lease, now=100)
        sink = LocalSink(self.folder / "sink.sqlite")
        sink.register(op)
        proof = sink.apply(op)
        barrier = threading.Barrier(2)

        def confirm(_):
            barrier.wait(timeout=10)
            try:
                return Controller(c.path).observe_effect("op-1", op["revision"], proof, lease=lease, now=100)
            except Conflict:
                return None

        with ThreadPoolExecutor(max_workers=2) as workers:
            results = list(workers.map(confirm, range(2)))
        self.assertEqual(sum(row is not None for row in results), 1)
        self.assertEqual(sink.count(), 1)
        self.assertEqual(c.effect("op-1")["state"], "confirmed")

    def test_two_spawned_processes_confirm_only_one_local_effect(self):
        c = self.controller
        prepare(c, start_running(c))
        context = multiprocessing.get_context("spawn")
        barrier, output = context.Barrier(2), context.Queue()
        sink = LocalSink(self.folder / "process-sink.sqlite")
        processes = [context.Process(target=effect_process,
                                     args=(str(c.path), sink.path, barrier, output)) for _ in range(2)]
        try:
            for process in processes:
                process.start()
            results = [output.get(timeout=30) for _ in processes]
            for process in processes:
                process.join(20)
                self.assertEqual(process.exitcode, 0)
            self.assertEqual(sorted(row[0] for row in results), ["confirmed", "conflict"])
            self.assertEqual(sink.count(), 1)
            self.assertEqual(c.effect("op-1")["dispatch_count"], 1)
            self.assertEqual(c.effect("op-1")["state"], "confirmed")
        finally:
            for process in processes:
                if process.is_alive():
                    process.terminate()
                process.join(10)
                process.close()
            output.close()
            output.join_thread()

    def test_renewal_and_expiry_sweep_are_serialized(self):
        c = self.controller
        job = start_running(c, ttl=10)
        barrier = threading.Barrier(2)

        def renew():
            barrier.wait(timeout=10)
            try:
                return c.renew("A", job["revision"], lease=Lease.from_record(job), ttl=20, now=110)
            except Conflict:
                return None

        def recover():
            barrier.wait(timeout=10)
            return c.recover_expired(now=110, retry_delay=1)

        with ThreadPoolExecutor(max_workers=2) as workers:
            first, second = workers.submit(renew), workers.submit(recover)
            self.assertIsNone(first.result(20))
            self.assertEqual(len(second.result(20)), 1)
        self.assertEqual(c.job("A")["state"], "retry_wait")


class ProcessDeathTests(StoreCase):
    def run_crash(self, point):
        context = multiprocessing.get_context("spawn")
        process = context.Process(target=crash_worker,
                                  args=(str(self.controller.path), str(self.folder / "sink.sqlite"), point))
        try:
            process.start()
            process.join(30)
            self.assertEqual(process.exitcode, 29)
        finally:
            if process.is_alive():
                process.terminate()
                process.join(10)
            process.close()
        return Controller(self.controller.path), LocalSink(self.folder / "sink.sqlite")

    def successor(self, c):
        c.recover_expired(now=110, retry_delay=1)
        job = c.job("A")
        job = c.claim("A", job["revision"], owner="successor", ttl=100, now=111)
        if job["state"] == "leased":
            job = c.transition("A", job["revision"], "running", lease=Lease.from_record(job), now=111)
        return job

    def test_process_dies_after_local_effect_successor_finds_no_reupload(self):
        c, sink = self.run_crash("effect")
        self.assertEqual(sink.count(), 1)
        op = c.effect("op-1")
        self.assertEqual(op["state"], "unknown")
        old = Lease.from_record(op)
        job = self.successor(c)
        self.assertEqual(job["state"], "reconciling")
        op = c.effect("op-1")
        op = c.claim_effect("op-1", op["revision"], job_lease=Lease.from_record(job), ttl=30, now=111)
        sink.register(op)
        with self.assertRaises(Conflict):
            c.observe_effect("op-1", op["revision"], sink.lookup(op), lease=old, now=111)
        op = c.observe_effect("op-1", op["revision"], sink.lookup(op), lease=Lease.from_record(op), now=111)
        self.assertEqual(op["state"], "confirmed")
        self.assertEqual(op["dispatch_count"], 1)
        self.assertEqual(sink.count(), 1)
        self.assertEqual(c.integrity()["open_effects"], 0)

    def test_crash_then_backup_restore_finds_durable_local_effect(self):
        c, sink = self.run_crash("effect")
        backup = c.backup(self.folder / "post-crash.sqlite")
        restored = Controller.restore(backup["path"], self.folder / "restored.sqlite", backup["digest"],
                                      fencing_floor=backup["fencing_highwater"], now=200)
        snapshot = restored.show()
        restored.activate_local_recovery(snapshot["meta"]["epoch"],
                                         fencing_floor=backup["fencing_highwater"],
                                         source_retired=True, inventory_reconciled=True, now=200)
        job = restored.job("A")
        job = restored.claim("A", job["revision"], owner="restored-worker", ttl=100, now=200)
        op = restored.effect("op-1")
        op = restored.claim_effect("op-1", op["revision"], job_lease=Lease.from_record(job), ttl=50, now=200)
        sink.register(op)
        op = restored.observe_effect("op-1", op["revision"], sink.lookup(op), lease=Lease.from_record(op), now=200)
        self.assertEqual(op["state"], "confirmed")
        self.assertEqual(sink.count(), 1)
        self.assertEqual(op["dispatch_count"], 1)
        self.assertEqual(restored.artifact(op["artifact_digest"]), b"synthetic archive")
        self.assertEqual(restored.integrity()["open_effects"], 0)

    def test_process_dies_after_intent_absence_stays_pending(self):
        c, sink = self.run_crash("intent")
        self.assertEqual(sink.count(), 0)
        job = self.successor(c)
        op = c.effect("op-1")
        op = c.claim_effect("op-1", op["revision"], job_lease=Lease.from_record(job), ttl=30, now=111)
        lease = Lease.from_record(op)
        op = c.observe_effect("op-1", op["revision"], sink.lookup(op), lease=lease, now=111)
        self.assertEqual(op["state"], "unknown")
        with self.assertRaises(Conflict):
            c.begin_dispatch("op-1", op["revision"], lease=lease, now=111)
        self.assertEqual(sink.count(), 0)

    def test_process_dies_before_dispatch_allows_only_checked_first_attempt(self):
        c, sink = self.run_crash("prepare")
        self.assertEqual(c.effect("op-1")["dispatch_count"], 0)
        job = self.successor(c)
        self.assertEqual(job["state"], "running")
        op = arm(c, job, c.effect("op-1"), now=111)
        sink.register(op)
        lease = Lease.from_record(op)
        op = c.begin_dispatch("op-1", op["revision"], lease=lease, now=111)
        c.observe_effect("op-1", op["revision"], sink.apply(op), lease=lease, now=111)
        self.assertEqual(sink.count(), 1)

    def test_process_dies_after_confirmation_receipt_survives_restart(self):
        c, sink = self.run_crash("confirm")
        self.assertEqual(c.effect("op-1")["state"], "confirmed")
        self.successor(c)
        self.assertEqual(c.effect("op-1")["observation"]["external_id"], "synthetic-receipt-1")
        self.assertEqual(sink.count(), 1)
        self.assertEqual(c.integrity()["open_effects"], 0)

    def test_real_termination_during_transaction_rolls_back_state_and_audit(self):
        context = multiprocessing.get_context("spawn")
        entered, hold = context.Event(), context.Event()
        before = self.controller.show()
        audit = self.controller.audit()
        process = context.Process(target=interrupted_transaction,
                                  args=(str(self.controller.path), entered, hold))
        try:
            process.start()
            self.assertTrue(entered.wait(20), "Kindprozess erreichte Transaktion nicht")
            process.terminate()
            process.join(20)
            self.assertIsNotNone(process.exitcode)
            self.assertNotEqual(process.exitcode, 0)
        finally:
            if process.is_alive():
                process.kill()
                process.join(10)
            process.close()
        reopened = Controller(self.controller.path)
        self.assertEqual(reopened.show(), before)
        self.assertEqual(reopened.audit(), audit)
        self.assertEqual(reopened.integrity()["integrity"], "ok")
