"""JSON-CLI ohne Dateien, Netz oder Freigaben zu veraendern."""
import argparse
import json
import sys

from .contracts import ContractError, load_json, validate_evidence
from .corpus import check_open_corpus
from .engine import evaluate_trace


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--trace", help="JSON-Ereignisliste oder offener Spurenumschlag")
    mode.add_argument("--evidence", help="Struktur eines Belegstatus pruefen; keine Authentisierung")
    mode.add_argument("--check-open-corpus", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.trace:
            data = load_json(args.trace)
            report = evaluate_trace(data["events"] if isinstance(data, dict) else data)
        elif args.evidence:
            validate_evidence(load_json(args.evidence))
            report = {"structureValid": True, "releaseAuthorized": False}
        else:
            report = check_open_corpus()
    except (ContractError, OSError, KeyError) as error:
        code = error.code if isinstance(error, ContractError) else "input_error"
        print(json.dumps({"error": code, "detail": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
