"""Quellpruefungen, keine Swift-Ausfuehrung und keine native Abnahme.

python produkt/App/Tools/verify_static.py
Optional: --swift-parser (tree-sitter und tree-sitter-swift nur im externen
Pruef-Environment installieren, nie als App-/Package-Abhaengigkeit).
"""
from __future__ import annotations

import argparse
import json
import plistlib
import re
from pathlib import Path
import xml.etree.ElementTree as ET

from generate_project import APP, PRODUCTS, identifier, outputs, project
from verify_repair import check_baseline, check_regressions, check_repair_sources, sources as repair_sources

PACKAGES = APP.parent / "Packages"
ROOT = APP.parents[1]
EXPECTED_GRAPH = {
    "CoreDomain": [],
    "ObservationLog": ["CoreDomain"],
    "TaskEngine": ["CoreDomain", "ObservationLog"],
    "LearningEngine": ["CoreDomain", "ObservationLog", "TaskEngine"],
    "EvidenceKit": ["CoreDomain", "ObservationLog", "LearningEngine"],
    "InputKit": [],
    "RecognitionKit": ["InputKit"],
}


class AuditError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AuditError(message)


def package_graph(text):
    graph = {}
    pattern = r'\.target\(name:\s*"([^"]+)"(?:,\s*dependencies:\s*\[([^\]]*)\])?\)'
    for name, dependencies in re.findall(pattern, text):
        require(name not in graph, "Doppeltes Package-Target")
        graph[name] = re.findall(r'"([^"]+)"', dependencies)
    return graph


def check_graph(graph):
    require(graph == EXPECTED_GRAPH, "Modulgrenzen weichen vom lokalen Entwicklungsvertrag ab")
    visited = set()

    def visit(name, stack):
        require(name in graph, "Unbekannte Modulabhaengigkeit")
        require(name not in stack, "Zyklische Modulabhaengigkeit")
        visited.add(name)
        for dependency in graph[name]:
            visit(dependency, stack + [name])

    visit("RecognitionKit", [])
    require(visited == {"RecognitionKit", "InputKit"}, "Erkennung erreicht fachlichen Kern")


def check_project(model):
    objects = model["objects"]
    require(model["rootObject"] in objects, "Projektwurzel fehlt")
    references = {"mainGroup", "productRefGroup", "buildConfigurationList", "productReference", "fileRef", "productRef", "package", "target", "targetProxy", "containerPortal", "remoteGlobalIDString"}
    lists = {"children", "buildConfigurations", "buildPhases", "dependencies", "targets", "packageReferences", "packageProductDependencies", "files"}
    for item in objects.values():
        for key in references & item.keys():
            require(item[key] in objects, "Nicht aufloesbare Xcode-Referenz: " + key)
        for key in lists & item.keys():
            require(all(reference in objects for reference in item[key]), "Nicht aufloesbare Xcode-Liste: " + key)
        require(item["isa"] not in {"XCRemoteSwiftPackageReference", "PBXShellScriptBuildPhase"}, "Remote-Package oder Build-Skript unerwartet")
        if item["isa"] == "XCBuildConfiguration":
            settings = item["buildSettings"]
            for key, expected in {"SWIFT_VERSION": "6.0", "SWIFT_STRICT_CONCURRENCY": "complete", "TARGETED_DEVICE_FAMILY": "2", "IPHONEOS_DEPLOYMENT_TARGET": "18.0", "CODE_SIGNING_ALLOWED": "NO", "DEVELOPMENT_TEAM": ""}.items():
                require(settings.get(key) == expected, "Build-Grenze verletzt: " + key)
        if item["isa"] == "PBXFileReference" and item["sourceTree"] == "SOURCE_ROOT":
            require((APP / item["path"]).is_file(), "Xcode-Datei fehlt: " + item["path"])
    targets = [item for item in objects.values() if item["isa"] == "PBXNativeTarget"]
    require({target["name"] for target in targets} == {"Chnobel", "ChnobelTests", "ChnobelUITests"}, "Unvollstaendige Targets")
    for target in targets:
        expected_bundle = {"Chnobel": "ch.chnobel.app", "ChnobelTests": "ch.chnobel.app.tests", "ChnobelUITests": "ch.chnobel.app.uitests"}[target["name"]]
        configurations = objects[target["buildConfigurationList"]]["buildConfigurations"]
        require(all(objects[key]["buildSettings"].get("PRODUCT_BUNDLE_IDENTIFIER") == expected_bundle for key in configurations), "Kanonische Bundle-ID stimmt nicht")
        phases = [objects[key] for key in target["buildPhases"]]
        source_phases = [phase for phase in phases if phase["isa"] == "PBXSourcesBuildPhase"]
        require(len(source_phases) == 1, "Quellenphase fehlt")
        paths = [objects[objects[key]["fileRef"]]["path"] for key in source_phases[0]["files"]]
        expected = {path.relative_to(APP).as_posix() for path in (APP / target["name"]).rglob("*.swift")}
        require(len(paths) == len(set(paths)) and set(paths) == expected and bool(paths), "Swift-Quellmitgliedschaft unvollstaendig")
    app = next(target for target in targets if target["name"] == "Chnobel")
    linked = {objects[key]["productName"] for key in app["packageProductDependencies"]}
    require(linked == set(PRODUCTS), "Package-Produkte fehlen im App-Target")
    resources = next(objects[key] for key in app["buildPhases"] if objects[key]["isa"] == "PBXResourcesBuildPhase")
    resource_paths = {objects[objects[key]["fileRef"]]["path"] for key in resources["files"]}
    require(resource_paths == {"Chnobel/PrivacyInfo.xcprivacy"}, "Privacy Manifest fehlt im Build")
    packages = [item for item in objects.values() if item["isa"] == "XCLocalSwiftPackageReference"]
    require(len(packages) == 1 and (APP / packages[0]["relativePath"]).resolve() == PACKAGES.resolve(), "Falscher lokaler Package-Pfad")


