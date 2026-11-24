"""Schema-, Referenz- und fail-closed Negativtests fuer v1."""
from copy import deepcopy
import hashlib
import io
import itertools
from pathlib import Path
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from produkt.werkzeuge.referenz import (ContractError, Truth, conjunction, decide,
                                       load_json, load_rules, negate, validate_evidence,
                                       validate_rules, validate_schema)
from produkt.werkzeuge.referenz.contracts import CONTRACTS, FACTS, validator
from produkt.werkzeuge.referenz.offene_spuren import uid


def evidence():
    # Synthetischer Unit-Test-Datensatz: keine ausgestellte Freigabe.
    digest = lambda text: hashlib.sha256(text.encode()).hexdigest()
    return {"schemaVersion": "1.0.0", "claim": "offene.unit.probe", "verfahren": "regeltest",
            "geltungsbereich": {"kandidat": "a" * 40, "ziel": "synthetische Unit-Probe",
                                "ausfuehrungsort": "adapter", "population": "synthetisch",
                                "laufzeitversion": "Unit-Probe", "geraeteklasse": "keine Hardware",
                                "eingabeart": "ereignis-json", "pruefsatz": "offene-unit-probe",
                                "auswertungseinheit": "ein synthetischer Fall",
                                "bedingungen": ["Kein Freigabebeleg"], "ausschluesse": ["Alle realen Kinder"],
                                "digestArtefakt": digest("synthetisches Unit-Artefakt")},
            "ergebnis": "passed",
            "herkunft": {"zeitpunkt": "2026-11-22T09:00:00Z", "pruefidentitaet": "offener-unit-test",
                         "laufId": uid("unit-run"), "digestPruefsatz": digest("Unit-Fall"),
                         "digestRegeln": digest("Unit-Regel"), "digestBericht": digest("Unit-Bericht")},
            "fallzahlen": {"erwartet": 1, "ausgefuehrt": 1, "bestanden": 1, "gescheitert": 0,
                           "unentschieden": 0, "uebersprungen": 0},
            "berichtstext": "Synthetischer Validator-Test; kein authentisierter Beleg."}


