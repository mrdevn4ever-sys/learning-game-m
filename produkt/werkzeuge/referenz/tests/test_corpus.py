"""Offene Regressionen und Pflichtfaelle: feste Sollwerte, keine Selbstabnahme."""
from copy import deepcopy
import json
import subprocess
import sys
import unittest

from produkt.werkzeuge.referenz import ContractError, evaluate_trace, load_json, load_rules
from produkt.werkzeuge.referenz.contracts import CONTRACTS
from produkt.werkzeuge.referenz.corpus import check_open_corpus
from produkt.werkzeuge.referenz.offene_spuren import build_traces


class OpenTraceTests(unittest.TestCase):
    pass


def valid_test(path):
    def run(self):
        row = load_json(path)
        report = evaluate_trace(row["events"])
        self.assertEqual(report["decisions"], row["expected"])
        self.assertEqual({c["claimId"] for c in report["claims"]},
                         {c for c, v in row["expected"].items() if v == "must_claim"})
        self.assertEqual(report["curriculumSourceStatus"], "offen")
    return run


def invalid_test(path):
    def run(self):
        row = load_json(path)
        with self.assertRaises(ContractError) as ctx:
            evaluate_trace(row["events"])
        self.assertEqual(ctx.exception.code, row["expectedError"])
    return run


for _path in sorted((CONTRACTS / "spuren").glob("*.json")):
    setattr(OpenTraceTests, "test_spur_" + _path.stem.replace("-", "_"), valid_test(_path))
for _path in sorted((CONTRACTS / "ungueltig").glob("*.json")):
    setattr(OpenTraceTests, "test_ungueltig_" + _path.stem.replace("-", "_"), invalid_test(_path))


def events(name):
    return load_json(CONTRACTS / "spuren" / (name + ".json"))["events"]


