"""Run discovered public unit tests; zero, skipped and expected failures fail closed."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))


def run_suite(directory: str, report: Path | None = None) -> dict:
    suite = unittest.defaultTestLoader.discover(directory, pattern="test_*.py")
    expected = suite.countTestCases()
    if expected == 0:
        raise ValueError("Testauswahl ist leer")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary = {"expected": expected, "executed": result.testsRun,
               "failures": len(result.failures), "errors": len(result.errors),
               "skipped": len(result.skipped), "expectedFailures": len(result.expectedFailures),
               "unexpectedSuccesses": len(result.unexpectedSuccesses)}
    summary["passed"] = (result.wasSuccessful() and result.testsRun == expected
                         and not result.skipped and not result.expectedFailures)
    if report:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if not summary["passed"]:
        raise ValueError("Pflichtlauf fehlgeschlagen oder unvollstaendig")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(run_suite(args.directory, args.report), sort_keys=True))
    except (ValueError, ImportError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
