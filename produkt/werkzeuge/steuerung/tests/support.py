"""Echte lokale Dateien/SQLite-Verbindungen, keine Providerattrappen im Produkt."""

from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

from produkt.werkzeuge.steuerung import Conflict, Controller, Lease
from produkt.werkzeuge.steuerung.contracts import RUNTIME, canonical, parse_json, sha


ROOT = Path(__file__).resolve().parents[4]
CANDIDATE = sha(b"public-synthetic-candidate")
TARGET = {"app_id": "synthetic.chnobel", "version": "0.0", "build_number": "1"}


def start_bytes(rows=None):
    if rows is None:
        rows = [{"id": "A", "titel": "Synthetischer Auftrag", "abhaengig": [], "zustand": "ready"},
                {"id": "B", "titel": "Synthetischer Folgeauftrag", "abhaengig": ["A"], "zustand": "planned"}]
    return canonical({"schemaVersion": "0.1.0", "phase": 0, "auftraege": rows}).encode("utf-8")


def start_running(controller, key="A", owner="worker", now=100, ttl=1000):
    job = controller.job(key)
    job = controller.claim(key, job["revision"], owner=owner, ttl=ttl, now=now)
    return controller.transition(key, job["revision"], "running", lease=Lease.from_record(job), now=now)


def complete(controller, job, now=100):
    lease = Lease.from_record(job)
    job, result = controller.record_artifact(job["id"], job["revision"], b"synthetic result",
                                             role="result", lease=lease, now=now)
    job = controller.transition(job["id"], job["revision"], "verifying", lease=lease, now=now)
    return controller.transition(job["id"], job["revision"], "done", results=[result], lease=lease, now=now)


def prepare(controller, job, operation_id="op-1", kind="upload", now=100, target=None):
    lease = Lease.from_record(job)
    job, archive = controller.record_artifact(job["id"], job["revision"], b"synthetic archive",
                                              role="archive", lease=lease, now=now)
    if target is None:
        target = TARGET if kind == "upload" else {
            "repository": "synthetic/example", "branch": "main", "commit": "a" * 40}
    result = controller.prepare_effect(job["id"], job["revision"], operation_id, kind,
                                       CANDIDATE, archive, target, lease=lease, now=now)
    return result["job"], result["effect"]


def observation(op, outcome, **extras):
    value = {key: op[key] for key in ("operation_id", "request_digest", "candidate_digest", "artifact_digest")}
    value.update(outcome=outcome, target=op["request"]["target"])
    if outcome == "found":
        value["external_id"] = "synthetic-receipt-1"
    if outcome == "unknown":
        value["reason"] = "Synthetischer Provider ist voruebergehend nicht auswertbar"
    value.update(extras)
    return value


def arm(controller, job, op, now=100, ttl=1000):
    op = controller.claim_effect(op["operation_id"], op["revision"], job_lease=Lease.from_record(job),
                                  ttl=ttl, now=now)
    return controller.observe_effect(op["operation_id"], op["revision"], observation(op, "absent"),
                                     lease=Lease.from_record(op), now=now)