def check_plists(info, privacy):
    require(not any("UsageDescription" in key for key in info), "Unerwartete Permission")
    require("NSAppTransportSecurity" not in info, "Unerwartete Netzwerkausnahme")
    require(info.get("UIApplicationSceneManifest", {}).get("UIApplicationSupportsMultipleScenes") is False, "Mehrfenster-Schreibkonflikt nicht ausgeschlossen")
    require(len(info.get("UISupportedInterfaceOrientations~ipad", [])) == 4, "iPad-Orientierungen fehlen")
    require(privacy == {"NSPrivacyTracking": False, "NSPrivacyTrackingDomains": [], "NSPrivacyCollectedDataTypes": [], "NSPrivacyAccessedAPITypes": []}, "Privacy-Angaben unerwartet; Datenfluss neu pruefen")


def check_scheme(root):
    testables = root.findall("./TestAction/Testables/TestableReference")
    require(len(testables) == 2, "Testtargets fehlen im Scheme")
    require(all(item.attrib.get("skipped") == "NO" for item in testables), "Testtarget wird uebersprungen")
    names = {item.find("BuildableReference").attrib["BlueprintName"] for item in testables}
    require(names == {"ChnobelTests", "ChnobelUITests"}, "Falsche Testtargets im Scheme")
    for reference in root.findall(".//BuildableReference"):
        name = reference.attrib["BlueprintName"]
        require(reference.attrib["BlueprintIdentifier"] == identifier("target:" + name), "Falsche Target-ID im Scheme")


def syntax_checks(files):
    try:
        import tree_sitter
        import tree_sitter_swift
    except ImportError as error:
        raise AuditError("Swift-Grammatikparser fehlt im externen Pruef-Environment") from error
    parser = tree_sitter.Parser(tree_sitter.Language(tree_sitter_swift.language()))
    errors = []
    for path in files:
        data = path.read_bytes()
        tree = parser.parse(data)
        if tree.root_node.has_error:
            stack = [tree.root_node]
            while stack:
                node = stack.pop()
                if node.type == "ERROR" or node.is_missing:
                    errors.append(f"{path.relative_to(ROOT)}:{node.start_point.row + 1}:{node.start_point.column + 1} {node.type}")
                stack.extend(reversed(node.children))
    require(not errors, "Swift-Grammatikfehler (kein Typecheck):\n" + "\n".join(errors))
    return len(files)


