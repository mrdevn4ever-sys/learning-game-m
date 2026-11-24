"""Strikte Eingaben und unveraenderte Uebernahme der Startliste."""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


class StoreError(Exception):
    """Erwarteter, fail-closed Steuerungsfehler."""


class Invalid(StoreError):
    pass


class Conflict(StoreError):
    pass


@dataclass(frozen=True)
class Lease:
    epoch: str
    owner: str
    token: int
    job_token: int = 0

    @classmethod
    def from_record(cls, record):
        if record["lease_owner"] is None:
            raise Invalid("Datensatz hat keine Lease")
        return cls(record["epoch"], record["lease_owner"], record["fencing_token"],
                   record.get("job_fencing_token", 0))


RUNTIME = Path("F:/ChnobelRuntime/steuerung")
CACHE = Path("F:/ChnobelRuntime/cache")
STATES = frozenset({"planned", "ready", "leased", "running", "verifying", "done",
                    "retry_wait", "reconciling", "blocked", "superseded"})


def integer(value, name, minimum=0):
    if type(value) is not int or not minimum <= value <= 2**63 - 1:
        raise Invalid(f"{name}: ganze Zahl ab {minimum} erforderlich")
    return value


def text(value, name):
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise Invalid(f"{name}: nichtleerer exakter Text erforderlich")
    return value


def identifier(value, name="ID"):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", value):
        raise Invalid(f"{name}: ungueltiges Format")
    return value


def digest(value, name="Digest"):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise Invalid(f"{name}: exakter SHA-256 (64 kleine Hexzeichen) erforderlich")
    return value


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise Invalid("Kein gueltiger JSON-Wert") from exc


def parse_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise Invalid(f"Doppelter JSON-Schluessel: {key}")
            result[key] = value
        return result

    def bad_constant(value):
        raise Invalid(f"Ungueltige JSON-Konstante: {value}")

    try:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad_constant)
    except (ValueError, UnicodeError, TypeError) as exc:
        raise Invalid("Ungueltiges JSON/UTF-8") from exc


def fields(value, required, optional=()):
    if not isinstance(value, dict) or not set(required) <= value.keys():
        raise Invalid("Pflichtfelder fehlen")
    if value.keys() - set(required) - set(optional):
        raise Invalid("Unbekannte Felder")


def runtime_path(path):
    candidate = Path(path).resolve()
    base = RUNTIME.resolve()
    if (base.drive.lower() != "f:" or candidate.drive.lower() != "f:"
            or not candidate.is_relative_to(base) or candidate == base):
        raise Invalid("Laufzeitdaten ausschliesslich unter F:/ChnobelRuntime/steuerung")
    return candidate


def bootstrap(raw):
    """Keine Statuskorrektur, kein Sortieren von Abhaengigkeiten, kein Teilimport."""
    if not isinstance(raw, bytes):
        raise Invalid("Startliste muss als unveraenderte Bytes vorliegen")
    data = parse_json(raw)
    fields(data, {"schemaVersion", "phase", "auftraege"}, {"hinweis"})
    if data["schemaVersion"] != "0.1.0":
        raise Invalid("Nicht unterstuetzte Startlisten-Version")
    integer(data["phase"], "Phase")
    if "hinweis" in data:
        text(data["hinweis"], "Hinweis")
    rows = data["auftraege"]
    if not isinstance(rows, list) or not rows:
        raise Invalid("Startliste ist leer")
    graph = {}
    for row in rows:
        fields(row, {"id", "titel", "abhaengig", "zustand"})
        key = identifier(row["id"])
        text(row["titel"], "Titel")
        if key in graph:
            raise Invalid("Doppelte Auftrags-ID")
        deps = row["abhaengig"]
        if not isinstance(deps, list):
            raise Invalid("Abhaengigkeiten muessen eine Liste sein")
        for dep in deps:
            identifier(dep, "Abhaengigkeit")
        if len(deps) != len(set(deps)) or key in deps:
            raise Invalid("Doppelte oder eigene Abhaengigkeit")
        if not isinstance(row["zustand"], str) or row["zustand"] not in {"planned", "ready"}:
            raise Invalid("Import uebernimmt nur passive Startzustaende")
        if row["zustand"] == "ready" and deps:
            raise Invalid("Startauftrag mit offenen Abhaengigkeiten ist nicht ready")
        graph[key] = deps
    if any(dep not in graph for deps in graph.values() for dep in deps):
        raise Invalid("Unbekannte Abhaengigkeit")
    # Kahn statt Rekursion: grosse Startlisten bleiben kontrolliert validierbar.
    pending = {key: set(deps) for key, deps in graph.items()}
    while pending:
        roots = {key for key, deps in pending.items() if not deps}
        if not roots:
            raise Invalid("Abhaengigkeitszyklus")
        pending = {key: deps - roots for key, deps in pending.items() if key not in roots}
    return data, sha(raw)