class CorpusTests(unittest.TestCase):
    def test_complete_counts_and_three_cases_per_claim(self):
        report = check_open_corpus()
        self.assertEqual(report["validTraces"], 46)
        self.assertEqual(report["invalidTracesRejected"], 12)
        self.assertEqual(report["rules"], 5)
        self.assertEqual(report["decisions"], 230)
        self.assertEqual(report["outcomes"], {"must_claim": 60, "must_not_claim": 136, "undecidable": 34})
        for counter in report["byClaim"].values():
            self.assertEqual(set(counter), {"must_claim", "must_not_claim", "undecidable"})
            self.assertTrue(all(count > 0 for count in counter.values()))

    def test_export_is_reproducible_without_computing_expectations(self):
        good, bad = build_traces()
        for directory, rows in [("spuren", good), ("ungueltig", bad)]:
            self.assertEqual({p.stem for p in (CONTRACTS / directory).glob("*.json")}, set(rows))
            for name, row in rows.items():
                with self.subTest(name=name):
                    path = CONTRACTS / directory / (name + ".json")
                    self.assertEqual(load_json(path), row)
                    self.assertNotIn(b"\r\n", path.read_bytes())

    def test_all_event_types_have_explicit_open_examples(self):
        actual = {e["type"] for p in (CONTRACTS / "spuren").glob("*.json")
                  for e in load_json(p)["events"]}
        expected = set(load_json(CONTRACTS / "ereignis.schema.json")["properties"]["type"]["enum"])
        self.assertEqual(actual, expected)

    def test_reading_16_never_becomes_error_in_any_prefix(self):
        for name in ["korrigierte-fehllesung", "lesart-16", "automatisch-16"]:
            trace = events(name)
            for length in range(1, len(trace) + 1):
                with self.subTest(trace=name, length=length):
                    report = evaluate_trace(trace[:length])
                    self.assertNotEqual(report["facts"]["answer.deviation"], "wahr")
                    if length < len(trace):
                        self.assertFalse(report["claims"])
        report = evaluate_trace(events("korrigierte-fehllesung"))
        self.assertEqual(report["facts"]["answer.value.15"], "wahr")
        self.assertEqual(report["decisions"]["attempt.result.correct"], "must_claim")

    def test_free_way_does_not_imply_answer(self):
        report = evaluate_trace(events("frei-zehnerweg"))
        self.assertEqual(report["decisions"]["attempt.ten"], "must_claim")
        self.assertEqual(report["decisions"]["attempt.result.correct"], "undecidable")

    def test_failed_narrower_rule_is_not_positive_fallback(self):
        for name, expected in [("zehnerweg-falsches-ergebnis", "must_not_claim"),
                               ("hinweis-falsches-ergebnis", "must_not_claim"),
                               ("hinweis-ohne-ergebnis", "undecidable")]:
            report = evaluate_trace(events(name))
            self.assertNotIn("attempt.result.correct", {c["claimId"] for c in report["claims"]})
            self.assertEqual(report["decisions"]["attempt.result.correct"], expected)
            if name.startswith("hinweis"):
                self.assertEqual(report["decisions"]["attempt.ten"], "must_not_claim")

    def test_dedupe_is_idempotent_and_order_independent(self):
        trace = events("frei-zehnerweg-ergebnis")
        baseline = evaluate_trace(trace)
        report = evaluate_trace(list(reversed(deepcopy(trace) + deepcopy(trace))))
        self.assertEqual(report["facts"], baseline["facts"])
        self.assertEqual(report["claims"], baseline["claims"])
        self.assertEqual(report["integrity"]["deduplicated"], len(trace))
        self.assertEqual(report["integrity"]["uniqueEvents"], len(trace))

    def test_restore_from_json_is_identical(self):
        for path in (CONTRACTS / "spuren").glob("*.json"):
            trace = load_json(path)["events"]
            with self.subTest(trace=path.stem):
                self.assertEqual(evaluate_trace(trace), evaluate_trace(json.loads(json.dumps(trace))))

    def test_undo_preserves_historical_action_not_effective_way(self):
        facts = evaluate_trace(events("undo"))["facts"]
        self.assertEqual(facts["history.ten.child"], "wahr")
        self.assertEqual(facts["board.ten.child"], "falsch")

    def test_undo_does_not_remove_received_help(self):
        for name in ["undo-hinweis-erneut", "demo-wiederholung"]:
            facts = evaluate_trace(events(name))["facts"]
            self.assertEqual(facts["board.ten.child"], "wahr")
            self.assertEqual(facts["support.ten.before"], "wahr")

    def test_app_provenance_is_not_child(self):
        facts = evaluate_trace(events("app-demo"))["facts"]
        self.assertEqual(facts["board.ten.app"], "wahr")
        self.assertEqual(facts["board.ten.child"], "falsch")

    def test_late_hint_keeps_earlier_free_action(self):
        facts = evaluate_trace(events("hinweis-nach-zug"))["facts"]
        self.assertEqual(facts["support.ten.before"], "falsch")

    def test_gap_only_blocks_dependent_claims(self):
        report = evaluate_trace(events("luecke-vor-zug"))
        self.assertEqual(report["decisions"]["attempt.result.correct"], "must_claim")
        self.assertEqual(report["decisions"]["attempt.ten"], "undecidable")

    def test_sources_remain_open_and_partial(self):
        for rule in load_rules():
            for ref in rule["target"]["references"]:
                self.assertEqual(ref["quellenstatus"], "offen")
                self.assertEqual(ref["bezug"], "teil")
                self.assertNotIn("url", ref)
                self.assertNotIn("ausgabe", ref)

    def test_cli_executes_real_trace(self):
        result = subprocess.run([sys.executable, "-m", "produkt.werkzeuge.referenz", "--trace",
                                 str(CONTRACTS / "spuren" / "korrigierte-fehllesung.json")],
                                capture_output=True, text=True, encoding="utf-8", check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["decisions"]["attempt.result.correct"], "must_claim")

    def test_cli_invalid_trace_has_no_positive_stdout(self):
        result = subprocess.run([sys.executable, "-m", "produkt.werkzeuge.referenz", "--trace",
                                 str(CONTRACTS / "ungueltig" / "kind-app-demo.json")],
                                capture_output=True, text=True, encoding="utf-8", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertEqual(json.loads(result.stderr)["error"], "schema")