class SchemaTests(unittest.TestCase):
    def assert_code(self, code, action):
        with self.assertRaises(ContractError) as ctx:
            action()
        self.assertEqual(ctx.exception.code, code)

    def test_three_schemas_are_valid_2020_12(self):
        for name in ["ereignis", "beweisregel", "belegstatus"]:
            Draft202012Validator.check_schema(load_json(CONTRACTS / (name + ".schema.json")))
            self.assertIsInstance(validator(name), Draft202012Validator)

    def test_root_entrypoints_resolve_to_versioned_contracts_offline(self):
        resources = []
        for path in CONTRACTS.glob("*.schema.json"):
            data = load_json(path)
            resources.append((data["$id"], Resource.from_contents(data)))
        registry = Registry().with_resources(resources)
        sample = load_json(CONTRACTS / "spuren" / "antwort-15.json")["events"][0]
        schema = load_json(CONTRACTS.parent / "ereignis.schema.json")
        Draft202012Validator(schema, registry=registry, format_checker=FormatChecker()).validate(sample)

    def test_all_payloads_are_typed_closed_and_required(self):
        examples = {}
        for path in (CONTRACTS / "spuren").glob("*.json"):
            for event in load_json(path)["events"]:
                examples[event["type"]] = event
        for typ, sample in examples.items():
            with self.subTest(type=typ, mutation="empty"):
                event = deepcopy(sample); event["payload"] = {}
                self.assert_code("schema", lambda: validate_schema("ereignis", event))
            with self.subTest(type=typ, mutation="unknown_property"):
                event = deepcopy(sample); event["payload"]["unvereinbart"] = True
                self.assert_code("schema", lambda: validate_schema("ereignis", event))

    def test_uuid_format_canonical_and_not_nil(self):
        event = load_json(CONTRACTS / "spuren" / "antwort-15.json")["events"][0]
        for value in ["", "kein-uuid", "00000000-0000-0000-0000-000000000000", uid("UPPER").upper()]:
            with self.subTest(value=value):
                event["streamId"] = value
                self.assert_code("schema", lambda: validate_schema("ereignis", event))

    def test_date_time_format_is_enforced(self):
        event = load_json(CONTRACTS / "spuren" / "antwort-15.json")["events"][0]
        for value in ["2026-11-22", "2026-11-22T09:00:00", "2026-02-30T09:00:00Z"]:
            event["occurredAt"] = value
            self.assert_code("schema", lambda: validate_schema("ereignis", event))

    def test_missing_format_plugin_fails_closed(self):
        validator.cache_clear()
        try:
            with patch("produkt.werkzeuge.referenz.contracts.FormatChecker") as factory:
                factory.return_value.checkers = {"uuid": object()}
                self.assert_code("format_dependency_missing", lambda: validator("ereignis"))
        finally:
            validator.cache_clear()

    def test_candidate_empty_is_rejected(self):
        event = load_json(CONTRACTS / "spuren" / "antwort-15.json")["events"][0]
        for key in event["candidate"]:
            altered = deepcopy(event); altered["candidate"][key] = " "
            self.assert_code("schema", lambda: validate_schema("ereignis", altered))

    def test_boolean_not_integer_answer(self):
        event = load_json(CONTRACTS / "spuren" / "antwort-15.json")["events"][2]
        event["payload"]["value"] = True
        self.assert_code("schema", lambda: validate_schema("ereignis", event))

    def test_nonfinite_json_is_rejected(self):
        event = load_json(CONTRACTS / "spuren" / "lesart-16.json")["events"][2]
        event["payload"]["confidence"] = float("nan")
        self.assert_code("not_json", lambda: validate_schema("ereignis", event))
        with patch.object(Path, "open", return_value=io.StringIO('{"value": NaN}')):
            self.assert_code("not_json", lambda: load_json("synthetic.json"))

    def test_duplicate_json_keys_are_rejected_before_decoding(self):
        with patch.object(Path, "open", return_value=io.StringIO('{"a": 1, "a": 2}')):
            self.assert_code("duplicate_json_key", lambda: load_json("synthetic.json"))

    def test_all_none_both_required_and_all_nonempty(self):
        for key in ["all", "none"]:
            rule = load_rules()[0]
            rule["logic"]["requires"].pop(key)
            self.assert_code("schema", lambda: validate_schema("beweisregel", rule))
        rule = load_rules()[0]; rule["logic"]["requires"]["all"] = []
        self.assert_code("schema", lambda: validate_schema("beweisregel", rule))

    def test_all_none_overlap_is_rejected(self):
        rules = load_rules(); rules[0]["logic"]["requires"]["none"] = ["observation.valid"]
        self.assert_code("contradictory_rule", lambda: validate_rules(rules))

    def test_validity_guards_cannot_be_omitted(self):
        rules = load_rules(); rules[0]["logic"]["requires"]["all"].remove("observation.valid")
        self.assert_code("missing_validity_guard", lambda: validate_rules(rules))

    def test_duplicate_fact_rejected(self):
        rule = load_rules()[0]; rule["logic"]["requires"]["all"].append("observation.valid")
        self.assert_code("schema", lambda: validate_schema("beweisregel", rule))

    def test_unknown_fact_cannot_be_silently_false(self):
        rules = load_rules(); rules[0]["logic"]["requires"]["all"].append("invented.fact")
        self.assert_code("schema", lambda: validate_rules(rules))

    def test_three_identical_kinds_do_not_meet_required_cases(self):
        rule = load_rules()[0]
        for case in rule["boundary"]["counterexamples"]:
            case["expected"] = "must_claim"
        self.assert_code("schema", lambda: validate_schema("beweisregel", rule))

    def test_same_trace_cannot_be_three_required_cases(self):
        rules = load_rules()
        cases = rules[0]["boundary"]["counterexamples"]
        for case in cases:
            case["traceRef"] = cases[0]["traceRef"]
        self.assert_code("duplicate_counterexample", lambda: validate_rules(rules))

    def test_trace_reference_cannot_escape_public_catalogue(self):
        rule = load_rules()[0]; rule["boundary"]["counterexamples"][0]["traceRef"] = "../../outside.json"
        self.assert_code("schema", lambda: validate_schema("beweisregel", rule))

    def test_fallback_requires_own_rule(self):
        rules = [rule for rule in load_rules() if rule["claimId"] != "attempt.result.correct"]
        self.assert_code("fallback_without_rule", lambda: validate_rules(rules))

    def test_fallback_cycles_fail_closed(self):
        rules = load_rules()
        rules[0]["boundary"]["wording"]["fallback"] = rules[0]["claimId"]
        self.assert_code("fallback_cycle", lambda: validate_rules(rules))

    def test_duplicate_claim_and_rule_are_rejected(self):
        rules = load_rules()
        self.assert_code("duplicate_rule", lambda: validate_rules(rules + [deepcopy(rules[0])]))
        rules[-1]["claimId"] = rules[0]["claimId"]
        self.assert_code("duplicate_claim", lambda: validate_rules(rules))

    def test_empty_rules_are_rejected(self):
        self.assert_code("rules_empty", lambda: validate_rules([]))

    def test_placeholders_cannot_be_marked_verified_sources(self):
        rule = load_rules()[0]; rule["target"]["references"][0]["quellenstatus"] = "geprueft"
        self.assert_code("schema", lambda: validate_schema("beweisregel", rule))

    def test_historical_v0_bytes_are_unchanged(self):
        digests = {
            "belegstatus.schema.json": "c0799f7c17ff259fadebb0333ca505e0dd1c403e356f34e59e922b15368363ef",
            "beweisregel.schema.json": "3049c63d431e25bd08d052d800c7677c2ff283d5dfa88e70134dca7ac8b03eff",
            "ereignis.schema.json": "a245c88be05c50b532874510acbe183622808fdebf8ca41b1f087188d18f7246",
            "beispiele/spur-korrigierte-fehllesung.json": "ca36c023fd089800708b06ab31036e5308c77f3554a6baf1370769f2d7b40706",
            "beispiele/sum15.result.json": "f759164909c6ca70fa1998e65a8bea39cf708248d9f3b250c1baff8efd58e83c",
            "beispiele/sum15.ten.json": "04f9788dcb75a4048b41d58f9c8b4d9fb52ab0b582bdcb9cccc6d2849d898d83",
        }
        for path, expected in digests.items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((CONTRACTS.parent / "v0" / path).read_bytes()).hexdigest(), expected)

    def test_historical_v0_gap_remains_demonstrable_not_retroactively_green(self):
        schema = load_json(CONTRACTS.parent / "v0" / "belegstatus.schema.json")
        old = {"claim": "offene.probe", "verfahren": "none", "ergebnis": "passed",
               "geltungsbereich": {"kandidat": "", "ausfuehrungsort": "keiner", "population": "keine"},
               "herkunft": {"zeitpunkt": "2026-11-22T09:00:00Z", "pruefidentitaet": ""}}
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(old)
        self.assert_code("schema", lambda: validate_schema("belegstatus", old))


