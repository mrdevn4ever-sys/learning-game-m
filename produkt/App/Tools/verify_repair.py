"""Statische Reparatur-Sperren. Keine Ausfuehrung oder Simulation von Swift.

Prueft die Quellverdrahtung der nativen Regressionen; semantisches PASS braucht
weiterhin Swift Testing, SwiftData und XCUITest am exakten Kandidaten.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TASK = "produkt/Packages/Sources/TaskEngine/TaskEngine.swift"
LEARNING = "produkt/Packages/Sources/LearningEngine/LearningEngine.swift"
EVENT = "produkt/Packages/Sources/ObservationLog/Event.swift"
NOTEBOOK = "produkt/App/Chnobel/Views/NotebookView.swift"
REPORT = "produkt/App/Chnobel/Views/ReportView.swift"
SESSION = "produkt/App/Chnobel/NotebookSession.swift"
STORE = "produkt/App/Chnobel/Persistence/NotebookStore.swift"
DOMAIN = "produkt/Packages/Sources/CoreDomain/Domain.swift"
SOURCE_PATHS = [TASK, LEARNING, EVENT, NOTEBOOK, REPORT, SESSION, STORE, DOMAIN]
REGRESSION_FILES = {
    "produkt/Packages/Tests/LearningEngineTests/ActorAnchorTests.swift": (10, "@Test"),
    "produkt/Packages/Tests/LearningEngineTests/AnswerCurrencyTests.swift": (8, "@Test"),
    "produkt/Packages/Tests/TaskEngineTests/RepairContractTests.swift": (16, "@Test"),
    "produkt/App/ChnobelTests/RepairSessionTests.swift": (9, "@Test"),
    "produkt/App/ChnobelUITests/RepairNotebookUITests.swift": (6, "func test"),
}


class RepairAuditError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise RepairAuditError(message)


def section(text, start, end):
    require(text.count(start) == 1, "Quellabschnitt nicht eindeutig: " + start)
    return text.split(start, 1)[1].split(end, 1)[0]


def sources():
    return {path: (ROOT / path).read_text(encoding="utf-8") for path in SOURCE_PATHS}


def check_baseline(texts=None):
    baseline = json.loads((Path(__file__).parent / "repair-baseline.json").read_text(encoding="utf-8"))
    if texts is None:
        texts = {path: (ROOT / path).read_text(encoding="utf-8") for path in baseline["files"]}
    require(set(texts) == set(baseline["files"]), "Bestehender Test fehlt")
    for path, digest in baseline["files"].items():
        actual = hashlib.sha256(texts[path].replace("\r\n", "\n").encode("utf-8")).hexdigest()
        require(actual == digest, "Bestehender Test veraendert: " + path)
    return len(baseline["files"])


def check_regressions(texts=None):
    if texts is None:
        texts = {path: (ROOT / path).read_text(encoding="utf-8") for path in REGRESSION_FILES}
    require(set(texts) == set(REGRESSION_FILES), "Neue native Regressionsdatei fehlt")
    for path, (minimum, marker) in REGRESSION_FILES.items():
        text = texts[path]
        require(text.count(marker) >= minimum, "Native Regressionen fehlen: " + path)
        require(not re.search(r"XCTSkip|\.disabled\(|\.enabled\(", text),
                "Native Regression wird uebersprungen: " + path)
    return {"definitions_present": "PASS", "execution": "NOT RUN"}


def check_repair_sources(data):
    task, learning = data[TASK], data[LEARNING]
    require("if event.sequence != state.lastSequence + 1 { state.observeGap() }" in task,
            "Seq-Luecke invalidiert Antwortaktualitaet nicht")
    require("if condition == .gapDetected { state.observeGap() }" in task,
            "Explizite Luecke invalidiert Antwortaktualitaet nicht")
    gap = section(task, "mutating func observeGap()", "mutating func anchorMaterialAction")
    require("answerCurrency = .unknown" in gap and "answer = nil" not in gap,
            "Luecke muss Aktualitaet unbekannt setzen, nicht Antwortgeschichte loeschen")
    commit = section(task, "case .answerCommitted(let answer):", "case .responseRetracted")
    require("state.answerCurrency != .yes" in commit and "state.answerCurrency = .yes" in commit,
            "Neue Antwort nach Luecke nicht wieder beurteilbar")
    require("let result: Truth = state.answerCurrency == .yes" in learning and ": .unknown" in learning,
            "Ergebnis ohne Antwortaktualitaet")
    require("state.answer == nil || state.answerCurrency != .yes" in task,
            "Abschluss mit alter Antwort erlaubt")
    require("session.state.answerCurrency != .yes" in data[NOTEBOOK] and "Aktualität offen" in data[REPORT],
            "UI verschweigt unbekannte Antwortaktualitaet")

    reading = section(task, "case .recognitionProposed(let reading):", "case .answerCommitted")
    require("isDirectNumber(reading.text)" in reading, "Nichtnumerische Lesart zugelassen")
    require("(answer.origin == .confirmed) == (proposedValue == answer.value)" in commit,
            "Bestaetigung und Korrektur nicht disjunkt")
    undo = section(task, "case .actionUndone(let target):", "case .supportPresented")
    require("event.actor == last.event.actor" in undo, "Undo-Akteur nicht an Ursprungszug gebunden")
    require(".actionUndone(eventID: move.event.id), actor: move.event.actor" in task,
            "Undo-Helfer erfindet Lernendenakteur")

    require(".supportPresented(supportForState(state))" in task and
            "guard support == supportForState(state)" in task, "Hilfeauswahl nicht zustandsgebunden")
    for counts, variant in [("8, 7, 0", "tenStep"), ("9, 6, 0", "tenFromNineV1"),
                            ("10, 5, 0", "tenAlreadyV1"), ("7, 7, 1", "tenFromDoublesV1")]:
        require(f"case ({counts}): return .{variant}" in task, "Hilfefall fehlt: " + counts)
        require(variant in data[EVENT], "Protokollierte Hilfevariante fehlt")
    move = section(task, "case .materialMoved(let move):", "case .actionUndone")
    require("state.shownSupport = nil" in move and "state.shownSupport = nil" in undo,
            "Zustandsfremder Tipp bleibt nach Materialaenderung sichtbar")
    require("Label(support.text" in data[NOTEBOOK] and "Text(support.text)" in data[REPORT],
            "Sichtbarer und protokollierter Hilfetext getrennt")
    presentation = section(task, "public static func presentSupport", "public static func undo")
    require(".materialMoved" not in presentation and "TaskEngine.open" not in presentation,
            "Hilfe setzt Material still zurueck")

    anchor = section(task, "mutating func anchorMaterialAction", "public var canUndo")
    child = section(anchor, "if event.actor == .learner {", "} else if event.actor == .app {")
    app = anchor.split("} else if event.actor == .app {", 1)[-1]
    require("currentTenAnchor = nil" in child and "retainedLearnerTenAnchor = nil" in child and
            "historicalTenAnchors.append(anchor)" in child and "[supportBefore]" in child,
            "Eigene Rueckkehr/Undo erhaelt keinen neuen Anker")
    require("anchor.positions == positions" in app and "currentTenAnchor = anchor" in app and
            "RepresentationAnchor(" not in app and "historicalTenAnchors.append" not in app,
            "App-Rueckkehr datiert Kind-Aktion neu")
    require("state.anchorMaterialAction(event, supportBefore: before)" in move and
            "state.anchorMaterialAction(event, supportBefore: before)" in undo,
            "Bewegung oder Undo umgeht Aktionsanker")
    require("state.currentTenAnchor?.tenSupportBefore" in learning and
            "historicalTenWithoutHint: historical" in learning, "Historie und aktueller Weg vermischt")

    require('rules: "local-draft-1"' in data[DOMAIN] and "localFormat == 1" in data[STORE],
            "Neue Semantik ohne lokale Versionsgrenze")
    apply = section(data[SESSION], "private func apply(", "} catch")
    require(apply.index("try store.save") < apply.index("ledger = next"), "UI publiziert vor Persistenz")
    require("context.rollback()" in data[STORE], "Fehlgeschlagener Save ohne Rollback")
    return {"source_wiring": "PASS", "swift_semantics": "NOT RUN"}
