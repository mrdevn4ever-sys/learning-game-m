"""Offene Regressionen F01-F03; keine unabhaengige Abnahme.

Die Sollwerte sind explizit, nicht aus dem Replay abgeleitet. Der historische
Katalog und seine 165 Tests bleiben unveraendert. F04-F06 sind nicht umdefiniert.
"""
from copy import deepcopy
import json
import unittest

from produkt.werkzeuge.referenz import ContractError, evaluate_trace
from produkt.werkzeuge.referenz.engine import Replay, Truth, _ordered
from produkt.werkzeuge.referenz.offene_spuren import Trace, uid

C, N, U = "must_claim", "must_not_claim", "undecidable"


class RepairTests(unittest.TestCase):
    def reject(self, t, code):
        with self.assertRaises(ContractError) as caught:
            evaluate_trace(t.events)
        self.assertEqual(caught.exception.code, code)

    def result(self, t, value="wahr", decision=C):
        report = evaluate_trace(t.events)
        self.assertEqual(report["facts"]["answer.value.15"], value)
        self.assertEqual(report["decisions"]["attempt.result.correct"], decision)
        return report

    def replay(self, t):
        ordered, _, gaps = _ordered(t.events)
        replay = Replay(ordered, gaps)
        for event in ordered:
            replay.consume(event)
        return replay

    def test_unknown_response_can_be_retracted_then_corrected(self):
        t = Trace("repair-f01-auto-gap-correction")
        t.recognition(); t.answer(16, "automatisch_uebernommen")
        t.condition(); t.add("response.retracted", {"answerId": t.answer_id})
        t.answer(15, "korrigiert"); t.close()
        report = self.result(t)
        self.assertEqual(report["facts"]["board.ten.child"], "unbekannt")
        for length in range(1, len(t.events) + 1):
            self.assertNotEqual(evaluate_trace(t.events[:length])["facts"]["answer.deviation"], "wahr")

    def test_gap_without_new_answer_does_not_preserve_old_result(self):
        t = Trace("repair-f01-unknown-answer"); t.answer(); t.condition(); t.close()
        self.result(t, "unbekannt", U)

    def test_known_retracted_answer_stays_inactive_across_gap(self):
        t = Trace("repair-f01-retracted-before-gap"); t.answer()
        t.add("response.retracted", {"answerId": t.answer_id}); t.condition()
        t.add("response.retracted", {"answerId": t.answer_id})
        self.reject(t, "inactive_answer")

    def test_unknown_retraction_becomes_known_inactive(self):
        t = Trace("repair-f01-double-after-gap"); t.answer(); t.condition()
        t.add("response.retracted", {"answerId": t.answer_id})
        t.add("response.retracted", {"answerId": t.answer_id})
        self.reject(t, "inactive_answer")

    def test_unknown_old_answer_cannot_be_retracted_after_new_commit(self):
        t = Trace("repair-f01-old-after-new"); t.answer(14); old = t.answer_id
        t.condition(); t.answer(); t.add("response.retracted", {"answerId": old})
        self.reject(t, "inactive_answer")

    def test_gap_does_not_hide_dangling_answer_reference(self):
        t = Trace("repair-f01-dangling"); t.condition()
        t.add("response.retracted", {"answerId": uid("repair-absent-answer")})
        self.reject(t, "dangling_reference")

    def test_unknown_old_answer_does_not_block_new_direct_answer(self):
        t = Trace("repair-f01-unknown-replacement"); t.answer(14); t.condition()
        t.answer(); t.close(); self.result(t)

    def test_new_commit_after_gap_is_active_and_requires_retraction(self):
        t = Trace("repair-f01-live-after-gap"); t.answer(14); t.condition(); t.answer(); t.answer(14)
        self.reject(t, "answer_not_retracted")

    def test_mode_can_be_observed_after_missing_change(self):
        t = Trace("repair-f01-mode-projection"); t.recognition()
        t.add("mode.changed", {"from": "handschrift_finger", "to": "ziffernblock"})
        t.answer(); t.close()
        t.events = [e for e in t.events if e["type"] != "mode.changed"]
        self.result(t)

    def test_mode_change_can_start_from_unknown_mode(self):
        t = Trace("repair-f01-mode-from-unknown"); t.capture(); t.condition()
        t.add("mode.changed", {"from": "tastatur", "to": "ziffernblock"})
        t.answer(); t.close(); self.result(t)

    def test_fresh_mode_is_strict_for_next_capture(self):
        t = Trace("repair-f01-fresh-capture-mode"); t.condition(); t.capture()
        t.capture("tastatur")
        self.reject(t, "mode_mismatch")

    def test_fresh_mode_is_strict_for_next_mode_change(self):
        t = Trace("repair-f01-fresh-change-mode"); t.condition()
        t.add("mode.changed", {"from": "handschrift_finger", "to": "ziffernblock"})
        t.add("mode.changed", {"from": "tastatur", "to": "auswahl"})
        self.reject(t, "mode_mismatch")

    def test_gap_does_not_bypass_recognition_input_binding(self):
        t = Trace("repair-f01-binding"); t.recognition(); t.condition()
        t.capture("handschrift_finger"); t.answer(15, "korrigiert")
        self.reject(t, "recognition_input_mismatch")

    def test_gap_does_not_bypass_direct_handwriting_rule(self):
        t = Trace("repair-f01-direct-handwriting"); t.condition(); t.answer()
        t.events[-2]["payload"]["mode"] = "handschrift_finger"
        self.reject(t, "direct_handwriting")

    def test_answer_activity_is_explicitly_three_valued(self):
        t = Trace("repair-f01-activity-state"); t.answer(); answer = t.answer_id
        self.assertEqual(self.replay(t).answer_activity[answer], Truth.TRUE)
        t.condition()
        self.assertEqual(self.replay(t).answer_activity[answer], Truth.UNKNOWN)
        t.add("response.retracted", {"answerId": answer})
        self.assertEqual(self.replay(t).answer_activity[answer], Truth.FALSE)

    def test_two_gaps_forget_new_answer_and_mode_again(self):
        t = Trace("repair-f01-two-gaps"); t.recognition(); t.condition(); t.answer()
        t.condition(); t.capture("tastatur"); t.close()
        self.result(t, "unbekannt", U)

    def test_local_zone_recovery_is_not_whole_board_knowledge(self):
        t = Trace("repair-f02-local-not-global"); t.condition(); t.move(); t.answer(); t.close()
        report = self.result(t)
        self.assertEqual(report["facts"]["board.ten.child"], "unbekannt")
        self.assertEqual(report["decisions"]["attempt.path.displayed"], U)

    def test_fully_reobserved_items_restore_path_not_absent_help(self):
        t = Trace("repair-f02-complete-recovery"); t.condition()
        t.move(t.left, "left", "spare"); t.move(t.right, "right", "spare")
        t.move(t.left + t.right[:2], "spare", "left")
        t.move(t.right[2:], "spare", "right"); t.answer(); t.close()
        report = self.result(t)
        self.assertEqual(report["facts"]["board.ten.child"], "wahr")
        self.assertEqual(report["facts"]["support.ten.before"], "unbekannt")
        self.assertEqual(report["decisions"]["attempt.path.displayed"], C)
        self.assertEqual(report["decisions"]["attempt.ten"], U)
        self.assertEqual(report["decisions"]["attempt.ten.guided"], U)

    def test_unobserved_undo_base_does_not_restore_old_child_provenance(self):
        t = Trace("repair-f01-unknown-undo-base"); original = t.move()
        t.condition(); detour = t.move(t.right[:2], "left", "spare", actor="app")
        t.undo(detour, "app"); t.answer(); t.close()
        replay = self.replay(t)
        self.assertEqual(replay.move_activity[original], Truth.UNKNOWN)
        self.assertEqual(replay.histories[t.right[0]], [None])
        self.assertEqual(self.result(t)["facts"]["board.ten.child"], "unbekannt")

    def test_child_detour_after_help_is_current_guided_not_historical_free(self):
        t = Trace("repair-f03-history-current"); t.move()
        prefix = deepcopy(t); prefix.close()
        self.assertEqual(evaluate_trace(prefix.events)["decisions"]["attempt.ten"], C)
        t.support(); m = t.move(t.right[2:3]); t.undo(m); t.close()
        report = evaluate_trace(t.events)
        self.assertEqual(report["facts"]["history.ten.child"], "wahr")
        self.assertEqual(report["facts"]["support.ten.before"], "wahr")
        self.assertEqual(report["decisions"]["attempt.ten"], N)
        self.assertEqual(report["decisions"]["attempt.ten.guided"], C)

    def test_child_undo_after_help_is_new_action_even_if_detour_precedes_help(self):
        t = Trace("repair-f03-child-undo-anchor"); t.move()
        m = t.move(t.right[2:3]); t.support(); t.undo(m); t.close()
        report = evaluate_trace(t.events)
        self.assertEqual(report["decisions"]["attempt.ten.guided"], C)
        self.assertEqual(report["facts"]["history.ten.child"], "wahr")

    def test_app_undo_does_not_redate_child_action_before_later_hint(self):
        t = Trace("repair-f03-app-undo-anchor"); t.move()
        m = t.move(t.right[2:3], actor="app"); t.support(); t.undo(m, "app"); t.close()
        report = evaluate_trace(t.events)
        self.assertEqual(report["decisions"]["attempt.ten"], C)
        self.assertEqual(report["decisions"]["attempt.ten.guided"], N)

    def test_app_demo_repeated_by_child_remains_guided(self):
        t = Trace("repair-f03-demo-repeat"); m = t.move(actor="app"); t.undo(m, "app")
        t.move(); t.close()
        self.assertEqual(evaluate_trace(t.events)["decisions"]["attempt.ten.guided"], C)

    def test_result_and_material_are_not_blanket_accepted_after_app_restore(self):
        for value, decision in [(15, C), (14, N), (None, U)]:
            with self.subTest(value=value):
                t = Trace("repair-f03-result-" + str(value)); t.move()
                t.support(); m = t.move(t.right[2:3], actor="app"); t.undo(m, "app")
                if value is not None:
                    t.answer(value)
                t.close(); report = evaluate_trace(t.events)
                self.assertEqual(report["decisions"]["attempt.ten"], C)
                self.assertEqual(report["decisions"]["attempt.result.correct"], decision)

    def test_repaired_trace_replay_and_redelivery_preserve_claims(self):
        t = Trace("repair-f03-redelivery"); t.move(); t.support()
        m = t.move(t.right[2:3], actor="app"); t.undo(m, "app"); t.answer(); t.close()
        baseline = self.result(t)
        supplied = list(reversed(deepcopy(t.events) * 3))
        report = evaluate_trace(json.loads(json.dumps(supplied)))
        self.assertEqual(report["facts"], baseline["facts"])
        self.assertEqual(report["claims"], baseline["claims"])
        self.assertEqual(report["integrity"]["deduplicated"], 2 * len(t.events))

    def test_known_inactivity_inferred_from_outer_undo_is_not_unknown(self):
        for actor in ("child", "app"):
            with self.subTest(actor=actor):
                t = Trace("repair-f01-inferred-inactive-" + actor)
                outer = t.move(t.right[:1], actor=actor)
                inner = t.move(t.right[:1], "left", "right", actor)
                t.condition(); t.undo(outer, actor)
                # Die gleiche Zone allein beweist keine wieder aktive innere ID.
                t.undo(inner, actor)
                self.reject(t, "inactive_move")

    def test_fresh_undo_zone_blocks_unknown_outer_undo(self):
        for actor in ("child", "app"):
            with self.subTest(actor=actor):
                t = Trace("repair-f01-transitive-" + actor)
                outer = t.move(t.right[:2], actor=actor)
                t.move(t.right[:2], "left", "spare", actor)
                inner = t.move(t.right[1:2], "spare", "right", actor)
                t.condition()
                # Das innere Undo belegt die neue Zone spare. Ein direktes
                # aeusseres Undo von left widerspricht dieser Beobachtung.
                t.undo(inner, actor); t.undo(outer, actor)
                self.reject(t, "undo_dependency")

    def test_observed_descendant_after_gap_cannot_outlive_ancestor_undo(self):
        for actor in ("child", "app"):
            with self.subTest(actor=actor):
                t = Trace("repair-f01-transitive-fresh-" + actor); t.condition()
                outer = t.move(t.right[:1], actor=actor)
                # Erstes und zweites Plattchen werden durch die Gruppenbewegung
                # gekoppelt; der frische letzte Zug betrifft nur das zweite.
                t.move(t.right[1:2], actor=actor)
                t.move(t.right[:2], "left", "spare", actor)
                t.move(t.right[1:2], "spare", "right", actor)
                t.undo(outer, actor)
                self.reject(t, "undo_dependency")


