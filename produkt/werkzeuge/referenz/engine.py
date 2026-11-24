"""Deterministischer Referenz-Replay fuer den offenen Leitfall 8 + 7."""
from __future__ import annotations

from collections import Counter
from enum import Enum
from typing import Any

from .contracts import (FACTS, VERSION, ContractError, canonical, load_rules,
                        require, validate_rules, validate_schema)


class Truth(str, Enum):
    TRUE = "wahr"
    FALSE = "falsch"
    UNKNOWN = "unbekannt"


def truth(value: bool) -> Truth:
    return Truth.TRUE if value else Truth.FALSE


def conjunction(values: list[Truth]) -> Truth:
    if Truth.FALSE in values:
        return Truth.FALSE
    if Truth.UNKNOWN in values:
        return Truth.UNKNOWN
    return Truth.TRUE


def negate(value: Truth) -> Truth:
    return {Truth.TRUE: Truth.FALSE, Truth.FALSE: Truth.TRUE,
            Truth.UNKNOWN: Truth.UNKNOWN}[value]


def decide(rule: dict, facts: dict[str, Truth]) -> str:
    """Kleene-Konjunktion: ein belegtes Veto dominiert Unbekannt."""
    req = rule["logic"]["requires"]
    result = conjunction([facts.get(name, Truth.UNKNOWN) for name in req["all"]]
                         + [negate(facts.get(name, Truth.UNKNOWN)) for name in req["none"]])
    return {Truth.TRUE: "must_claim", Truth.FALSE: "must_not_claim",
            Truth.UNKNOWN: "undecidable"}[result]


LIFECYCLE = {"content.withdrawn", "observation.invalidated", "artifact.deleted",
             "profile.erasure_requested"}


def _ordered(events: list[dict]) -> tuple[list[dict], int, list[int]]:
    require(isinstance(events, list) and bool(events), "empty_trace", "Ereignisspur fehlt")
    by_id, by_seq = {}, {}
    duplicates = 0
    for event in events:
        validate_schema("ereignis", event)
        eid, seq = event["eventId"], event["seq"]
        if eid in by_id:
            require(canonical(event) == canonical(by_id[eid]), "event_id_conflict", eid)
            duplicates += 1
            continue
        require(seq not in by_seq, "sequence_conflict", str(seq))
        by_id[eid] = event
        by_seq[seq] = event
    ordered = sorted(by_id.values(), key=lambda event: event["seq"])
    first = ordered[0]
    require(first["seq"] == 0 and first["type"] == "attempt.opened",
            "missing_open", "Stream muss mit attempt.opened an seq 0 beginnen")
    gaps = []
    previous = -1
    clocks = {}
    for event in ordered:
        require(event["streamId"] == first["streamId"], "foreign_stream", event["eventId"])
        require(event["candidate"] == first["candidate"], "candidate_changed", event["eventId"])
        if event["seq"] != previous + 1:
            gaps.append(previous + 1)
        previous = event["seq"]
        if "monotonic" in event:
            clock = event["monotonic"]
            require(clock["ns"] >= clocks.get(clock["bootId"], 0),
                    "monotonic_reversal", event["eventId"])
            clocks[clock["bootId"]] = clock["ns"]
        if event["type"] == "condition.observed":
            payload = event["payload"]
            if payload["kind"] == "gap":
                require(0 < payload["sinceSeq"] <= event["seq"],
                        "gap_range", event["eventId"])
                gaps.append(payload["sinceSeq"])
            elif payload["kind"] == "interruption":
                gaps.append(event["seq"])
    return ordered, duplicates, sorted(set(gaps))


