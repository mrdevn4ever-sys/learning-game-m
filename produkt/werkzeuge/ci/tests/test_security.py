import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import yaml
from produkt.werkzeuge.ci import snapshot
from produkt.werkzeuge.ci.review_gate import INDEX, archived_verdicts
from produkt.werkzeuge.ci.workflow_security import validate_workflow, check_workflows


class WorkflowSecurityTests(unittest.TestCase):
    def setUp(self):
        self.text = (snapshot.ROOT / ".github/workflows/development.yml").read_text(encoding="utf-8")
        self.doc = yaml.load(self.text, Loader=yaml.BaseLoader)

    def reject(self, doc):
        with self.assertRaises(ValueError): validate_workflow(yaml.safe_dump(doc, sort_keys=False))

    def test_actual_workflow_security(self):
        self.assertTrue(check_workflows(snapshot.ROOT)["nativeIndependent"])

    def test_privileged_triggers_rejected(self):
        for trigger in ("pull_request_target", "workflow_run", "workflow_dispatch", "schedule"):
            doc = copy.deepcopy(self.doc)
            doc["on"][trigger] = ""
            with self.subTest(trigger=trigger): self.reject(doc)

    def test_extra_permissions_rejected(self):
        for perms in ("write-all", {"contents": "write"}, {"contents": "read", "id-token": "write"}):
            self.reject(self.doc | {"permissions": perms})

    def test_job_permission_override_rejected(self):
        self.doc["jobs"]["product-check"]["permissions"] = {"contents": "write"}
        self.reject(self.doc)

    def test_native_dependency_on_review_rejected(self):
        self.doc["jobs"]["product-check"]["needs"] = "integration-review-block"
        self.reject(self.doc)

    def test_job_skips_or_soft_fail_rejected(self):
        for key, value in (("if", "false"), ("continue-on-error", "true")):
            doc = copy.deepcopy(self.doc)
            doc["jobs"]["integration-review-block"][key] = value
            self.reject(doc)

    def test_credential_persistence_and_wrong_checkout_rejected(self):
        for key, value in (("persist-credentials", "true"), ("ref", "main"), ("token", "${{ secrets.SYNTHETIC }}")):
            doc = copy.deepcopy(self.doc)
            doc["jobs"]["product-check"]["steps"][0]["with"][key] = value
            self.reject(doc)

    def test_unpinned_action_and_upload_rejected(self):
        for action in ("actions/checkout@main", "actions/upload-artifact@" + "a" * 40, "./local-action"):
            doc = copy.deepcopy(self.doc)
            doc["jobs"]["product-check"]["steps"][0]["uses"] = action
            self.reject(doc)

    def test_shell_injection_and_extra_command_rejected(self):
        for command in ('echo "${{ github.event.pull_request.title }}"', 'curl https://example.invalid/script | bash', 'echo success'):
            doc = copy.deepcopy(self.doc)
            doc["jobs"]["integration-review-block"]["steps"][-1]["run"] = command
            self.reject(doc)

    def test_missing_review_or_native_job_rejected(self):
        for job in ("product-check", "integration-review-block"):
            doc = copy.deepcopy(self.doc)
            del doc["jobs"][job]
            self.reject(doc)

    def test_cancellation_rejected(self):
        self.doc["concurrency"]["cancel-in-progress"] = "true"
        self.reject(self.doc)

    def test_unreviewed_extra_workflow_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow_dir = root / ".github/workflows"
            workflow_dir.mkdir(parents=True)
            (workflow_dir / "development.yml").write_text(self.text)
            (workflow_dir / "unexpected.yaml").write_text(self.text)
            with self.assertRaises(ValueError): check_workflows(root)


