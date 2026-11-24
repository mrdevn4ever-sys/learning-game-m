"""Validate native development counts and select a real compatible iPad."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def select_ipad(document: dict, sdk: str) -> str:
    match = re.fullmatch(r"(\d+)\.(\d+)(?:\.\d+)?", sdk.strip())
    if not match:
        raise ValueError("SDK-Version nicht parsebar")
    ceiling = tuple(map(int, match.groups()))
    candidates = []
    for runtime, devices in document.get("devices", {}).items():
        version = re.search(r"\.iOS-(\d+)-(\d+)", runtime)
        if not version:
            continue
        numbers = tuple(map(int, version.groups()))
        if numbers[0] < 27 or numbers > ceiling:
            continue
        for device in devices:
            if (device.get("isAvailable") is True and
                    str(device.get("name", "")).startswith("iPad") and
                    re.fullmatch(r"[0-9A-Fa-f-]{36}", str(device.get("udid", "")))):
                candidates.append((numbers, device["name"], device["udid"]))
    if not candidates:
        raise ValueError("Kein verfuegbarer kompatibler iPad-Simulator")
    return sorted(candidates)[-1][2]


def validate_xunit(path: Path) -> dict:
    root = ET.parse(path).getroot()
    cases = root.findall(".//testcase")
    if root.tag == "testcase":
        cases = [root]
    if not cases or any(c.find(tag) is not None for c in cases for tag in ("failure", "error", "skipped")):
        raise ValueError("Native Unit-Tests leer, fehlgeschlagen oder uebersprungen")
    declarations = [root] if root.tag == "testsuite" else root.findall("testsuite")
    if not declarations or sum(int(s.attrib.get("tests", "0")) for s in declarations) != len(cases):
        raise ValueError("Native Testfallzahl stimmt nicht mit Deklaration ueberein")
    return {"executed": len(cases), "passed": True}


def validate_xcresult(summary: dict) -> dict:
    keys = ("totalTestCount", "passedTests", "failedTests", "skippedTests")
    if any(type(summary.get(k)) is not int for k in keys):
        raise ValueError("Unbekanntes xcresult-Summaryformat")
    if (summary["totalTestCount"] <= 0 or summary["failedTests"] != 0 or
            summary["skippedTests"] != 0 or summary["passedTests"] != summary["totalTestCount"]):
        raise ValueError("UI-Pflichtlauf nicht vollstaendig bestanden")
    return {"executed": summary["totalTestCount"], "passed": True}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("kind", choices=["simulator", "xunit", "xcresult"])
    p.add_argument("path", type=Path)
    p.add_argument("--sdk")
    a = p.parse_args()
    if a.kind == "xunit":
        print(json.dumps(validate_xunit(a.path)))
    elif a.kind == "xcresult":
        print(json.dumps(validate_xcresult(json.loads(a.path.read_text()))))
    else:
        print(select_ipad(json.loads(a.path.read_text()), a.sdk or ""))