class Replay:
    def __init__(self, events: list[dict], gaps: list[int]):
        self.events = events
        self.gaps = gaps
        self.opening = events[0]["payload"]
        require(events[0]["candidate"]["rules"] == VERSION,
                "unsupported_rules_version", "Regelpaket stimmt nicht mit Referenz v1 ueberein")
        initial = self.opening["initialMaterial"]
        require(self.opening["taskContract"] == "sum-8-7"
                and self.opening["taskVersion"] == VERSION
                and self.opening["startingState"] == "board-8-7-v1"
                and self.opening["family"] == "addition-20"
                and self.opening["representation"] == "counters"
                and self.opening["target"] == "sum-8-7", "unsupported_task", "Aufgabenfassung")
        self.initial = {item["itemId"]: item["zone"] for item in initial}
        require(len(self.initial) == len(initial), "duplicate_material", "Anfangsmaterial")
        require(Counter(self.initial.values()) == Counter(left=8, right=7),
                "starting_material", "Genau acht und sieben Aufgabenplaettchen erforderlich")
        self.positions = dict(self.initial)
        self.histories = {item: [] for item in self.initial}
        self.inputs, self.recognitions, self.answers, self.moves, self.artifacts = {}, {}, {}, {}, {}
        self.identities = set(self.initial)
        self.active_moves = set()
        self.active_answer = None
        self.support = []
        self.closed = None
        self.valid = True
        self.history_ten = False
        self.seen_events = set()
        self.gap_cursor = 0
        self.board_known = True
        self.ten_seq = self.doubles_seq = None
        self.current_mode = None

    def declare(self, identifier: str) -> None:
        require(identifier not in self.identities, "duplicate_entity", identifier)
        self.identities.add(identifier)

    def reference(self, identifier: str, collection: dict, kind: str) -> Any:
        require(identifier in collection, "dangling_reference", kind)
        return collection[identifier]

    def board(self) -> tuple[Truth, Truth, Truth]:
        if not self.board_known:
            return (Truth.UNKNOWN,) * 3
        counts = Counter(self.positions.values())
        ten = counts == Counter(left=10, right=5)
        doubles = counts == Counter(left=7, right=7, spare=1)
        displaced = [item for item in self.positions if self.positions[item] != self.initial[item]]
        actors = {self.moves[self.histories[item][-1]]["actor"] for item in displaced}
        child = bool(displaced) and actors == {"child"}
        return truth(ten and child), truth(ten and "app" in actors), truth(doubles and child)

    def before(self, target: str, seq: int | None) -> Truth:
        if seq is None:
            return Truth.UNKNOWN
        if any(s <= seq and t in {target, "all"} for s, t in self.support):
            return Truth.TRUE
        if any(g <= seq for g in self.gaps):
            return Truth.UNKNOWN
        return Truth.FALSE

    def consume(self, event: dict) -> None:
        typ, p, seq = event["type"], event["payload"], event["seq"]
        while self.gap_cursor < len(self.gaps) and self.gaps[self.gap_cursor] <= seq:
            # Fehlende Ereignisse koennen einen Wert zuruecknehmen oder Material aendern.
            # Eine SPAETERE definitive Antwort kann das Ergebnis erneut belegen.
            self.active_answer = None
            self.board_known = False
            self.gap_cursor += 1
        require(self.closed is None or typ in LIFECYCLE, "event_after_close", typ)
        if typ == "attempt.opened":
            require(seq == 0, "second_open", "Nur ein Anfang pro Stream")
        elif typ == "attempt.closed":
            self.closed = p["reason"]
        elif typ == "input.captured":
            self.declare(p["inputId"])
            if self.current_mode is not None:
                require(p["mode"] == self.current_mode, "mode_mismatch", "Eingabemodus")
            self.current_mode = p["mode"]
            self.inputs[p["inputId"]] = p
        elif typ == "recognition.proposed":
            captured = self.reference(p["inputId"], self.inputs, "inputId")
            require(captured["mode"] in {"handschrift_finger", "handschrift_stift"},
                    "recognition_mode", "Nur Handschrift erzeugt Lesarten")
            self.declare(p["recognitionId"])
            self.recognitions[p["recognitionId"]] = p
        elif typ == "answer.committed":
            captured = self.reference(p["inputId"], self.inputs, "inputId")
            require(self.active_answer is None, "answer_not_retracted", "Aktive Antwort besteht")
            if p["origin"] == "direkt":
                require(captured["mode"] in {"ziffernblock", "tastatur", "auswahl"},
                        "direct_handwriting", "Handschrift braucht eine bestaetigte Lesart")
            else:
                rec = self.reference(p["fromRecognitionId"], self.recognitions, "fromRecognitionId")
                require(rec["inputId"] == p["inputId"], "recognition_input_mismatch", "inputId")
                same = int(rec["reading"]) == p["value"]
                require(same == (p["origin"] != "korrigiert"), "recognition_value_mismatch", p["origin"])
            self.declare(p["answerId"])
            self.answers[p["answerId"]] = p
            self.active_answer = p["answerId"]
        elif typ == "response.retracted":
            self.reference(p["answerId"], self.answers, "answerId")
            require(p["answerId"] == self.active_answer, "inactive_answer", "Ruecknahme")
            self.active_answer = None
        elif typ == "material.moved":
            require(p["fromZone"] != p["toZone"], "ineffective_move", "Gleiche Zone")
            self.declare(p["moveId"])
            for item in p["items"]:
                require(item in self.positions, "unknown_material", item)
                if self.board_known:
                    require(self.positions[item] == p["fromZone"], "wrong_source", item)
            self.moves[p["moveId"]] = event
            self.active_moves.add(p["moveId"])
            for item in p["items"]:
                self.positions[item] = p["toZone"]
                self.histories[item].append(p["moveId"])
            if event["actor"] == "app":
                # Sichtbare App-Bewegung ist selbst Hilfe, auch ohne separates Hilfsereignis.
                self.support.append((seq, "all"))
        elif typ == "action.undone":
            move = self.reference(p["moveId"], self.moves, "moveId")
            mp = move["payload"]
            require(move["actor"] == event["actor"], "undo_actor", "Nur eigener Zug")
            require(p["moveId"] in self.active_moves, "inactive_move", "Undo")
            for item in mp["items"]:
                require(self.histories[item] and self.histories[item][-1] == p["moveId"],
                        "undo_dependency", item)
            self.active_moves.remove(p["moveId"])
            for item in mp["items"]:
                self.positions[item] = mp["fromZone"]
                self.histories[item].pop()
        elif typ == "support.presented":
            self.declare(p["supportId"])
            require(not (p["kind"] == "demo" and p["effect"] == "neutral"),
                    "neutral_demo", "Eine Demo ist nicht neutral")
            require(not (p["kind"] in {"teilschritt", "loesungsweg"} and p["effect"] == "neutral"),
                    "neutral_step", "Ein gezeigter Rechenschritt ist nicht neutral")
            if p["effect"] != "neutral":
                self.support.append((seq, p["target"]))
        elif typ == "mode.changed":
            require(p["from"] != p["to"], "ineffective_mode", "Gleicher Modus")
            if self.current_mode is not None:
                require(self.current_mode == p["from"], "mode_mismatch", "Ausgangsmodus")
            self.current_mode = p["to"]
        elif typ == "artifact.saved":
            self.declare(p["artifactId"])
            self.artifacts[p["artifactId"]] = p
        elif typ == "self_report.recorded":
            self.declare(p["reportId"])
        elif typ == "content.withdrawn":
            require(p["content"] == event["candidate"]["content"], "foreign_content", "Inhaltsfassung")
            self.valid = False
        elif typ == "observation.invalidated":
            require(set(p["eventIds"]) <= self.seen_events, "dangling_reference", "eventIds")
            self.valid = False
        elif typ == "artifact.deleted":
            self.reference(p["artifactId"], self.artifacts, "artifactId")
            del self.artifacts[p["artifactId"]]
        elif typ == "profile.erasure_requested":
            require(p["profileId"] == self.opening["profileId"], "foreign_profile", "profileId")
            self.valid = False
        ten, _, doubles = self.board()
        if ten == Truth.TRUE:
            self.history_ten = True
            if self.ten_seq is None:
                self.ten_seq = seq
        else:
            self.ten_seq = None
        if doubles == Truth.TRUE:
            if self.doubles_seq is None:
                self.doubles_seq = seq
        else:
            self.doubles_seq = None
        self.seen_events.add(event["eventId"])

    def facts(self) -> dict[str, Truth]:
        result = {key: Truth.UNKNOWN for key in FACTS}
        result["observation.valid"] = truth(self.valid)
        result["attempt.submitted"] = (Truth.UNKNOWN if self.closed is None
                                       else truth(self.closed == "submitted"))
        result["observation.complete"] = (Truth.TRUE if self.closed and not self.gaps
                                          else Truth.UNKNOWN)
        if self.active_answer is not None:
            answer = self.answers[self.active_answer]
            if answer["origin"] != "automatisch_uebernommen":
                result["answer.value.15"] = truth(answer["value"] == 15)
                result["answer.deviation"] = truth(answer["value"] != 15)
        ten, app, doubles = self.board()
        result["board.ten.child"] = ten
        result["board.ten.app"] = app
        result["board.doubles.child"] = doubles
        result["board.path.child"] = (Truth.TRUE if Truth.TRUE in (ten, doubles) else
                                      Truth.UNKNOWN if Truth.UNKNOWN in (ten, doubles) else Truth.FALSE)
        result["history.ten.child"] = (Truth.TRUE if self.history_ten else
                                       Truth.UNKNOWN if self.gaps else Truth.FALSE)
        result["support.ten.before"] = self.before("ten.step", self.ten_seq)
        result["support.doubles.before"] = self.before("doubles.step", self.doubles_seq)
        return result


