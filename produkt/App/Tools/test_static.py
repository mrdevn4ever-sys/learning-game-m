"""Negative Selbsttests der statischen Architektur-/Projektpruefung."""
import copy
import plistlib
import unittest
import xml.etree.ElementTree as ET

from generate_project import APP, project, scheme
from verify_static import AuditError, EXPECTED_GRAPH, check_graph, check_plists, check_project, check_scheme


class StaticGateTests(unittest.TestCase):
    def test_current_graph_is_allowed(self):
        check_graph(copy.deepcopy(EXPECTED_GRAPH))

    def test_recognition_cannot_import_task_engine(self):
        graph = copy.deepcopy(EXPECTED_GRAPH)
        graph["RecognitionKit"].append("TaskEngine")
        with self.assertRaises(AuditError):
            check_graph(graph)

    def test_input_cannot_transitively_leak_task_engine(self):
        graph = copy.deepcopy(EXPECTED_GRAPH)
        graph["InputKit"].append("TaskEngine")
        with self.assertRaises(AuditError):
            check_graph(graph)

    def test_unlisted_modules_are_rejected(self):
        graph = copy.deepcopy(EXPECTED_GRAPH)
        graph["Extra"] = []
        with self.assertRaises(AuditError):
            check_graph(graph)

    def test_current_project_is_connected(self):
        check_project(project())

    def test_dangling_project_reference_fails(self):
        model = project()
        model["objects"][model["rootObject"]]["mainGroup"] = "MISSING"
        with self.assertRaises(AuditError):
            check_project(model)

    def test_signing_cannot_be_enabled_silently(self):
        model = project()
        config = next(item for item in model["objects"].values() if item["isa"] == "XCBuildConfiguration")
        config["buildSettings"]["CODE_SIGNING_ALLOWED"] = "YES"
        with self.assertRaises(AuditError):
            check_project(model)

    def test_canonical_bundle_id_cannot_drift(self):
        model = project()
        config = next(item for item in model["objects"].values() if item["isa"] == "XCBuildConfiguration" and item["buildSettings"].get("PRODUCT_BUNDLE_IDENTIFIER") == "ch.chnobel.app")
        config["buildSettings"]["PRODUCT_BUNDLE_IDENTIFIER"] = "invalid.bundle"
        with self.assertRaises(AuditError):
            check_project(model)

    def test_swift_five_is_not_accepted(self):
        model = project()
        config = next(item for item in model["objects"].values() if item["isa"] == "XCBuildConfiguration")
        config["buildSettings"]["SWIFT_VERSION"] = "5.0"
        with self.assertRaises(AuditError):
            check_project(model)

    def test_privacy_manifest_must_be_a_resource(self):
        model = project()
        resources = next(item for item in model["objects"].values() if item["isa"] == "PBXResourcesBuildPhase" and item["files"])
        resources["files"] = []
        with self.assertRaises(AuditError):
            check_project(model)

    def test_remote_packages_fail(self):
        model = project()
        model["objects"]["REMOTE"] = {"isa": "XCRemoteSwiftPackageReference"}
        with self.assertRaises(AuditError):
            check_project(model)

    def test_ui_test_cannot_be_skipped(self):
        root = ET.fromstring(scheme())
        root.find("./TestAction/Testables/TestableReference").attrib["skipped"] = "YES"
        with self.assertRaises(AuditError):
            check_scheme(root)

    def test_camera_permission_is_not_accepted(self):
        info = plistlib.loads((APP / "Chnobel/Info.plist").read_bytes())
        privacy = plistlib.loads((APP / "Chnobel/PrivacyInfo.xcprivacy").read_bytes())
        check_plists(info, privacy)
        info["NSCameraUsageDescription"] = "not-authorized"
        with self.assertRaises(AuditError):
            check_plists(info, privacy)

    def test_tracking_is_not_accepted(self):
        info = plistlib.loads((APP / "Chnobel/Info.plist").read_bytes())
        privacy = plistlib.loads((APP / "Chnobel/PrivacyInfo.xcprivacy").read_bytes())
        privacy["NSPrivacyTracking"] = True
        with self.assertRaises(AuditError):
            check_plists(info, privacy)


if __name__ == "__main__":
    unittest.main()
