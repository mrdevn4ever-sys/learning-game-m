"""Lokale v1-Schema- und Vertragsvalidierung; keine Netzabrufe."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry
from referencing.exceptions import NoSuchResource

CONTRACTS = Path(__file__).resolve().parents[2] / "vertraege" / "v1"
VERSION = "1.0.0"
FACTS = (
    "attempt.submitted", "observation.valid", "observation.complete",
    "answer.value.15", "answer.deviation", "board.ten.child", "board.ten.app",
    "board.doubles.child", "board.path.child", "history.ten.child",
    "support.ten.before", "support.doubles.before",
)


class ContractError(ValueError):
    """Ungueltige Eingabe: kein Teilbericht und keine positiven Aussagen."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise ContractError(code, detail)


def canonical(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False)
    except (ValueError, TypeError) as error:
        raise ContractError("not_json", "Nur endliche JSON-Werte erlaubt") from error


def _pairs(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate_json_key", key)
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise ContractError("not_json", f"Nichtendlicher Wert: {value}")


def load_json(path: str | Path) -> Any:
    try:
        with Path(path).open(encoding="utf-8") as handle:
            return json.load(handle, object_pairs_hook=_pairs, parse_constant=_constant)
    except json.JSONDecodeError as error:
        raise ContractError("not_json", f"Zeile {error.lineno}, Spalte {error.colno}") from error


def _offline(uri: str):
    raise NoSuchResource(ref=uri)


@lru_cache(maxsize=3)
def validator(name: str) -> Draft202012Validator:
    require(name in {"ereignis", "beweisregel", "belegstatus"}, "schema_name", name)
    schema = load_json(CONTRACTS / f"{name}.schema.json")
    Draft202012Validator.check_schema(schema)
    checker = FormatChecker()
    require({"uuid", "date-time"} <= set(checker.checkers), "format_dependency_missing",
            "requirements.txt vollstaendig installieren; Formate duerfen nicht stumm entfallen")
    return Draft202012Validator(schema, format_checker=checker,
                               registry=Registry(retrieve=_offline))


def validate_schema(name: str, value: Any) -> None:
    canonical(value)
    error = next(validator(name).iter_errors(value), None)
    if error:
        path = "/".join(str(part) for part in error.absolute_path) or "$"
        raise ContractError("schema", f"{name}/{path}: {error.message}")


def validate_rules(rules: list[dict]) -> None:
    require(isinstance(rules, list) and bool(rules), "rules_empty", "Regeln fehlen")
    ids, claims = set(), set()
    for rule in rules:
        validate_schema("beweisregel", rule)
        require(rule["id"] not in ids, "duplicate_rule", rule["id"])
        require(rule["claimId"] not in claims, "duplicate_claim", rule["claimId"])
        ids.add(rule["id"])
        claims.add(rule["claimId"])
        req = rule["logic"]["requires"]
        require(not set(req["all"]) & set(req["none"]), "contradictory_rule", rule["id"])
        # Diese Regeln duerfen gueltige Beobachtungen und den Abschluss nicht umgehen.
        require({"observation.valid", "attempt.submitted"} <= set(req["all"]),
                "missing_validity_guard", rule["id"])
        refs = [case["traceRef"] for case in rule["boundary"]["counterexamples"]]
        require(len(refs) == len(set(refs)), "duplicate_counterexample", rule["id"])
    fallbacks = {rule["claimId"]: rule["boundary"]["wording"]["fallback"] for rule in rules}
    for claim in claims:
        seen = set()
        current = claim
        while current != "insufficient_observation":
            require(current in fallbacks, "fallback_without_rule", current)
            require(current not in seen, "fallback_cycle", current)
            seen.add(current)
            current = fallbacks[current]


def load_rules() -> list[dict]:
    rules = [load_json(path) for path in sorted((CONTRACTS / "regeln").glob("*.json"))]
    validate_rules(rules)
    return rules


def validate_evidence(evidence: dict, *, expected_candidate: str | None = None,
                      expected_digests: dict[str, str] | None = None,
                      expected_count: int | None = None) -> None:
    """Struktur/Bindung, NICHT Authentisierung oder Releasefreigabe.

    Erwartungswerte muessen vom Aufrufer kommen, nie aus dem Bericht selbst.
    """
    validate_schema("belegstatus", evidence)
    scope = evidence["geltungsbereich"]
    provenance = evidence["herkunft"]
    if "fallzahlen" in evidence:
        counts = evidence["fallzahlen"]
        require(counts["ausgefuehrt"] == counts["bestanden"] + counts["gescheitert"]
                + counts["unentschieden"], "count_mismatch", "Ausgefuehrte Faelle")
        require(counts["erwartet"] == counts["ausgefuehrt"] + counts["uebersprungen"],
                "count_mismatch", "Erwartete Faelle")
        if evidence["ergebnis"] == "passed":
            require(counts["erwartet"] == counts["bestanden"], "count_mismatch", "passed")
    if expected_candidate is not None:
        require(scope["kandidat"] == expected_candidate, "candidate_binding", "Fremder Kandidat")
    if expected_count is not None:
        require(evidence.get("fallzahlen", {}).get("erwartet") == expected_count,
                "count_binding", "Fremder Nenner")
    for key, digest in (expected_digests or {}).items():
        require(key in {"digestArtefakt", "digestPruefsatz", "digestRegeln", "digestBericht"},
                "digest_key", key)
        actual = scope.get(key) if key == "digestArtefakt" else provenance.get(key)
        require(actual == digest, "digest_binding", key)
