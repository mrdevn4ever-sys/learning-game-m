"""Reproduzierbares Xcode-Projekt, nur Python-Standardbibliothek.

Aus dem Repository: python produkt/App/Tools/generate_project.py --check
Ohne --check werden ausschliesslich die beiden Projektdateien erneuert.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

APP = Path(__file__).resolve().parents[1]
PRODUCTS = ["CoreDomain", "ObservationLog", "TaskEngine", "LearningEngine", "EvidenceKit", "InputKit", "RecognitionKit"]


def identifier(name: str) -> str:
    return hashlib.sha256(name.encode()).hexdigest()[:24].upper()


def project() -> dict:
    objects = {}

    def add(symbol, isa, **values):
        key = identifier(symbol)
        assert key not in objects
        objects[key] = {"isa": isa, **values}
        return key

    source_refs = {}
    source_builds = {}
    target_files = {
        "Chnobel": sorted(APP.glob("Chnobel/**/*.swift")),
        "ChnobelTests": sorted(APP.glob("ChnobelTests/*.swift")),
        "ChnobelUITests": sorted(APP.glob("ChnobelUITests/*.swift")),
    }
    for target, paths in target_files.items():
        source_refs[target], source_builds[target] = [], []
        for path in paths:
            relative = path.relative_to(APP).as_posix()
            ref = add("file:" + relative, "PBXFileReference", lastKnownFileType="sourcecode.swift", path=relative, sourceTree="SOURCE_ROOT")
            source_refs[target].append(ref)
            source_builds[target].append(add("build:" + relative, "PBXBuildFile", fileRef=ref))

    info = add("info", "PBXFileReference", lastKnownFileType="text.plist.xml", path="Chnobel/Info.plist", sourceTree="SOURCE_ROOT")
    privacy = add("privacy", "PBXFileReference", lastKnownFileType="text.xml", path="Chnobel/PrivacyInfo.xcprivacy", sourceTree="SOURCE_ROOT")
    privacy_build = add("build:privacy", "PBXBuildFile", fileRef=privacy)
    package = add("package", "XCLocalSwiftPackageReference", relativePath="../Packages")
    products = {}
    target_ids = {name: identifier("target:" + name) for name in target_files}
    for target in target_files:
        suffix, filetype = (".app", "wrapper.application") if target == "Chnobel" else (".xctest", "wrapper.cfbundle")
        products[target] = add("product:" + target, "PBXFileReference", explicitFileType=filetype, includeInIndex="0", path=target + suffix, sourceTree="BUILT_PRODUCTS_DIR")

    groups = []
    for target in target_files:
        children = source_refs[target] + ([info, privacy] if target == "Chnobel" else [])
        groups.append(add("group:" + target, "PBXGroup", children=children, name=target, sourceTree="<group>"))
    products_group = add("products", "PBXGroup", children=list(products.values()), name="Products", sourceTree="<group>")
    main_group = add("main-group", "PBXGroup", children=groups + [products_group], sourceTree="<group>")

    base_settings = {
        "ALWAYS_SEARCH_USER_PATHS": "NO", "CLANG_ENABLE_MODULES": "YES",
        "CODE_SIGNING_ALLOWED": "NO", "DEVELOPMENT_TEAM": "", "ENABLE_USER_SCRIPT_SANDBOXING": "YES",
        "IPHONEOS_DEPLOYMENT_TARGET": "18.0", "SDKROOT": "iphoneos",
        "SUPPORTED_PLATFORMS": "iphoneos iphonesimulator", "SUPPORTS_MACCATALYST": "NO",
        "SWIFT_VERSION": "6.0", "SWIFT_STRICT_CONCURRENCY": "complete", "TARGETED_DEVICE_FAMILY": "2",
    }

    def configurations(name, extra):
        ids = []
        for config in ["Debug", "Release"]:
            settings = dict(base_settings)
            settings.update(extra)
            settings.update({
                "SWIFT_OPTIMIZATION_LEVEL": "-Onone" if config == "Debug" else "-O",
                "DEBUG_INFORMATION_FORMAT": "dwarf" if config == "Debug" else "dwarf-with-dsym",
                "ENABLE_TESTABILITY": "YES" if config == "Debug" else "NO",
                "SWIFT_ACTIVE_COMPILATION_CONDITIONS": ["$(inherited)", "DEBUG"] if config == "Debug" else ["$(inherited)"],
            })
            ids.append(add("config:" + name + config, "XCBuildConfiguration", buildSettings=settings, name=config))
        return add("configs:" + name, "XCConfigurationList", buildConfigurations=ids, defaultConfigurationIsVisible="0", defaultConfigurationName="Release")

    project_config = configurations("project", {})
    for target in target_files:
        linked = PRODUCTS if target == "Chnobel" else (["CoreDomain", "ObservationLog", "TaskEngine"] if target == "ChnobelTests" else [])
        dependencies, frameworks = [], []
        for product in linked:
            dependency = add("dependency:" + target + product, "XCSwiftPackageProductDependency", package=package, productName=product)
            dependencies.append(dependency)
            frameworks.append(add("framework:" + target + product, "PBXBuildFile", productRef=dependency))
        sources = add("sources:" + target, "PBXSourcesBuildPhase", buildActionMask="2147483647", files=source_builds[target], runOnlyForDeploymentPostprocessing="0")
        framework_phase = add("frameworks:" + target, "PBXFrameworksBuildPhase", buildActionMask="2147483647", files=frameworks, runOnlyForDeploymentPostprocessing="0")
        resources = add("resources:" + target, "PBXResourcesBuildPhase", buildActionMask="2147483647", files=[privacy_build] if target == "Chnobel" else [], runOnlyForDeploymentPostprocessing="0")
        bundle_ids = {
            "Chnobel": "ch.chnobel.app",
            "ChnobelTests": "ch.chnobel.app.tests",
            "ChnobelUITests": "ch.chnobel.app.uitests",
        }
        settings = {
            "PRODUCT_NAME": "$(TARGET_NAME)", "PRODUCT_BUNDLE_IDENTIFIER": bundle_ids[target],
            "LD_RUNPATH_SEARCH_PATHS": ["$(inherited)", "@executable_path/Frameworks", "@loader_path/Frameworks"],
        }
        target_dependencies = []
        if target == "Chnobel":
            settings.update({"GENERATE_INFOPLIST_FILE": "NO", "INFOPLIST_FILE": "Chnobel/Info.plist", "PRODUCT_MODULE_NAME": "Chnobel"})
            product_type = "com.apple.product-type.application"
        else:
            settings.update({"GENERATE_INFOPLIST_FILE": "YES"})
            proxy = add("proxy:" + target, "PBXContainerItemProxy", containerPortal=identifier("project"), proxyType="1", remoteGlobalIDString=target_ids["Chnobel"], remoteInfo="Chnobel")
            target_dependencies.append(add("target-dependency:" + target, "PBXTargetDependency", target=target_ids["Chnobel"], targetProxy=proxy))
            if target == "ChnobelTests":
                settings.update({"BUNDLE_LOADER": "$(TEST_HOST)", "TEST_HOST": "$(BUILT_PRODUCTS_DIR)/Chnobel.app/Chnobel"})
                product_type = "com.apple.product-type.bundle.unit-test"
            else:
                settings["TEST_TARGET_NAME"] = "Chnobel"
                product_type = "com.apple.product-type.bundle.ui-testing"
        add("target:" + target, "PBXNativeTarget", buildConfigurationList=configurations(target, settings), buildPhases=[sources, framework_phase, resources], buildRules=[], dependencies=target_dependencies, name=target, packageProductDependencies=dependencies, productName=target, productReference=products[target], productType=product_type)

    add("project", "PBXProject", attributes={"BuildIndependentTargetsInParallel": "YES", "LastUpgradeCheck": "1600", "TargetAttributes": {target_ids[name]: {"CreatedOnToolsVersion": "16.0", **({"TestTargetID": target_ids["Chnobel"]} if name != "Chnobel" else {})} for name in target_files}}, buildConfigurationList=project_config, compatibilityVersion="Xcode 14.0", developmentRegion="de_CH", hasScannedForEncodings="0", knownRegions=["de_CH", "Base"], mainGroup=main_group, packageReferences=[package], productRefGroup=products_group, projectDirPath="", projectRoot="", targets=list(target_ids.values()))
    return {"archiveVersion": "1", "classes": {}, "objectVersion": "56", "objects": objects, "rootObject": identifier("project")}


def openstep(value, level=0):
    indent = "\t" * level
    if isinstance(value, dict):
        return "{\n" + "".join("\t" * (level + 1) + json.dumps(k) + " = " + openstep(v, level + 1) + ";\n" for k, v in value.items()) + indent + "}"
    if isinstance(value, list):
        return "(\n" + "".join("\t" * (level + 1) + openstep(v, level + 1) + ",\n" for v in value) + indent + ")"
    return json.dumps(value, ensure_ascii=False)


def scheme():
    root = ET.Element("Scheme", LastUpgradeVersion="1600", version="1.3")

    def reference(parent, target):
        ET.SubElement(parent, "BuildableReference", BuildableIdentifier="primary", BlueprintIdentifier=identifier("target:" + target), BuildableName=target + (".app" if target == "Chnobel" else ".xctest"), BlueprintName=target, ReferencedContainer="container:Chnobel.xcodeproj")

    action = ET.SubElement(root, "BuildAction", parallelizeBuildables="YES", buildImplicitDependencies="YES")
    entries = ET.SubElement(action, "BuildActionEntries")
    for target in ["Chnobel", "ChnobelTests", "ChnobelUITests"]:
        enabled = "YES" if target == "Chnobel" else "NO"
        entry = ET.SubElement(entries, "BuildActionEntry", buildForTesting="YES", buildForRunning=enabled, buildForProfiling=enabled, buildForArchiving=enabled, buildForAnalyzing="YES")
        reference(entry, target)
    test = ET.SubElement(root, "TestAction", buildConfiguration="Debug", selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB", selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB", shouldUseLaunchSchemeArgsEnv="YES")
    testables = ET.SubElement(test, "Testables")
    for target in ["ChnobelTests", "ChnobelUITests"]:
        reference(ET.SubElement(testables, "TestableReference", skipped="NO", parallelizable="NO"), target)
    launch = ET.SubElement(root, "LaunchAction", buildConfiguration="Debug", selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB", selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB", launchStyle="0", useCustomWorkingDirectory="NO", ignoresPersistentStateOnLaunch="NO", debugDocumentVersioning="YES", allowLocationSimulation="NO")
    reference(ET.SubElement(launch, "BuildableProductRunnable", runnableDebuggingMode="0"), "Chnobel")
    profile = ET.SubElement(root, "ProfileAction", buildConfiguration="Release", shouldUseLaunchSchemeArgsEnv="YES", savedToolIdentifier="", useCustomWorkingDirectory="NO", debugDocumentVersioning="YES")
    reference(ET.SubElement(profile, "BuildableProductRunnable", runnableDebuggingMode="0"), "Chnobel")
    ET.SubElement(root, "AnalyzeAction", buildConfiguration="Debug")
    ET.SubElement(root, "ArchiveAction", buildConfiguration="Release", revealArchiveInOrganizer="YES")
    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"


def outputs():
    return {
        APP / "Chnobel.xcodeproj/project.pbxproj": "// !$*UTF8*$!\n" + openstep(project()) + "\n",
        APP / "Chnobel.xcodeproj/xcshareddata/xcschemes/Chnobel.xcscheme": scheme(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, text in outputs().items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                raise SystemExit("FAIL: Projektdatei weicht ab: " + str(path))
            print("PASS:", path.relative_to(APP))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
            print("Erzeugt:", path.relative_to(APP))


if __name__ == "__main__":
    main()
