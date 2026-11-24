"""Synthetic reporter mutations, not fabricated native execution evidence."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from produkt.werkzeuge.ci.native_evidence import validate_xunit, validate_xcresult, xunit_counts
from produkt.werkzeuge.ci.snapshot import contract


class BoundCountsTests(unittest.TestCase):
    def good_xml(self):
        return '<testsuites><testsuite tests="43" failures="0" errors="0" skipped="0">' + ''.join(
            f'<testcase name="{name}()"/>' for name in contract()["tests"]["packages"]["names"]) + '</testsuite></testsuites>'

    def validate_xml(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.xml"
            path.write_text(text, encoding="utf-8")
            return validate_xunit(path, contract()["tests"]["packages"])

    def test_all_43_xunit_identities_required(self):
        self.assertEqual(self.validate_xml(self.good_xml()), {"expected": 43, "executed": 43, "passed": True})

    def test_self_consistent_single_case_not_a_substitute(self):
        with self.assertRaises(ValueError): self.validate_xml('<testsuite tests="1"><testcase name="one"/></testsuite>')

    def test_self_consistent_missing_case_rejected(self):
        name = contract()["tests"]["packages"]["names"][0]
        xml = self.good_xml().replace('tests="43"', 'tests="42"').replace(f'<testcase name="{name}()"/>', '')
        with self.assertRaises(ValueError): self.validate_xml(xml)

    def test_suite_errors_without_failed_cases_rejected(self):
        for attr in ("failures", "errors", "skipped"):
            with self.subTest(attr=attr), self.assertRaises(ValueError):
                self.validate_xml(self.good_xml().replace(f'{attr}="0"', f'{attr}="1"'))

    def test_suite_error_element_rejected(self):
        with self.assertRaises(ValueError): self.validate_xml(self.good_xml().replace('</testsuite>', '<error/></testsuite>'))

    def test_case_error_element_rejected(self):
        with self.assertRaises(ValueError): self.validate_xml(self.good_xml().replace('/>', '><error/></testcase>', 1))

    def test_duplicate_and_foreign_identity_rejected(self):
        names = contract()["tests"]["packages"]["names"]
        for replacement in (names[1], "foreign"):
            with self.subTest(replacement=replacement), self.assertRaises(ValueError): self.validate_xml(self.good_xml().replace(names[0], replacement))

    def test_declared_count_mismatch_rejected(self):
        with self.assertRaises(ValueError): self.validate_xml(self.good_xml().replace('tests="43"', 'tests="44"'))

    def test_disabled_case_rejected(self):
        with self.assertRaises(ValueError): self.validate_xml(self.good_xml().replace('<testcase ', '<testcase status="notrun" ', 1))

    def test_failure_counts_remain_observable(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "failed.xml"
            path.write_text(self.good_xml().replace('/>', '><failure/></testcase>', 1))
            self.assertEqual(xunit_counts(path), {"observedCases": 43, "failedCases": 1, "skippedCases": 0})

    def xc_good(self):
        groups = contract()["tests"]
        summary = {"totalTestCount": 9, "passedTests": 9, "failedTests": 0, "skippedTests": 0,
                   "result": "Passed", "testFailures": []}
        tree = {"testNodes": [{"nodeType": "Test Plan", "result": "Passed", "children": [
            {"nodeType": "Test Case", "name": name + "()", "result": "Passed"}
            for lane in ("swiftdata", "ui") for name in groups[lane]["names"]]}]}
        return summary, tree, groups

    def test_4_swiftdata_and_5_ui_separately(self):
        self.assertEqual(validate_xcresult(*self.xc_good()),
            {"swiftdata": {"expected": 4, "executed": 4, "passed": True}, "ui": {"expected": 5, "executed": 5, "passed": True}})

    def test_self_consistent_missing_xcresult_count_rejected(self):
        summary, tree, groups = self.xc_good()
        with self.assertRaises(ValueError): validate_xcresult(summary | {"totalTestCount": 8, "passedTests": 8}, tree, groups)

    def test_xcresult_suite_failure_with_positive_counts_rejected(self):
        summary, tree, groups = self.xc_good()
        for delta in [{"result": "Failed"}, {"testFailures": [{"message": "suite setup failed"}]}, {"expectedFailures": 1}]:
            with self.subTest(delta=delta), self.assertRaises(ValueError): validate_xcresult(summary | delta, tree, groups)

    def test_tree_required_not_only_sum(self):
        summary, _, groups = self.xc_good()
        with self.assertRaises(ValueError): validate_xcresult(summary, {}, groups)

    def test_missing_swiftdata_with_positive_summary_rejected(self):
        summary, tree, groups = self.xc_good()
        tree["testNodes"][0]["children"] = tree["testNodes"][0]["children"][4:]
        with self.assertRaises(ValueError): validate_xcresult(summary, tree, groups)

    def test_duplicate_ui_cannot_replace_unit(self):
        summary, tree, groups = self.xc_good()
        cases = tree["testNodes"][0]["children"]
        cases[0] = cases[-1]
        with self.assertRaises(ValueError): validate_xcresult(summary, tree, groups)

    def test_tree_suite_failure_rejected(self):
        summary, tree, groups = self.xc_good()
        tree["testNodes"][0]["result"] = "Failed"
        with self.assertRaises(ValueError): validate_xcresult(summary, tree, groups)

    def test_tree_skip_failure_notrun_rejected(self):
        summary, tree, groups = self.xc_good()
        for result in ("Skipped", "Failed", "Not Run", "Expected Failure"):
            changed = copy.deepcopy(tree)
            changed["testNodes"][0]["children"][0]["result"] = result
            with self.subTest(result=result), self.assertRaises(ValueError): validate_xcresult(summary, changed, groups)

    def test_python_skip_expected_failure_and_suite_error_rejected(self):
        for decorator, body in [("@unittest.skip('synthetic')", "pass"), ("@unittest.expectedFailure", "self.fail('synthetic')"), ("", "raise RuntimeError('synthetic')")]:
            with self.subTest(decorator=decorator), tempfile.TemporaryDirectory() as tmp:
                directory = Path(tmp)
                (directory / "test_negative.py").write_text(
                    f"import unittest\nclass Probe(unittest.TestCase):\n    {decorator}\n    def test_case(self):\n        {body}\n")
                report = directory / "result.json"
                runner = Path(__file__).resolve().parents[1] / "run_suite.py"
                result = subprocess.run([sys.executable, str(runner), str(directory), "--report", str(report)], capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(json.loads(report.read_text())["passed"])