def answer_recovery(value, expected_value, expected_decision):
    def run(self):
        t = Trace("repair-f01-new-answer-" + str(value)); t.answer(14); t.condition()
        t.add("response.retracted", {"answerId": t.answer_id})
        if value is not None:
            t.answer(value)
        t.close(); self.result(t, expected_value, expected_decision)
    return run


def actor_regression(actor, case):
    def run(self):
        t = Trace("repair-" + case + "-" + actor)
        if case == "missing-inner-undo":
            a = t.move(t.right[:1], actor=actor)
            b = t.move(t.right[:1], "left", "spare", actor)
            t.undo(b, actor); t.undo(a, actor); t.answer(); t.close()
            t.events = [e for e in t.events if not (e["type"] == "action.undone" and e["payload"]["moveId"] == b)]
            self.result(t)
        elif case == "fresh-dependency":
            a = t.move(t.right[:1], actor=actor); t.condition()
            t.move(t.right[:1], "left", "spare", actor); t.undo(a, actor)
            self.reject(t, "undo_dependency")
        elif case == "inactive-before-gap":
            a = t.move(actor=actor); t.undo(a, actor); t.condition(); t.undo(a, actor)
            self.reject(t, "inactive_move")
        elif case == "unknown-then-double-undo":
            a = t.move(actor=actor); t.condition(); t.undo(a, actor); t.undo(a, actor)
            self.reject(t, "inactive_move")
        elif case == "wrong-actor-after-gap":
            a = t.move(actor=actor); t.condition(); t.undo(a, "app" if actor == "child" else "child")
            self.reject(t, "undo_actor")
        elif case == "fresh-zone-conflict":
            t.condition(); t.move(t.right[:1], actor=actor)
            t.move(t.right[:1], "right", "spare", actor); t.answer(); t.close()
            self.reject(t, "wrong_source")
        elif case == "fresh-zone-correct":
            t.condition(); t.move(t.right[:1], actor=actor)
            t.move(t.right[:1], "left", "spare", actor); t.answer(); t.close()
            self.result(t)
        elif case == "undo-restores-zone-check":
            t.condition(); a = t.move(t.right[:1], actor=actor); t.undo(a, actor)
            t.move(t.right[:1], "left", "spare", actor)
            self.reject(t, "wrong_source")
        elif case == "second-gap-then-local-conflict":
            t.condition(); t.move(t.right[:1], actor=actor); t.condition()
            t.move(t.right[:1], "right", "spare", actor)
            t.move(t.right[:1], "right", "left", actor)
            self.reject(t, "wrong_source")
        elif case == "unrelated-item-still-unknown":
            t.condition(); t.move(t.right[:1], actor=actor)
            t.move(t.right[1:2], "spare", "right", actor); t.answer(); t.close()
            self.result(t)
    return run


