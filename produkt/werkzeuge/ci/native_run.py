"""Unsigned native diagnosis. Outputs stay on the runner; logs contain open tests only."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from produkt.werkzeuge.ci.snapshot import ROOT, contract, git, verify
from produkt.werkzeuge.ci.native_evidence import select_ipad, validate_xunit, validate_xcresult, xunit_counts


def main() -> int:
    if sys.platform != "darwin":
        raise RuntimeError("Native Ausfuehrung verlangt macOS; kein Ersatzlauf")
    binding = contract()
    verify(binding)
    sha = git("rev-parse", "HEAD").decode().strip()
    if sha != os.environ["EXPECTED_SOURCE_SHA"]:
        raise ValueError("Workflow- und Checkout-SHA weichen ab")
    work = Path(os.environ["RUNNER_TEMP"]) / ("chnobel-native-" + os.environ["GITHUB_RUN_ID"] + "-" + os.environ["GITHUB_RUN_ATTEMPT"])
    work.mkdir(exist_ok=False)
    report = {"checkoutSha": sha, "runId": os.environ["GITHUB_RUN_ID"],
              "attempt": os.environ["GITHUB_RUN_ATTEMPT"], "job": os.environ["GITHUB_JOB"],
              "platform": platform.platform(), "releaseAuthorized": False,
              "expected": {k: v["expected"] for k, v in binding["tests"].items()},
              "stages": {k: "NOT RUN" for k in ("toolchain", "packages", "ipad", "release")},
              "validatedCounts": {}, "observedCounts": {"packages": None, "ipad": None}}
    phase = "toolchain"

    def run(name: str, args: list[str], check: bool = True) -> tuple[int, str]:
        print("::group::" + name, flush=True)
        print("COMMAND " + json.dumps(args), flush=True)
        output = []
        with (work / (name + ".log")).open("w", encoding="utf-8") as log:
            process = subprocess.Popen(args, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       text=True, encoding="utf-8", errors="replace")
            for line in process.stdout:
                print(line, end="", flush=True)
                log.write(line)
                output.append(line)
            code = process.wait()
        print(f"EXIT {name} {code}", flush=True)
        print("::endgroup::", flush=True)
        if code and check:
            raise subprocess.CalledProcessError(code, args)
        return code, "".join(output)

    code = 1
    try:
        _, xcode = run("xcode-version", ["xcodebuild", "-version"])
        if not xcode.startswith("Xcode 27.2\n"):
            raise ValueError("Ausgewaehltes Xcode entspricht nicht 27.2")
        _, sdk = run("simulator-sdk", ["xcrun", "--sdk", "iphonesimulator", "--show-sdk-version"])
        if sdk.strip() != "27.2":
            raise ValueError("Ausgewaehltes Simulator-SDK entspricht nicht 27.2")
        run("swift-version", ["swift", "--version"])
        report["toolchain"] = {"xcode": xcode.strip(), "sdk": sdk.strip(), "developerDir": os.environ["DEVELOPER_DIR"]}
        report["stages"][phase] = "PASS"

        phase = "packages"
        run("swift-test", ["swift", "test", "--package-path", "produkt/Packages",
                           "--scratch-path", str(work / "PackageBuild"), "--xunit-output", str(work / "swift.xml")])
        # SwiftPM preserves XCTest output separately; these 43 definitions use Swift Testing.
        report["validatedCounts"]["packages"] = validate_xunit(work / "swift-swift-testing.xml", binding["tests"]["packages"])
        report["stages"][phase] = "PASS"

        phase = "ipad"
        _, devices = run("simulators", ["xcrun", "simctl", "list", "devices", "available", "-j"])
        udid = select_ipad(json.loads(devices), sdk.strip())
        report["simulatorUdid"] = udid
        common = ["xcodebuild", "-project", "produkt/App/Chnobel.xcodeproj", "-scheme", "Chnobel"]
        test_code, _ = run("ipad-test", common + ["-destination", "id=" + udid,
            "-derivedDataPath", str(work / "DerivedData"), "-resultBundlePath", str(work / "iPad.xcresult"),
            "CODE_SIGNING_ALLOWED=NO", "-parallel-testing-enabled", "NO", "test"], check=False)
        # Extract actual summaries even if xcodebuild failed; never upload the bundle or build.
        for kind in ("summary", "tests"):
            extract_code, text = run("xcresult-" + kind, ["xcrun", "xcresulttool", "get", "test-results", kind,
                                                         "--path", str(work / "iPad.xcresult")], check=False)
            if extract_code == 0:
                (work / ("ipad-" + kind + ".json")).write_text(text, encoding="utf-8")
        if test_code:
            raise subprocess.CalledProcessError(test_code, "xcodebuild test")
        summary = json.loads((work / "ipad-summary.json").read_text())
        tree = json.loads((work / "ipad-tests.json").read_text())
        report["validatedCounts"].update(validate_xcresult(summary, tree, binding["tests"]))
        report["stages"][phase] = "PASS"

        phase = "release"
        run("release-build", common + ["-configuration", "Release", "-destination", "generic/platform=iOS Simulator",
            "-derivedDataPath", str(work / "ReleaseDerivedData"), "CODE_SIGNING_ALLOWED=NO", "build"])
        report["stages"][phase] = "PASS"
        code = 0
    except Exception as exc:
        report["stages"][phase] = "FAIL"
        report["failure"] = {"stage": phase, "type": type(exc).__name__, "message": str(exc)}
        print(f"::error::Native Diagnose scheitert in {phase}: {exc}", flush=True)
    finally:
        for lane, path in (("packages", work / "swift-swift-testing.xml"), ("ipad", work / "ipad-summary.json")):
            if path.is_file():
                try:
                    report["observedCounts"][lane] = xunit_counts(path) if lane == "packages" else {
                        k: v for k, v in json.loads(path.read_text()).items()
                        if k in {"totalTestCount", "passedTests", "failedTests", "skippedTests", "result"}}
                except Exception as exc:
                    report["observedCounts"][lane] = {"unreadable": type(exc).__name__}
        report["logDigests"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(work.glob("*.log"))}
        (work / "diagnosis.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("NATIVE_DIAGNOSIS " + json.dumps(report, sort_keys=True), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
