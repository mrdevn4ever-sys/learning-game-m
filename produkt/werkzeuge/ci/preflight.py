"""Public development checks. Never issues a release verdict."""
from __future__ import annotations
import ast
import json
from pathlib import Path
import re
import subprocess
import sys

from jsonschema import Draft202012Validator
import yaml

ROOT = Path(__file__).resolve().parents[3]


def tracked_paths() -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / p.decode("utf-8") for p in raw.split(b"\0") if p]


def check_repository() -> dict:
    paths = tracked_paths()
    forbidden_suffixes = {".p8", ".p12", ".mobileprovision", ".ipa", ".zip", ".xcarchive", ".sqlite", ".db"}
    credential = re.compile(r"(?:gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{35,}|-----BEGIN (?:RSA |EC )?PRIVATE KEY-----)")
    counts = {"files": len(paths), "schemas": 0, "json": 0, "python": 0}
    for path in paths:
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() in forbidden_suffixes or path.name == ".env" or path.name.startswith(".env."):
            raise ValueError(f"Unzulaessiger Repository-Pfad: {rel}")
        if any(part.endswith(".xcarchive") or part in {"DerivedData", ".build"} for part in path.parts):
            raise ValueError(f"Buildartefakt im Repository: {rel}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if credential.search(text):
            raise ValueError(f"Credential-Muster gefunden (Wert unterdrueckt): {rel}")
        if path.suffix == ".json":
            document = json.loads(text)
            counts["json"] += 1
            if path.name.endswith(".schema.json"):
                Draft202012Validator.check_schema(document)
                counts["schemas"] += 1
        if path.suffix == ".py":
            ast.parse(text, filename=rel)
            counts["python"] += 1
        if path.suffix == ".swift":
            if "\u00df" in text:
                raise ValueError(f"Schweizer Schreibweise verletzt: {rel}")
            if re.search(r"\b(?:URLSession|NWConnection|WKWebView)\b", text):
                raise ValueError(f"Netzwerkgrenze der App verletzt: {rel}")
            if "RecognitionKit" in path.parts and re.search(r"\bimport\s+(?:TaskEngine|LearningEngine|ContentPacks|CurriculumKit)\b", text):
                raise ValueError(f"Erkennungsabhaengigkeit verletzt: {rel}")
    if counts["schemas"] < 3:
        raise ValueError("Pflichtschemas fehlen")
    rights = (ROOT / "docs/rechteverzeichnis.md").read_text(encoding="utf-8")
    if len([line for line in rights.splitlines() if line.startswith("|")]) <= 2:
        raise ValueError("Rechteinventar ist noch leer")
    if not (ROOT / "produkt/Packages/Package.swift").is_file():
        raise ValueError("Swift-Package fehlt")
    workflow = yaml.load((ROOT / ".github/workflows/development.yml").read_text(), Loader=yaml.BaseLoader)
    if set(workflow["on"]) != {"pull_request", "merge_group", "push"}:
        raise ValueError("Unerwartete Workflow-Ausloeser")
    if workflow.get("permissions") != {"contents": "read"}:
        raise ValueError("Entwicklungs-CI verlangt zu viele Rechte")
    raw_workflow = (ROOT / ".github/workflows/development.yml").read_text()
    if re.search(r"secrets\s*[.\[]|upload-artifact|pull_request_target", raw_workflow):
        raise ValueError("Privilegierter Zugriff/Artefakt-Upload in oeffentlicher Entwicklungs-CI")
    return counts


def main() -> None:
    print(json.dumps(check_repository(), sort_keys=True))
    for directory in ("produkt/werkzeuge/ci/tests", "produkt/werkzeuge/referenz/tests"):
        subprocess.run([sys.executable, "produkt/werkzeuge/ci/run_suite.py", directory], cwd=ROOT, check=True)
    print("Oeffentlicher Entwicklungs-Preflight bestanden; kein Freigabebeleg.")


if __name__ == "__main__":
    main()
