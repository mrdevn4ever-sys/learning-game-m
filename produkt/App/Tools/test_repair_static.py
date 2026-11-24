"""Echte Python-Negativtests fuer Quellgates, nicht fuer Swift-Semantik."""
import json
from pathlib import Path
import unittest

from verify_repair import (
    DOMAIN, EVENT, LEARNING, NOTEBOOK, ROOT, STORE, TASK,
    REGRESSION_FILES, RepairAuditError, check_baseline, check_regressions, check_repair_sources, sources,
)


class RepairStaticGateTests(unittest.TestCase):
    def reject_mutation(self, path, old, new):
        data = sources()
        self.assertIn(old, data[path])
        data[path] = data[path].replace(old, new)
        with self.assertRaises(RepairAuditError):
            check_repair_sources(data)

    def test_current_source_wiring(self):
        self.assertEqual(check_repair_sources(sources())["swift_semantics"], "NOT RUN")

    def test_original_test_files_are_unchanged(self):
        self.assertEqual(check_baseline(), 10)

    def test_native_regression_inventory_is_not_execution(self):
        self.assertEqual(check_regressions()["execution"], "NOT RUN")

    def test_missing_new_native_case_fails(self):
        data = {path: (ROOT / path).read_text(encoding="utf-8") for path in REGRESSION_FILES}
        path = "produkt/Packages/Tests/LearningEngineTests/ActorAnchorTests.swift"
        data[path] = data[path].replace("@Test", "", 1)
        with self.assertRaises(RepairAuditError):
            check_regressions(data)

    def test_skipped_new_native_case_fails(self):
        data = {path: (ROOT / path).read_text(encoding="utf-8") for path in REGRESSION_FILES}
        path = "produkt/Packages/Tests/LearningEngineTests/ActorAnchorTests.swift"
        data[path] = data[path].replace("@Test", '@Test(.disabled("not-run"))', 1)
        with self.assertRaises(RepairAuditError):
            check_regressions(data)

    def test_weakened_existing_expectation_fails(self):
        baseline = json.loads((Path(__file__).parent / "repair-baseline.json").read_text(encoding="utf-8"))
        texts = {path: (ROOT / path).read_text(encoding="utf-8") for path in baseline["files"]}
        path = "produkt/Packages/Tests/LearningEngineTests/LearningTests.swift"
        texts[path] = texts[path].replace("report.tenWithoutHint == .yes", "report.tenWithoutHint != .no")
        with self.assertRaises(RepairAuditError):
            check_baseline(texts)

    def test_missing_sequence_must_use_gap_transition(self):
        self.reject_mutation(TASK, "if event.sequence != state.lastSequence + 1 { state.observeGap() }",
                             "if event.sequence != state.lastSequence + 1 { state.hasGap = true }")

    def test_explicit_gap_must_use_gap_transition(self):
        self.reject_mutation(TASK, "if condition == .gapDetected { state.observeGap() }",
                             "if condition == .gapDetected { state.hasGap = true }")

    def test_gap_cannot_keep_answer_current(self):
        self.reject_mutation(TASK, "answerCurrency = .unknown", "answerCurrency = .yes")

    def test_fresh_answer_must_reestablish_currency(self):
        self.reject_mutation(TASK, "state.answerCurrency = .yes", "state.answerCurrency = .unknown")

    def test_result_must_require_current_answer(self):
        self.reject_mutation(LEARNING, "let result: Truth = state.answerCurrency == .yes", "let result: Truth = true")

    def test_finish_ui_cannot_accept_unknown_answer(self):
        self.reject_mutation(NOTEBOOK, "session.state.answerCurrency != .yes", "session.state.answer == nil")

    def test_reading_requires_numeric_validation(self):
        self.reject_mutation(TASK, ", isDirectNumber(reading.text)", "")

    def test_correction_cannot_be_confirmation(self):
        self.reject_mutation(TASK, "(answer.origin == .confirmed) == (proposedValue == answer.value)", "true")

    def test_undo_replay_cannot_drop_actor_binding(self):
        self.reject_mutation(TASK, "event.actor == last.event.actor", "event.actor == .learner")

    def test_undo_helper_cannot_relabel_app_action(self):
        self.reject_mutation(TASK, ".actionUndone(eventID: move.event.id), actor: move.event.actor",
                             ".actionUndone(eventID: move.event.id), actor: .learner")

    def test_nine_six_cannot_reuse_two_token_hint(self):
        self.reject_mutation(TASK, "case (9, 6, 0): return .tenFromNineV1", "case (9, 6, 0): return .tenStep")

    def test_presentation_cannot_bypass_state_selection(self):
        self.reject_mutation(TASK, ".supportPresented(supportForState(state))", ".supportPresented(.tenStep)")

    def test_move_and_undo_cannot_leave_stale_help_visible(self):
        self.reject_mutation(TASK, "state.shownSupport = nil", "// alter Tipp bleibt stehen")

    def test_child_return_must_use_current_action_support(self):
        self.reject_mutation(TASK, "contributingMoves.map(\\.tenSupportBefore) + [supportBefore]",
                             "contributingMoves.map(\\.tenSupportBefore)")

    def test_undo_cannot_omit_anchor_update(self):
        data = sources()
        old = "state.anchorMaterialAction(event, supportBefore: before)"
        first = data[TASK].index(old)
        second = data[TASK].index(old, first + len(old))
        data[TASK] = data[TASK][:second] + data[TASK][second:].replace(old, "", 1)
        with self.assertRaises(RepairAuditError):
            check_repair_sources(data)

    def test_app_return_cannot_manufacture_new_history(self):
        self.reject_mutation(TASK, "if ownLayout, let anchor = retainedLearnerTenAnchor, anchor.positions == positions {",
                             "if ownLayout, let anchor = retainedLearnerTenAnchor, anchor.positions == positions { historicalTenAnchors.append(anchor)")

    def test_app_return_requires_exact_retained_positions(self):
        self.reject_mutation(TASK, "anchor.positions == positions", "true")

    def test_child_action_must_invalidate_suspended_anchor(self):
        self.reject_mutation(TASK, "retainedLearnerTenAnchor = nil", "// alter Anker bleibt")

    def test_old_local_format_is_not_silently_reinterpreted(self):
        self.reject_mutation(STORE, "localFormat == 1", "localFormat >= 0")

    def test_new_rule_revision_is_explicit(self):
        self.reject_mutation(DOMAIN, 'rules: "local-draft-1"', 'rules: "local-draft-0"')


if __name__ == "__main__":
    unittest.main()
