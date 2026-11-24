import os
from pathlib import Path
import subprocess
import sys

from produkt.werkzeuge.steuerung import Controller
from produkt.werkzeuge.steuerung.contracts import canonical, parse_json, sha
from support import ROOT, StoreCase
from test_gates import policy_data, report_data


class CliTests(StoreCase):
    def cli(self, *args):
        env = os.environ.copy()
        env.update(TEMP="F:/ChnobelRuntime/steuerung", TMP="F:/ChnobelRuntime/steuerung",
                   TMPDIR="F:/ChnobelRuntime/steuerung", PYTHONPYCACHEPREFIX="F:/ChnobelRuntime/cache",
                   PYTHONUTF8="1")
        return subprocess.run([sys.executable, "-m", "produkt.werkzeuge.steuerung", *map(str, args)],
                              cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", timeout=30)

    def test_original_preview_and_passive_import_preserve_all_dependencies(self):
        original = ROOT / "steuerung/auftraege/phase-0.json"
        before = original.read_bytes()
        expected = parse_json(before)
        preview = self.cli("preview")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        value = parse_json(preview.stdout)
        self.assertEqual(value["jobs"], expected["auftraege"])
        self.assertEqual(value["count"], len(expected["auftraege"]))
        self.assertEqual(value["source_digest"], sha(before))
        path = self.folder / "original-passive.sqlite"
        imported = self.cli("import", "--database", path, "--expected-digest", value["source_digest"], "--now", 100)
        self.assertEqual(imported.returncode, 0, imported.stderr)
        self.assertEqual(parse_json(imported.stdout)["count"], len(expected["auftraege"]))
        shown = self.cli("show", "--database", path)
        self.assertEqual(shown.returncode, 0, shown.stderr)
        rows = {row["id"]: row for row in parse_json(shown.stdout)["jobs"]}
        self.assertEqual(set(rows), {row["id"] for row in expected["auftraege"]})
        for source in expected["auftraege"]:
            row = rows[source["id"]]
            self.assertEqual(row["dependencies"], source["abhaengig"])
            self.assertEqual(row["state"], source["zustand"])
            self.assertEqual((row["revision"], row["attempts"], row["fencing_token"]), (1, 0, 0))
        self.assertEqual(original.read_bytes(), before)

    def test_wrong_import_digest_never_creates_database(self):
        path = self.folder / "bad-import.sqlite"
        result = self.cli("import", "--database", path, "--expected-digest", "0" * 64, "--now", 100)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(path.exists())

    def test_cli_backup_restore_and_readonly_integrity(self):
        before = self.controller.show()
        check = self.cli("check", "--database", self.controller.path)
        self.assertEqual(check.returncode, 0, check.stderr)
        self.assertEqual(parse_json(check.stdout)["integrity"], "ok")
        backup = self.cli("backup", "--database", self.controller.path,
                          "--destination", self.folder / "cli-backup.sqlite")
        self.assertEqual(backup.returncode, 0, backup.stderr)
        value = parse_json(backup.stdout)
        restored_path = self.folder / "cli-restored.sqlite"
        result = self.cli("restore", "--source", value["path"], "--destination", restored_path,
                          "--expected-digest", value["digest"], "--fencing-floor", 0, "--now", 100)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(parse_json(result.stdout)["recovery_locked"])
        self.assertEqual(Controller(restored_path).show()["meta"]["recovery_locked"], "1")
        self.assertEqual(self.controller.show(), before)

    def test_cli_has_no_manual_status_completion_or_release_command(self):
        before = self.controller.show()
        for command in ("done", "set-state", "upload", "merge", "activate-restore"):
            with self.subTest(command=command):
                result = self.cli(command, "--database", self.controller.path)
                self.assertEqual(result.returncode, 2)
        self.assertEqual(self.controller.show(), before)

    def test_gate_cli_never_returns_release_success_for_local_reports(self):
        policy = policy_data()
        report = report_data(policy)
        policy_file, report_file = self.folder / "policy.json", self.folder / "report.json"
        policy_file.write_text(canonical(policy), encoding="utf-8")
        report_file.write_text(canonical(report), encoding="utf-8")
        result = self.cli("validate-report", "--policy", policy_file, "--report", report_file)
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertTrue(parse_json(result.stdout)["checks_valid"])
        self.assertFalse(parse_json(result.stdout)["release_authorized"])
        report["jobs"][0]["executed_cases"] = 0
        report_file.write_text(canonical(report), encoding="utf-8")
        result = self.cli("validate-report", "--policy", policy_file, "--report", report_file)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(parse_json(result.stdout)["checks_valid"])
