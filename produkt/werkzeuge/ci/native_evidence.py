"""Validate native counts against a pre-run source-bound inventory."""
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
                    re.fullmatch(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", str(device.get("udid", "")))):
                candidates.append((numbers, device["name"], device["udid"]))
    if not candidates:
        raise ValueError("Kein verfuegbarer kompatibler iPad-Simulator")
    return sorted(candidates)[-1][2]


def expectation(group: dict) -> set[str]:
    names = group["names"]
    if (type(group["expected"]) is not int or group["expected"] <= 0 or
            len(names) != group["expected"] or len(set(names)) != len(names)):
        raise ValueError("Ungueltige vorab gebundene Erwartung")
    return set(names)


def case_name(value: str) -> str:
    # Native reporters append () and may qualify a function with a module/class.
    name = value.rsplit("/", 1)[-1].rsplit(".", 1)[-1]
    return name[:-2] if name.endswith("()") else name


def xunit_counts(path: Path) -> dict:
    root = ET.parse(path).getroot()
    cases = root.findall(".//testcase")
    return {"observedCases": len(cases),
            "failedCases": sum(any(c.find(t) is not None for t in ("failure", "error")) for c in cases),
            "skippedCases": sum(c.find("skipped") is not None for c in cases)}


def validate_xunit(path: Path, group: dict) -> dict:
    expected = expectation(group)
    root = ET.parse(path).getroot()
    cases = root.findall(".//testcase")
    if root.tag not in {"testsuites", "testsuite"} or len(cases) != len(expected):
        raise ValueError("Native Testfallzahl weicht von vorab gebundener Erwartung ab")
    if any(list(root.iter(tag)) for tag in ("failure", "error", "skipped")):
        raise ValueError("Native Tests/Suite fehlgeschlagen oder uebersprungen")
    suites = [s for s in root.iter() if s.tag in {"testsuites", "testsuite"}]
    if not any(s.tag == "testsuite" for s in suites):
        raise ValueError("Native Testsuite fehlt")
    for suite in suites:
        for attr in ("failures", "errors", "skipped", "disabled"):
            if int(suite.get(attr, "0")) != 0:
                raise ValueError("Suitefehler/Skip trotz positiver Testcases")
        declared = suite.get("tests")
        if (suite.tag == "testsuite" and declared is None) or (declared is not None and int(declared) != len(suite.findall(".//testcase"))):
            raise ValueError("Native Suite-Deklaration widerspruechlich")
    names = [case_name(c.get("name", "")) for c in cases]
    if len(set(names)) != len(names) or set(names) != expected:
        raise ValueError("Testidentitaeten fehlen, sind fremd oder doppelt")
    if any(c.get("status", "run") not in {"run", "passed"} for c in cases):
        raise ValueError("Testcase nicht ausgefuehrt")
    return {"expected": len(expected), "executed": len(cases), "passed": True}


def xcresult_cases(tree: dict) -> list[dict]:
    if not isinstance(tree.get("testNodes"), list) or not tree["testNodes"]:
        raise ValueError("xcresult-Testbaum fehlt")
    cases = []
    def walk(node: dict) -> None:
        if "result" in node and node["result"] != "Passed":
            raise ValueError("xcresult-Suite oder Test nicht bestanden")
        if node.get("nodeType") == "Test Case":
            if node.get("result") != "Passed":
                raise ValueError("xcresult-Testcase ohne Passed")
            cases.append(node)
        else:
            for child in node.get("children", []):
                walk(child)
    for node in tree["testNodes"]:
        walk(node)
    return cases


def validate_xcresult(summary: dict, tree: dict, groups: dict) -> dict:
    expected_groups = {lane: expectation(groups[lane]) for lane in ("swiftdata", "ui")}
    expected = set().union(*expected_groups.values())
    if len(expected) != sum(map(len, expected_groups.values())):
        raise ValueError("Mehrdeutige Lane-Erwartung")
    keys = ("totalTestCount", "passedTests", "failedTests", "skippedTests")
    if any(type(summary.get(k)) is not int for k in keys):
        raise ValueError("Unbekanntes xcresult-Summaryformat")
    if (summary["totalTestCount"] != len(expected) or summary["failedTests"] != 0 or
            summary["skippedTests"] != 0 or summary["passedTests"] != len(expected)):
        raise ValueError("iPad-Pflichtlauf nicht vollstaendig bestanden")
    if summary.get("testFailures") or summary.get("expectedFailures", 0) != 0 or summary.get("result", "Passed") != "Passed":
        raise ValueError("xcresult-Suitefehler trotz positiver Summen")
    cases = xcresult_cases(tree)
    names = [case_name(c.get("name", "")) for c in cases]
    if len(names) != len(expected) or len(set(names)) != len(names) or set(names) != expected:
        raise ValueError("xcresult-Testidentitaeten fehlen, sind fremd oder doppelt")
    return {lane: {"expected": len(values), "executed": len(set(names) & values), "passed": True}
            for lane, values in expected_groups.items()}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("kind", choices=["simulator", "xunit", "xcresult"])
    p.add_argument("path", type=Path)
    p.add_argument("--sdk")
    p.add_argument("--tree", type=Path)
    p.add_argument("--contract", type=Path, default=Path(__file__).with_name("native-contract.json"))
    a = p.parse_args()
    if a.kind == "simulator":
        print(select_ipad(json.loads(a.path.read_text()), a.sdk or ""))
    else:
        groups = json.loads(a.contract.read_text(encoding="utf-8"))["tests"]
        if a.kind == "xunit":
            print(json.dumps(validate_xunit(a.path, groups["packages"])))
        else:
            if a.tree is None:
                p.error("--tree erforderlich")
            print(json.dumps(validate_xcresult(json.loads(a.path.read_text()), json.loads(a.tree.read_text()), groups)))
