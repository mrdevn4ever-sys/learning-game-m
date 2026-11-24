"""Passive Startlisten-Uebernahme und Diagnose; keine Worker-/Release-CLI."""

import argparse
from pathlib import Path
import sqlite3
import sys

from .contracts import StoreError, Conflict, bootstrap, canonical, digest, integer, parse_json, runtime_path
from .core import Controller
from .gates import Policy, validate_report


ORIGINAL = Path(__file__).resolve().parents[3] / "steuerung/auftraege/phase-0.json"


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    preview = commands.add_parser("preview", help="Original unveraendert pruefen/anzeigen")
    preview.add_argument("--source", type=Path, default=ORIGINAL)
    take = commands.add_parser("import", help="Passiver, digestgebundener Einmalimport")
    take.add_argument("--source", type=Path, default=ORIGINAL)
    take.add_argument("--database", required=True, type=Path)
    take.add_argument("--expected-digest", required=True)
    take.add_argument("--now", type=int, required=True)
    for name in ("show", "check", "audit"):
        item = commands.add_parser(name)
        item.add_argument("--database", required=True, type=Path)
    backup = commands.add_parser("backup")
    backup.add_argument("--database", required=True, type=Path)
    backup.add_argument("--destination", required=True, type=Path)
    restore = commands.add_parser("restore", help="Neue, gesperrte Instanz aus Sicherung")
    restore.add_argument("--source", required=True, type=Path)
    restore.add_argument("--destination", required=True, type=Path)
    restore.add_argument("--expected-digest", required=True)
    restore.add_argument("--fencing-floor", required=True, type=int)
    restore.add_argument("--now", required=True, type=int)
    gate = commands.add_parser("validate-report", help="Nur Struktur, nie Freigabe")
    gate.add_argument("--report", required=True, type=Path)
    gate.add_argument("--policy", required=True, type=Path)
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command in {"preview", "import"}:
            raw = args.source.read_bytes()
            data, value = bootstrap(raw)
            if args.command == "preview":
                result = {"source_digest": value, "phase": data["phase"],
                          "count": len(data["auftraege"]), "jobs": data["auftraege"],
                          "note": "Passive Startliste; kein Auftragsabschluss und keine Freigabe"}
            else:
                if digest(args.expected_digest) != value:
                    raise Conflict("Startlistendigest stimmt nicht; keine Uebernahme")
                integer(args.now, "Importzeit")
                path = runtime_path(args.database)
                controller = Controller(path) if path.exists() else Controller.create(path)
                result = controller.import_bootstrap(raw, args.expected_digest, now=args.now)
                result["verified"] = controller.integrity()
        elif args.command == "restore":
            controller = Controller.restore(args.source, args.destination, args.expected_digest,
                                            fencing_floor=args.fencing_floor, now=args.now)
            result = {"database": str(controller.path), "recovery_locked": True,
                      "verified": controller.integrity()}
        elif args.command == "validate-report":
            policy = Policy.from_dict(parse_json(args.policy.read_bytes()))
            check = validate_report(parse_json(args.report.read_bytes()), policy)
            print(canonical(check.as_dict()))
            # Auch ein formal gueltiger lokaler Bericht bleibt unauthentisiert.
            return 3 if check.checks_valid else 2
        else:
            controller = Controller(args.database)
            if args.command == "show":
                result = controller.show()
            elif args.command == "check":
                result = controller.integrity()
            elif args.command == "audit":
                result = controller.audit()
            else:
                result = controller.backup(args.destination)
        print(canonical(result))
        return 0
    except (StoreError, OSError, sqlite3.Error) as exc:
        print(canonical({"error": str(exc), "release_authorized": False}), file=sys.stderr)
        return 2