def evaluate_trace(events: list[dict], rules: list[dict] | None = None) -> dict:
    """Auswertung einer vollstaendigen Spur oder eines Zwischenpraefixes.

    Die Zustellung darf beliebig geordnet sein; seq ist die fachliche Reihenfolge.
    Integritaetsfehler sperren den ganzen Bericht, Luecken bleiben dreiwertig.
    """
    rules = load_rules() if rules is None else rules
    validate_rules(rules)
    ordered, duplicates, gaps = _ordered(events)
    replay = Replay(ordered, gaps)
    for event in ordered:
        replay.consume(event)
    facts = replay.facts()
    decisions, claims = {}, []
    for rule in rules:
        applies = (replay.opening["taskContract"] in rule["applicability"]["taskContracts"]
                   and replay.opening["startingState"] in rule["applicability"]["startingStates"])
        decision = decide(rule, facts) if applies else "undecidable"
        decisions[rule["claimId"]] = decision
        if decision == "must_claim":
            claims.append({"claimId": rule["claimId"], "ruleId": rule["id"],
                           "ruleVersion": rule["version"],
                           "text": rule["boundary"]["wording"]["de-CH"]})
    # Fallbacks werden NICHT als Behauptungen kopiert. Jede Regel steht fuer sich.
    return {"schemaVersion": VERSION, "streamId": ordered[0]["streamId"],
            "candidate": ordered[0]["candidate"],
            "facts": {key: value.value for key, value in facts.items()},
            "decisions": decisions, "claims": claims,
            "integrity": {"uniqueEvents": len(ordered), "deduplicated": duplicates,
                          "gapStarts": gaps}, "curriculumSourceStatus": "offen"}