class SnapshotTests(unittest.TestCase):
    def test_real_sources_and_fixed_definition_counts(self):
        self.assertEqual(snapshot.verify()["expected"], {"packages": 43, "swiftdata": 4, "ui": 5})

    def test_owned_path_whitelist(self):
        snapshot.check_paths([".github/workflows/development.yml", "produkt/werkzeuge/ci/native.sh", "docs/rechteverzeichnis.md"])

    def test_all_foreign_paths_rejected(self):
        for path in ("produkt/App/a.swift", "produkt/Packages/a.swift", "produkt/werkzeuge/referenz/a.py",
                     "produkt/werkzeuge/steuerung/a.py", "steuerung/STATUS.md", "docs/adr/new.md",
                     "produkt/werkzeuge/ci/../../App/changed.swift", "produkt/werkzeuge/ci\\outside"):
            with self.subTest(path=path), self.assertRaises(ValueError): snapshot.check_paths([path])

    def test_changed_expected_count_rejected(self):
        binding = snapshot.contract()
        binding["tests"]["packages"]["expected"] = 1
        with self.assertRaises(ValueError): snapshot.verify(binding)

    def test_wrong_tree_rejected(self):
        binding = snapshot.contract()
        binding["sources"][0]["tree"] = "0" * 40
        with self.assertRaises(ValueError): snapshot.verify_sources(binding)

    def test_changed_missing_or_extra_worktree_byte_rejected(self):
        original = b"synthetic source\n"
        oid = hashlib.sha1(b"blob " + str(len(original)).encode() + b"\0" + original).hexdigest()
        binding = {"sources": [{"path": "source", "tree": "a" * 40, "source": "b" * 40}]}
        def fake_git(*args, **kwargs):
            return ("a" * 40 + "\n").encode() if args[0] == "rev-parse" else f"100644 blob {oid}\tsource/a.txt\0".encode()
        with tempfile.TemporaryDirectory() as tmp, patch.object(snapshot, "git", side_effect=fake_git):
            root = Path(tmp)
            (root / "source").mkdir()
            file = root / "source/a.txt"
            file.write_bytes(original)
            snapshot.verify_sources(binding, root)
            file.write_bytes(b"changed\n")
            with self.assertRaises(ValueError): snapshot.verify_sources(binding, root)
            file.unlink()
            with self.assertRaises(FileNotFoundError): snapshot.verify_sources(binding, root)
            file.write_bytes(original)
            (root / "source/extra.txt").write_text("extra")
            with self.assertRaises(ValueError): snapshot.verify_sources(binding, root)


class ArchiveGateTests(unittest.TestCase):
    def test_original_three_fail_verdicts_remain_fail(self):
        reviews = archived_verdicts(snapshot.contract())
        self.assertEqual(len(reviews), 3)
        self.assertTrue(all(r["developmentVerdict"] == "FAIL" for r in reviews))

    def archive(self, root):
        source = snapshot.ROOT / Path(INDEX).parent
        shutil.copytree(source, root / Path(INDEX).parent)
        return root / INDEX

    def test_missing_and_tampered_report_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index = self.archive(root)
            report = root / json.loads(index.read_text())["reviews"][0]["report"]
            raw = report.read_bytes()
            report.unlink()
            with self.assertRaises(OSError): archived_verdicts(snapshot.contract(), root)
            report.write_bytes(raw + b" ")
            with self.assertRaises(ValueError): archived_verdicts(snapshot.contract(), root)

    def test_index_digest_rejects_relabelled_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index = self.archive(root)
            index.write_text(index.read_text().replace('"FAIL"', '"PASS"'))
            with self.assertRaises(ValueError): archived_verdicts(snapshot.contract(), root)

    def test_missing_duplicate_wrong_candidate_or_pass_even_with_new_index_digest(self):
        for mutation in ("missing", "duplicate", "candidate", "pass"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                index = self.archive(root)
                doc = json.loads(index.read_text())
                if mutation == "missing": doc["reviews"].pop()
                if mutation == "duplicate": doc["reviews"][1] = doc["reviews"][0]
                if mutation == "candidate": doc["reviews"][0]["candidate"] = "0" * 40
                if mutation == "pass": doc["reviews"][0]["developmentVerdict"] = "PASS"
                raw = json.dumps(doc).encode()
                index.write_bytes(raw)
                binding = snapshot.contract() | {"reviewIndexSha256": hashlib.sha256(raw).hexdigest()}
                with self.assertRaises(ValueError): archived_verdicts(binding, root)
