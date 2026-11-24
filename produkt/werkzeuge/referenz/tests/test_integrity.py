"""Semantische Gegenproben jenseits der JSON-Struktur."""
from copy import deepcopy
import unittest

from produkt.werkzeuge.referenz import ContractError, evaluate_trace, load_rules
from produkt.werkzeuge.referenz.offene_spuren import Trace, uid


class IntegrityTests(unittest.TestCase):
    def reject(self, events, code):
        with self.assertRaises(ContractError) as ctx:
            evaluate_trace(events)
        self.assertEqual(ctx.exception.code, code)

    def test_empty_trace_rejected(self):
        self.reject([], "empty_trace")

    def test_opening_is_required(self):
        t = Trace("unit-no-open"); t.answer(); t.close()
        self.reject(t.events[1:], "missing_open")

    def test_second_opening_rejected(self):
        t = Trace("unit-second-open")
        t.add("attempt.opened", deepcopy(t.events[0]["payload"]), "system")
        self.reject(t.events, "second_open")

    def test_event_after_close_rejected(self):
        t = Trace("unit-after-close"); t.close(); t.answer()
        self.reject(t.events, "event_after_close")

    def test_candidate_cannot_change_inside_stream(self):
        t = Trace("unit-candidate"); t.answer(); t.close()
        t.events[1]["candidate"]["content"] = "2.0.0"
        self.reject(t.events, "candidate_changed")

    def test_unsupported_rule_package_is_not_evaluated_as_v1(self):
        t = Trace("unit-rules"); t.answer(); t.close()
        for e in t.events:
            e["candidate"]["rules"] = "2.0.0"
        self.reject(t.events, "unsupported_rules_version")

    def test_unsupported_task_has_no_positive_fallback(self):
        t = Trace("unit-task"); t.answer(); t.close()
        t.events[0]["payload"]["taskContract"] = "anderer-vertrag"
        self.reject(t.events, "unsupported_task")

    def test_duplicate_material_identity_different_zone_rejected(self):
        t = Trace("unit-material-id")
        items = t.events[0]["payload"]["initialMaterial"]
        items[-1]["itemId"] = items[0]["itemId"]
        self.reject(t.events, "duplicate_material")

    def test_initial_material_count_cannot_lie(self):
        t = Trace("unit-material-count")
        t.events[0]["payload"]["initialMaterial"].pop()
        self.reject(t.events, "starting_material")

    def test_move_entity_may_not_repeat_under_new_event_id(self):
        t = Trace("unit-duplicate-move"); t.move()
        t.add("material.moved", deepcopy(t.events[-1]["payload"]))
        self.reject(t.events, "duplicate_entity")

    def test_ineffective_move_rejected(self):
        t = Trace("unit-ineffective"); t.move(source="right", target="right")
        self.reject(t.events, "ineffective_move")

    def test_app_cannot_use_child_input_mode(self):
        t = Trace("unit-app-via"); t.move(actor="app", via="ziehen")
        self.reject(t.events, "schema")

    def test_mixed_app_child_material_not_wholly_child_way(self):
        t = Trace("unit-mixed"); t.move(t.right[:1], actor="app"); t.move(t.right[1:2]); t.answer(); t.close()
        report = evaluate_trace(t.events)
        self.assertEqual(report["facts"]["board.ten.child"], "falsch")
        self.assertEqual(report["facts"]["board.ten.app"], "wahr")
        self.assertEqual(report["decisions"]["attempt.result.correct"], "must_claim")

    def test_dangling_undo_rejected(self):
        t = Trace("unit-undo-missing"); t.undo(uid("absent"))
        self.reject(t.events, "dangling_reference")

    def test_undo_different_actor_rejected(self):
        t = Trace("unit-undo-actor"); move = t.move(actor="app"); t.undo(move)
        self.reject(t.events, "undo_actor")

    def test_duplicate_undo_new_event_rejected(self):
        t = Trace("unit-undo-twice"); move = t.move(); t.undo(move); t.undo(move)
        self.reject(t.events, "inactive_move")

    def test_undo_respects_per_item_dependencies(self):
        t = Trace("unit-undo-dependency"); move = t.move(t.right[:1]); t.move(t.right[:1], "left", "spare"); t.undo(move)
        self.reject(t.events, "undo_dependency")

    def test_undo_of_unrelated_item_need_not_be_global_lifo(self):
        t = Trace("unit-independent-undo"); first = t.move(t.right[:1]); t.move(t.right[1:2]); t.undo(first); t.close()
        report = evaluate_trace(t.events)
        self.assertEqual(report["facts"]["board.ten.child"], "falsch")
        self.assertEqual(report["facts"]["history.ten.child"], "wahr")

    def test_hint_between_two_partial_moves_is_prior_help(self):
        t = Trace("unit-partial-help"); t.move(t.right[:1]); t.support(); t.move(t.right[1:2]); t.close()
        self.assertEqual(evaluate_trace(t.events)["decisions"]["attempt.ten.guided"], "must_claim")

    def test_undo_demo_and_replay_same_items_is_still_guided(self):
        t = Trace("unit-demo-reset"); move = t.move(actor="app"); t.undo(move, "app"); t.move(); t.close()
        report = evaluate_trace(t.events)
        self.assertEqual(report["facts"]["support.ten.before"], "wahr")
        self.assertEqual(report["decisions"]["attempt.ten"], "must_not_claim")

    def test_neutral_demo_label_cannot_hide_help(self):
        t = Trace("unit-neutral-demo"); t.support(effect="neutral")
        t.events[-1]["payload"]["kind"] = "demo"
        self.reject(t.events, "neutral_demo")

    def test_nontrivial_step_cannot_be_labelled_neutral(self):
        for kind in ["teilschritt", "loesungsweg"]:
            t = Trace("unit-neutral-" + kind); t.support(effect="neutral")
            t.events[-1]["payload"]["kind"] = kind
            self.reject(t.events, "neutral_step")

    def test_correct_after_automatic_reading_does_not_retain_error(self):
        t = Trace("unit-auto-correct"); t.recognition(); t.answer(16, "automatisch_uebernommen")
        t.add("response.retracted", {"answerId": t.answer_id}); t.answer(15, "korrigiert"); t.close()
        for length in range(1, len(t.events) + 1):
            self.assertNotEqual(evaluate_trace(t.events[:length])["facts"]["answer.deviation"], "wahr")
        self.assertEqual(evaluate_trace(t.events)["decisions"]["attempt.result.correct"], "must_claim")

    def test_answer_needs_existing_input(self):
        t = Trace("unit-no-input"); t.answer()
        t.events[-1]["payload"]["inputId"] = uid("absent")
        self.reject(t.events, "dangling_reference")

    def test_direct_handwriting_cannot_skip_confirmation(self):
        t = Trace("unit-direct-handwriting"); t.answer()
        t.events[1]["payload"]["mode"] = "handschrift_finger"
        self.reject(t.events, "direct_handwriting")

    def test_direct_answer_cannot_carry_recognition_reference(self):
        t = Trace("unit-direct-ref"); t.answer()
        t.events[-1]["payload"]["fromRecognitionId"] = uid("unused")
        self.reject(t.events, "schema")

    def test_automatic_answer_actor_must_be_app(self):
        t = Trace("unit-auto-actor"); t.recognition(); t.answer(16, "automatisch_uebernommen")
        t.events[-1]["actor"] = "child"
        self.reject(t.events, "schema")

    def test_recognition_cannot_reference_different_input(self):
        t = Trace("unit-cross-input"); t.recognition(); t.capture("handschrift_finger"); t.answer(15, "korrigiert")
        self.reject(t.events, "recognition_input_mismatch")

    def test_recognition_requires_handwriting_mode(self):
        t = Trace("unit-recognition-mode"); t.recognition()
        t.events[1]["payload"]["mode"] = "ziffernblock"
        self.reject(t.events, "recognition_mode")

    def test_confirmation_must_match_reading_value(self):
        t = Trace("unit-confirm-value"); t.recognition(); t.answer(15, "bestaetigt")
        self.reject(t.events, "recognition_value_mismatch")

    def test_active_answer_must_be_retracted_before_replacement(self):
        t = Trace("unit-live-answer"); t.answer(); t.answer(14)
        self.reject(t.events, "answer_not_retracted")

    def test_retraction_requires_active_reference(self):
        t = Trace("unit-inactive-answer"); t.answer(); t.add("response.retracted", {"answerId": t.answer_id}); t.add("response.retracted", {"answerId": t.answer_id})
        self.reject(t.events, "inactive_answer")

    def test_retraction_cannot_target_unknown_answer(self):
        t = Trace("unit-unknown-answer"); t.add("response.retracted", {"answerId": uid("unknown")})
        self.reject(t.events, "dangling_reference")

    def test_gap_marker_cannot_point_into_future(self):
        t = Trace("unit-future-gap"); t.condition(since=10)
        self.reject(t.events, "gap_range")

    def test_gap_marker_with_old_start_taints_old_observations(self):
        t = Trace("unit-retro-gap"); t.move(); t.support(); t.condition(since=1); t.answer(); t.close()
        report = evaluate_trace(t.events)
        self.assertEqual(report["decisions"]["attempt.ten"], "undecidable")
        self.assertEqual(report["decisions"]["attempt.result.correct"], "must_claim")

    def test_permission_denied_does_not_invent_error_for_digit_pad(self):
        t = Trace("unit-permission"); t.condition("permission_missing"); t.answer(); t.close()
        self.assertEqual(evaluate_trace(t.events)["decisions"]["attempt.result.correct"], "must_claim")

    def test_device_clock_reversal_is_not_sequence_reversal(self):
        t = Trace("unit-clock"); t.move(); t.answer(); t.close()
        t.events[-1]["occurredAt"] = "2025-01-01T00:00:00Z"
        self.assertEqual(evaluate_trace(t.events)["decisions"]["attempt.ten"], "must_claim")

    def test_monotonic_clock_reversal_same_boot_is_integrity_error(self):
        t = Trace("unit-monotonic"); t.move()
        t.events[0]["monotonic"] = {"bootId": uid("boot"), "ns": 10}
        t.events[1]["monotonic"] = {"bootId": uid("boot"), "ns": 5}
        self.reject(t.events, "monotonic_reversal")

    def test_new_boot_may_restart_monotonic_clock(self):
        t = Trace("unit-new-boot"); t.move(); t.close()
        t.events[0]["monotonic"] = {"bootId": uid("boot-one"), "ns": 10}
        t.events[1]["monotonic"] = {"bootId": uid("boot-two"), "ns": 5}
        self.assertEqual(evaluate_trace(t.events)["decisions"]["attempt.ten"], "must_claim")

    def test_mode_change_must_match_current_mode(self):
        t = Trace("unit-mode"); t.capture(); t.add("mode.changed", {"from": "tastatur", "to": "auswahl"})
        self.reject(t.events, "mode_mismatch")

    def test_invalidation_cannot_reference_unknown_event(self):
        t = Trace("unit-invalidation"); t.add("observation.invalidated", {"eventIds": [uid("unknown")], "reason": "offene Probe"}, "system")
        self.reject(t.events, "dangling_reference")

    def test_profile_erasure_must_match_local_profile(self):
        t = Trace("unit-profile"); t.add("profile.erasure_requested", {"profileId": uid("other-profile")}, "system")
        self.reject(t.events, "foreign_profile")

    def test_content_withdrawal_must_match_candidate_content(self):
        t = Trace("unit-content"); t.add("content.withdrawn", {"content": "2.0.0", "reason": "offene Probe"}, "system")
        self.reject(t.events, "foreign_content")

    def test_artifact_deletion_cannot_invent_artifact(self):
        t = Trace("unit-artifact"); t.add("artifact.deleted", {"artifactId": uid("unknown")}, "system")
        self.reject(t.events, "dangling_reference")

    def test_foreign_rule_applicability_stays_undecidable(self):
        t = Trace("unit-applicability"); t.move(); t.answer(); t.close()
        rules = load_rules()
        for rule in rules:
            rule["applicability"]["taskContracts"] = ["anderer-vertrag"]
        report = evaluate_trace(t.events, rules)
        self.assertFalse(report["claims"])
        self.assertEqual(set(report["decisions"].values()), {"undecidable"})

    def test_evaluation_does_not_mutate_caller_data(self):
        t = Trace("unit-pure"); t.move(); t.answer(); t.close()
        before = deepcopy(t.events)
        evaluate_trace(t.events)
        self.assertEqual(t.events, before)