def audit(use_parser=False):
    manifest = (PACKAGES / "Package.swift").read_text(encoding="utf-8")
    require(manifest.startswith("// swift-tools-version: 6.0"), "Swift-6-Manifest fehlt")
    require("swiftLanguageModes: [.v6]" in manifest, "Swift-6-Modus fehlt")
    require("dependencies: []" in manifest and ".package(" not in manifest, "Drittanbieter-Package gefunden")
    graph = package_graph(manifest)
    check_graph(graph)
    files = sorted([*PACKAGES.rglob("*.swift"), *APP.rglob("*.swift")])
    for module, dependencies in graph.items():
        sources = sorted((PACKAGES / "Sources" / module).glob("*.swift"))
        require(bool(sources), "Leeres Modul: " + module)
        for path in sources:
            text = path.read_text(encoding="utf-8")
            imports = set(re.findall(r"^import (\w+)", text, re.MULTILINE))
            require(imports <= set(dependencies) | {"Foundation"}, "Nicht deklarierter Import: " + str(path))
        tests = list((PACKAGES / "Tests" / (module + "Tests")).glob("*.swift"))
        require(tests and any("@Test" in path.read_text(encoding="utf-8") for path in tests), "Swift-Testing-Faelle fehlen: " + module)
    for path in files:
        text = path.read_text(encoding="utf-8")
        require("\u00df" not in text, "Schweizer Schreibweise verletzt")
        if "/Sources/" in path.as_posix() or "/Chnobel/" in path.as_posix():
            require(not re.search(r"\b(URLSession|URLRequest|NWConnection|UserDefaults|AVCaptureSession|SFSpeechRecognizer)\b|^import (Network|CoreML)\b", text, re.MULTILINE), "Unerwartete Netzwerk-/Erkennungs-/Privacy-API: " + str(path))
    for path, expected in outputs().items():
        require(path.is_file() and path.read_text(encoding="utf-8") == expected, "Projekt muss reproduzierbar erneuert werden: " + str(path))
    check_project(project())
    info = plistlib.loads((APP / "Chnobel/Info.plist").read_bytes())
    privacy = plistlib.loads((APP / "Chnobel/PrivacyInfo.xcprivacy").read_bytes())
    check_plists(info, privacy)
    check_scheme(ET.parse(APP / "Chnobel.xcodeproj/xcshareddata/xcschemes/Chnobel.xcscheme").getroot())
    swift_tests = sum(len(re.findall(r"@Test\b", path.read_text(encoding="utf-8"))) for path in (PACKAGES / "Tests").rglob("*.swift"))
    native_tests = sum(len(re.findall(r"@Test\b", path.read_text(encoding="utf-8"))) for path in (APP / "ChnobelTests").glob("*.swift"))
    ui_tests = sum(len(re.findall(r"func test\w+\(", path.read_text(encoding="utf-8"))) for path in (APP / "ChnobelUITests").glob("*.swift"))
    require(swift_tests > 0 and native_tests > 0 and ui_tests >= 4, "Leere oder unvollstaendige Testinventare")
    preserved = check_baseline()
    repair = check_repair_sources(repair_sources())
    regressions = check_regressions()
    parsed = syntax_checks(files) if use_parser else None
    return {
        "source_checks": "PASS", "module_count": len(graph), "swift_files": len(files),
        "repair_source_gates": repair, "unchanged_baseline_test_files": preserved,
        "repair_native_regressions": regressions,
        "swift_grammar_only": {"status": "PASS" if use_parser else "NOT RUN", "parsed_files": parsed},
        "prepared_tests_not_executed": {"swift_testing_package": swift_tests, "swift_data_native": native_tests, "xcuitest": ui_tests},
        "native_typecheck": "NOT RUN", "swift_test": "NOT RUN", "xcodebuild": "NOT RUN", "xcuitest": "NOT RUN",
        "scope": "statische Entwicklungspruefung; keine Phase-0-Abnahme",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--swift-parser", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = audit(args.swift_parser)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.report:
        require(not args.report.resolve().is_relative_to(ROOT.resolve()), "Pruefberichte gehoeren ausserhalb des Repositories")
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