class LocalSink:
    """Nur Tests: lokale persistente Wirkung mit eindeutiger ID und Fencing."""
    def __init__(self, path):
        self.path = str(path)
        with self.connection() as db:
            db.execute("CREATE TABLE IF NOT EXISTS fences (id TEXT PRIMARY KEY, token INTEGER NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS effects (id TEXT PRIMARY KEY, target TEXT UNIQUE, "
                       "request TEXT NOT NULL, token INTEGER NOT NULL, receipt TEXT NOT NULL)")

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=15)
        try:
            with db:
                yield db
        finally:
            db.close()

    def register(self, op):
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT token FROM fences WHERE id=?", (op["operation_id"],)).fetchone()
            if old and old[0] > op["fencing_token"]:
                raise Conflict("Lokaler Wirkungsdienst weist alten Token ab")
            db.execute("INSERT INTO fences VALUES (?,?) ON CONFLICT(id) DO UPDATE SET token=excluded.token",
                       (op["operation_id"], op["fencing_token"]))

    def apply(self, op):
        with self.connection() as db:
            db.execute("PRAGMA synchronous=FULL")
            db.execute("BEGIN IMMEDIATE")
            token = db.execute("SELECT token FROM fences WHERE id=?", (op["operation_id"],)).fetchone()
            if not token or token[0] != op["fencing_token"]:
                raise Conflict("Nicht aktuelle Wirkungsberechtigung")
            prior = db.execute("SELECT request FROM effects WHERE id=?", (op["operation_id"],)).fetchone()
            request = canonical(op["request"])
            if prior and prior[0] != request:
                raise Conflict("Operations-ID kollidiert im lokalen Dienst")
            db.execute("INSERT OR IGNORE INTO effects VALUES (?,?,?,?,?)",
                       (op["operation_id"], canonical(op["request"]["target"]), request,
                        op["fencing_token"], "synthetic-receipt-1"))
        return self.lookup(op)

    def lookup(self, op):
        with self.connection() as db:
            row = db.execute("SELECT request,receipt FROM effects WHERE id=?", (op["operation_id"],)).fetchone()
        if not row:
            return observation(op, "absent")
        request = parse_json(row[0])
        return observation(op, "found", request_digest=sha(row[0].encode("utf-8")),
                           candidate_digest=request["candidate_digest"], artifact_digest=request["artifact_digest"],
                           target=request["target"], external_id=row[1])

    def count(self):
        with self.connection() as db:
            return db.execute("SELECT count(*) FROM effects").fetchone()[0]


class StoreCase(unittest.TestCase):
    def setUp(self):
        RUNTIME.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="synthetic-steuerung-", dir=RUNTIME)
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.controller = Controller.create(self.folder / "controller.sqlite")
        self.raw = start_bytes()
        self.controller.import_bootstrap(self.raw, sha(self.raw), now=100)


def claim_process(path, barrier, output, owner):
    try:
        controller = Controller(path)
        barrier.wait(timeout=20)
        job = controller.claim("A", 1, owner=owner, ttl=20, now=100)
        output.put(("won", job["fencing_token"]))
    except Conflict:
        output.put(("conflict", None))
    except BaseException as exc:
        output.put(("error", repr(exc)))


def crash_worker(path, sink_path, point):
    controller = Controller(path)
    job = start_running(controller, owner="crash-worker", ttl=10)
    job, op = prepare(controller, job)
    if point == "prepare":
        os._exit(29)
    op = arm(controller, job, op, ttl=10)
    sink = LocalSink(sink_path)
    sink.register(op)
    op = controller.begin_dispatch(op["operation_id"], op["revision"], lease=Lease.from_record(op), now=100)
    if point == "intent":
        os._exit(29)
    proof = sink.apply(op)
    if point == "effect":
        os._exit(29)
    controller.observe_effect(op["operation_id"], op["revision"], proof, lease=Lease.from_record(op), now=100)
    os._exit(29)


def effect_process(path, sink_path, barrier, output):
    try:
        controller = Controller(path)
        job, op = controller.job("A"), controller.effect("op-1")
        barrier.wait(timeout=20)
        op = controller.claim_effect("op-1", op["revision"], job_lease=Lease.from_record(job), ttl=20, now=100)
        sink = LocalSink(sink_path)
        sink.register(op)
        op = controller.observe_effect("op-1", op["revision"], sink.lookup(op), lease=Lease.from_record(op), now=100)
        lease = Lease.from_record(op)
        op = controller.begin_dispatch("op-1", op["revision"], lease=lease, now=100)
        op = controller.observe_effect("op-1", op["revision"], sink.apply(op), lease=lease, now=100)
        output.put(("confirmed", op["fencing_token"]))
    except Conflict:
        output.put(("conflict", None))
    except BaseException as exc:
        output.put(("error", repr(exc)))


def interrupted_transaction(path, entered, hold):
    controller = Controller(path)
    with controller._transaction(101) as db:
        row = controller._row(db, "jobs", "A")
        controller._save_job(db, row, 101, "synthetic_uncommitted", state="blocked",
                             blocked_reason="Nur synthetischer Abbruchtest")
        entered.set()
        hold.wait(60)