class LogicTests(unittest.TestCase):
    def test_complete_three_valued_truth_table(self):
        expected = {
            (Truth.TRUE, Truth.TRUE): Truth.TRUE, (Truth.TRUE, Truth.FALSE): Truth.FALSE,
            (Truth.TRUE, Truth.UNKNOWN): Truth.UNKNOWN, (Truth.FALSE, Truth.TRUE): Truth.FALSE,
            (Truth.FALSE, Truth.FALSE): Truth.FALSE, (Truth.FALSE, Truth.UNKNOWN): Truth.FALSE,
            (Truth.UNKNOWN, Truth.TRUE): Truth.UNKNOWN, (Truth.UNKNOWN, Truth.FALSE): Truth.FALSE,
            (Truth.UNKNOWN, Truth.UNKNOWN): Truth.UNKNOWN,
        }
        for pair in itertools.product(Truth, repeat=2):
            self.assertEqual(conjunction(list(pair)), expected[pair])
        self.assertEqual(negate(Truth.UNKNOWN), Truth.UNKNOWN)
        self.assertEqual(negate(Truth.FALSE), Truth.TRUE)
        self.assertEqual(negate(Truth.TRUE), Truth.FALSE)

    def test_none_requires_known_false_not_absence(self):
        rule = {"logic": {"requires": {"all": ["shown"], "none": ["help"]}}}
        self.assertEqual(decide(rule, {"shown": Truth.TRUE}), "undecidable")
        self.assertEqual(decide(rule, {"shown": Truth.TRUE, "help": Truth.FALSE}), "must_claim")
        self.assertEqual(decide(rule, {"shown": Truth.TRUE, "help": Truth.TRUE}), "must_not_claim")
        self.assertEqual(decide(rule, {"shown": Truth.UNKNOWN, "help": Truth.TRUE}), "must_not_claim")

    def test_catalogue_matches_schema_exactly(self):
        facts = load_json(CONTRACTS / "beweisregel.schema.json")["properties"]["logic"]["properties"]["requires"]["properties"]["all"]["items"]["enum"]
        self.assertEqual(set(facts), set(FACTS))


