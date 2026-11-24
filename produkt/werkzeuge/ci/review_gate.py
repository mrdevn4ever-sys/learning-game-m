"""Deterministic integration veto for the three archived FAIL candidates."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from produkt.werkzeuge.ci.snapshot import ROOT, contract, verify

INDEX = "steuerung/gedaechtnis/pruefergebnisse/2026-11-24-code-reviews/index.json"


def archived_verdicts(binding: dict, root: Path = ROOT) -> list[dict]:
    raw = (root / INDEX).read_bytes()
    if hashlib.sha256(raw).hexdigest() != binding["reviewIndexSha256"]:
        raise ValueError("Archivierter Reviewindex veraendert")
    reviews = json.loads(raw)["reviews"]
    candidates = {s["source"] for s in binding["sources"]}
    if len(reviews) != 3 or {r["component"] for r in reviews} != {"steuerung", "referenz", "ipad"}:
        raise ValueError("Pflichtreview fehlt oder ist doppelt")
    if {r["candidate"] for r in reviews} != candidates:
        raise ValueError("Reviewkandidaten passen nicht zum Snapshot")
    output = []
    for review in reviews:
        path = root / review["report"]
        if not path.resolve().is_relative_to((root / Path(INDEX).parent).resolve()):
            raise ValueError("Reviewpfad verlaesst Archiv")
        raw_report = path.read_bytes()
        if hashlib.sha256(raw_report).hexdigest() != review["containerSha256"]:
            raise ValueError("Reviewcontainer-Digest abweichend")
        document = json.loads(raw_report)
        if document["encoding"] != "utf-8-lines" or not all(type(line) is str for line in document["lines"]):
            raise ValueError("Unbekanntes verlustfreies Reviewformat")
        content = "".join(document["lines"]).encode("utf-8")
        digest = hashlib.sha256(content).hexdigest()
        if digest != review["reportSha256"] or digest != document["contentSha256"]:
            raise ValueError("Originalreview-Digest abweichend")
        if (review["developmentVerdict"] != "FAIL" or review["releaseAuthorized"] is not False
                or review["candidate"] not in content.decode("utf-8") or b"FAIL" not in content):
            raise ValueError("Historisches FAIL fehlt oder wurde umetikettiert")
        output.append({key: review[key] for key in ("component", "candidate", "developmentVerdict", "reportSha256")})
    return output


def main() -> int:
    try:
        binding = contract()
        verify(binding)
        reviews = archived_verdicts(binding)
        print(json.dumps({"integrationBlocked": True, "reviews": reviews,
                          "releaseAuthorized": False, "nativeDiagnosisIndependent": True}, sort_keys=True))
        for review in reviews:
            print(f"::error::Integrationssperre {review['component']}: archiviertes FAIL fuer {review['candidate']}")
        return 1
    except (ValueError, KeyError, OSError) as exc:
        print(f"::error::Reviewbindung ungueltig: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
