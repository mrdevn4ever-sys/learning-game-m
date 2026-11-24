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
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "result.xml"
            p.write_text('<testsuite tests="1"><testcase name="one"/></testsuite>')
            self.assertEqual(validate_xunit(p)["executed"], 1)
            for xml in ['<testsuite tests="0"/>', '<testsuite tests="2"><testcase/></testsuite>',
                        '<testsuite tests="1"><testcase><skipped/></testcase></testsuite>',
                        '<testsuite tests="1"><testcase><failure/></testcase></testsuite>']:
                p.write_text(xml)
                with self.assertRaises(ValueError): validate_xunit(p)

    def test_xcresult_positive_and_mutations(self):
        good = {"totalTestCount": 3, "passedTests": 3, "failedTests": 0, "skippedTests": 0}
        self.assertEqual(validate_xcresult(good)["executed"], 3)
        for delta in [{"totalTestCount": 0}, {"skippedTests": 1}, {"failedTests": 1},
                      {"passedTests": 2}, {"passedTests": True}]:
            with self.assertRaises(ValueError): validate_xcresult(good | delta)

    def test_empty_python_suite_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): run_suite(tmp)


if __name__ == "__main__": unittest.main()