class EvidenceTests(unittest.TestCase):
    def reject(self, data, code="schema", **kwargs):
        with self.assertRaises(ContractError) as ctx:
            validate_evidence(data, **kwargs)
        self.assertEqual(ctx.exception.code, code)

    def test_positive_structure_and_external_bindings(self):
        row = evidence()
        bindings = {"digestArtefakt": row["geltungsbereich"]["digestArtefakt"],
                    **{k: row["herkunft"][k] for k in ["digestPruefsatz", "digestRegeln", "digestBericht"]}}
        validate_evidence(row, expected_candidate="a" * 40, expected_count=1, expected_digests=bindings)

    def test_passed_none_rejected(self):
        row = evidence(); row["verfahren"] = "none"; self.reject(row)

    def test_empty_candidate_rejected(self):
        row = evidence(); row["geltungsbereich"]["kandidat"] = ""; self.reject(row)

    def test_each_missing_digest_rejected(self):
        for section, key in [("geltungsbereich", "digestArtefakt"), ("herkunft", "digestPruefsatz"),
                             ("herkunft", "digestRegeln"), ("herkunft", "digestBericht")]:
            with self.subTest(key=key):
                row = evidence(); del row[section][key]; self.reject(row)

    def test_invalid_digest_rejected(self):
        row = evidence(); row["herkunft"]["digestBericht"] = "kein-digest"; self.reject(row)

    def test_missing_execution_identity_rejected(self):
        for field in ["laufId", "pruefidentitaet", "zeitpunkt"]:
            row = evidence(); del row["herkunft"][field]; self.reject(row)

    def test_all_scope_fields_required_for_execution(self):
        for field in evidence()["geltungsbereich"]:
            row = evidence(); del row["geltungsbereich"][field]; self.reject(row)

    def test_zero_cases_cannot_pass(self):
        row = evidence()
        row["fallzahlen"] = {key: 0 for key in row["fallzahlen"]}
        self.reject(row)

    def test_skipped_job_cannot_pass(self):
        row = evidence(); row["fallzahlen"]["uebersprungen"] = 1; self.reject(row)

    def test_missing_counts_cannot_pass(self):
        row = evidence(); del row["fallzahlen"]; self.reject(row)

    def test_inconsistent_count_sums_rejected(self):
        row = evidence(); row["fallzahlen"]["erwartet"] = 2; self.reject(row, "count_mismatch")
        row = evidence(); row["fallzahlen"]["ausgefuehrt"] = 2; self.reject(row, "count_mismatch")

    def test_failed_or_inconclusive_cases_cannot_pass(self):
        for field in ["gescheitert", "unentschieden"]:
            row = evidence(); row["fallzahlen"][field] = 1; self.reject(row)

    def test_foreign_candidate_does_not_reuse_green_report(self):
        self.reject(evidence(), "candidate_binding", expected_candidate="b" * 40)

    def test_foreign_artifact_or_rules_digest_rejected(self):
        for key in ["digestArtefakt", "digestPruefsatz", "digestRegeln", "digestBericht"]:
            self.reject(evidence(), "digest_binding", expected_digests={key: "b" * 64})

    def test_foreign_expected_count_rejected(self):
        self.reject(evidence(), "count_binding", expected_count=2)

    def test_open_none_is_allowed_but_not_a_pass(self):
        row = evidence(); row["verfahren"] = "none"; row["ergebnis"] = "open"
        row.pop("fallzahlen")
        for key in ["laufId", "digestPruefsatz", "digestRegeln", "digestBericht"]:
            del row["herkunft"][key]
        validate_evidence(row)
        self.assertNotEqual(row["ergebnis"], "passed")

    def test_open_outcome_does_not_satisfy_expected_execution_count(self):
        row = evidence(); row["ergebnis"] = "open"; row.pop("fallzahlen")
        self.reject(row, "count_binding", expected_count=1)