def anchor_regression(actor, shape, moved_item, gap):
    def run(self):
        t = Trace(f"repair-f03-{actor}-{shape}-{moved_item}-{gap}")
        if shape == "ten":
            t.move(); target, fact = "ten.step", "support.ten.before"
        else:
            t.move(t.left[:1], "left", "spare")
            target, fact = "doubles.step", "support.doubles.before"
        t.support(target)
        if gap:
            t.condition()
        if moved_item == "original":
            item, source = (t.right[:1], "left") if shape == "ten" else (t.left[:1], "spare")
            destination = "right"
        else:
            item, source, destination = t.right[2:3], "right", "left"
        m = t.move(item, source, destination, actor); t.undo(m, actor); t.answer(); t.close()
        report = self.result(t)
        expected = "unbekannt" if gap else "falsch" if actor == "app" else "wahr"
        self.assertEqual(report["facts"][fact], expected)
        if shape == "ten":
            self.assertEqual(report["facts"]["history.ten.child"], "wahr")
            self.assertEqual(report["decisions"]["attempt.ten"], U if gap else C if actor == "app" else N)
            self.assertEqual(report["decisions"]["attempt.ten.guided"], U if gap else N if actor == "app" else C)
    return run


for _value, _fact, _decision in [(15, "wahr", C), (14, "falsch", N), (None, "unbekannt", U)]:
    setattr(RepairTests, "test_new_answer_after_gap_" + str(_value), answer_recovery(_value, _fact, _decision))
for _actor in ("child", "app"):
    for _case in ("missing-inner-undo", "fresh-dependency", "inactive-before-gap",
                  "unknown-then-double-undo", "wrong-actor-after-gap", "fresh-zone-conflict",
                  "fresh-zone-correct", "undo-restores-zone-check", "second-gap-then-local-conflict",
                  "unrelated-item-still-unknown"):
        setattr(RepairTests, "test_" + _case.replace("-", "_") + "_" + _actor, actor_regression(_actor, _case))
    for _shape in ("ten", "doubles"):
        for _item in ("original", "other"):
            for _gap in (False, True):
                setattr(RepairTests, f"test_anchor_{_actor}_{_shape}_{_item}_gap_{_gap}",
                        anchor_regression(_actor, _shape, _item, _gap))
