"""Synthetic subprocess fixtures exercise failure reporting, never native evidence."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from produkt.werkzeuge.ci import native_run


class NativeDriverTests(unittest.TestCase):
    def exercise(self, compile_code, malformed_xml=False):
        commands = []
        class Process:
            def __init__(self, args, **kwargs):
                commands.append(args)
                self.code = 0
                text = "synthetic fixture\n"
                if args == ["xcodebuild", "-version"]:
                    text = "Xcode 27.2\nBuild version synthetic\n"
                elif "--show-sdk-version" in args:
                    text = "27.2\n"
                elif args[:2] == ["swift", "test"]:
                    self.code = compile_code
                    text = "synthetic compiler failure\n" if compile_code else "synthetic tests\n"
                    if malformed_xml:
                        output = Path(args[args.index("--xunit-output") + 1]).with_name("swift-swift-testing.xml")
                        output.write_text("<broken")
                self.stdout = iter(text.splitlines(keepends=True))
            def wait(self):
                return self.code
        with tempfile.TemporaryDirectory() as tmp:
            env = {"RUNNER_TEMP": tmp, "GITHUB_RUN_ID": "synthetic", "GITHUB_RUN_ATTEMPT": "1",
                   "GITHUB_JOB": "fixture", "EXPECTED_SOURCE_SHA": "0" * 40, "DEVELOPER_DIR": "synthetic"}
            output = io.StringIO()
            with patch.dict(os.environ, env), patch.object(native_run.sys, "platform", "darwin"), \
                    patch.object(native_run, "verify"), patch.object(native_run, "git", return_value=("0" * 40).encode()), \
                    patch.object(native_run.platform, "platform", return_value="synthetic"), \
                    patch.object(native_run.subprocess, "Popen", Process), contextlib.redirect_stdout(output):
                result = native_run.main()
            report = json.loads((Path(tmp) / "chnobel-native-synthetic-1/diagnosis.json").read_text())
        self.assertEqual(result, 1)
        self.assertEqual(report["stages"], {"toolchain": "PASS", "packages": "FAIL", "ipad": "NOT RUN", "release": "NOT RUN"})
        self.assertFalse(any("simctl" in cmd or "test" in cmd and cmd[0] == "xcodebuild" for cmd in commands))
        self.assertEqual(report["validatedCounts"], {})
        return report

    def test_compile_failure_preserves_unrun_followup_gates(self):
        report = self.exercise(1)
        self.assertIsNone(report["observedCounts"]["packages"])

    def test_malformed_report_is_failure_not_missing_success(self):
        report = self.exercise(0, malformed_xml=True)
        self.assertEqual(report["observedCounts"]["packages"], {"unreadable": "ParseError"})
