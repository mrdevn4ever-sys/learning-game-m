import json
from pathlib import Path
import tempfile
import unittest
from produkt.werkzeuge.ci.native_evidence import select_ipad, validate_xunit, validate_xcresult
from produkt.werkzeuge.ci.run_suite import run_suite


class NativeEvidenceTests(unittest.TestCase):
    def document(self, available=True, name="iPad (A16)", runtime="27-2"):
        return {"devices": {"com.apple.CoreSimulator.SimRuntime.iOS-" + runtime: [
            {"name": name, "isAvailable": available, "udid": "12345678-1234-1234-1234-123456789abc"}]}}

    def test_real_ipad_selected(self):
        self.assertEqual(select_ipad(self.document(), "27.2"), "12345678-1234-1234-1234-123456789abc")

    def test_device_suffix_is_parseable(self):
        self.assertTrue(select_ipad(self.document(runtime="27-2-device"), "27.2"))

    def test_unavailable_rejected(self):
        with self.assertRaises(ValueError): select_ipad(self.document(available=False), "27.2")

    def test_iphone_not_ipad(self):
        with self.assertRaises(ValueError): select_ipad(self.document(name="iPhone 17"), "27.2")

    def test_newer_runtime_rejected(self):
        with self.assertRaises(ValueError): select_ipad(self.document(runtime="27-3"), "27.2")

    def test_missing_runtime_rejected(self):
        with self.assertRaises(ValueError): select_ipad({}, "27.2")

    def test_xunit_positive_and_mutations(self):
        from produkt.werkzeuge.ci.snapshot import contract
        group = contract()["tests"]["packages"]
        good = '<testsuite tests="43">' + ''.join(f'<testcase name="{n}()"/>' for n in group["names"]) + '</testsuite>'
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "result.xml"
            p.write_text(good)
            self.assertEqual(validate_xunit(p, group)["executed"], 43)
            for xml in ['<testsuite tests="0"/>', '<testsuite tests="2"><testcase/></testsuite>',
                        good.replace('/>', '><skipped/></testcase>', 1),
                        good.replace('/>', '><failure/></testcase>', 1)]:
                p.write_text(xml)
                with self.assertRaises(ValueError): validate_xunit(p, group)

    def test_xcresult_positive_and_mutations(self):
        from produkt.werkzeuge.ci.snapshot import contract
        groups = contract()["tests"]
        tree = {"testNodes": [{"nodeType": "Test Case", "name": n + "()", "result": "Passed"}
                              for lane in ("swiftdata", "ui") for n in groups[lane]["names"]]}
        good = {"totalTestCount": 9, "passedTests": 9, "failedTests": 0, "skippedTests": 0}
        self.assertEqual(validate_xcresult(good, tree, groups)["ui"]["executed"], 5)
        for delta in [{"totalTestCount": 0}, {"skippedTests": 1}, {"failedTests": 1},
                      {"passedTests": 8}, {"passedTests": True}]:
            with self.assertRaises(ValueError): validate_xcresult(good | delta, tree, groups)

    def test_empty_python_suite_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): run_suite(tmp)


if __name__ == "__main__": unittest.main()
