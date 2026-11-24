"""Ausfuehrung des offenen Entwicklungskatalogs, keine Schlussabnahme."""
from collections import Counter

from .contracts import CONTRACTS, ContractError, load_json, load_rules, require
from .engine import evaluate_trace


def check_open_corpus() -> dict:
    rules = load_rules()
    claims = {rule["claimId"] for rule in rules}
    paths = sorted((CONTRACTS / "spuren").glob("*.json"))
    negatives = sorted((CONTRACTS / "ungueltig").glob("*.json"))
    require(len(paths) >= 20, "corpus_too_small", "Mindestens 20 offene Ereignisspuren")
    counts = Counter()
    by_claim = {claim: Counter() for claim in sorted(claims)}
    traces = {}
    for path in paths:
        row = load_json(path)
        require(row["id"] == path.stem and row["id"] not in traces,
                "trace_identity", path.name)
        require(set(row["expected"]) == claims, "expectations_incomplete", path.name)
        report = evaluate_trace(row["events"], rules)
        require(report["decisions"] == row["expected"], "decision_mismatch", path.name)
        require({c["claimId"] for c in report["claims"]}
                == {c for c, result in row["expected"].items() if result == "must_claim"},
                "claim_mismatch", path.name)
        traces[row["id"]] = row
        counts.update(row["expected"].values())
        for claim, result in row["expected"].items():
            by_claim[claim][result] += 1
    for claim, results in by_claim.items():
        require(set(results) == {"must_claim", "must_not_claim", "undecidable"},
                "missing_required_case", claim)
    for rule in rules:
        for case in rule["boundary"]["counterexamples"]:
            name = case["traceRef"].removeprefix("spuren/").removesuffix(".json")
            require(name in traces, "missing_counterexample", name)
            require(traces[name]["expected"][rule["claimId"]] == case["expected"],
                    "counterexample_mismatch", name)
    for path in negatives:
        row = load_json(path)
        try:
            evaluate_trace(row["events"], rules)
        except ContractError as error:
            require(error.code == row["expectedError"], "wrong_rejection", path.name)
        else:
            raise ContractError("invalid_trace_accepted", path.name)
    return {"scope": "offene eigene Entwicklungsregression, keine unabhaengige Abnahme",
            "validTraces": len(paths), "invalidTracesRejected": len(negatives),
            "rules": len(rules), "decisions": sum(counts.values()),
            "outcomes": dict(sorted(counts.items())),
            "byClaim": {claim: dict(sorted(results.items())) for claim, results in by_claim.items()},
            "curriculumSourceStatus": "offen"}
