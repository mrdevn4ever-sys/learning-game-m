import CoreDomain
import Foundation
import ObservationLog
import SwiftData
import TaskEngine
import Testing
@testable import Chnobel

@MainActor
private func repairStoreURL() throws -> URL {
    let base = try FileManager.default.url(for: .applicationSupportDirectory, in: .userDomainMask, appropriateFor: nil, create: true)
    return base.appendingPathComponent("ChnobelRepairTests/" + UUID().uuidString, isDirectory: true).appendingPathComponent("test.store")
}

@MainActor
private func place(_ items: [String], in zone: Zone, session: NotebookSession) {
    for item in items { session.select(item) }
    session.place(in: zone)
}

@Test @MainActor func staleAnswerRestoresAsUnknownAndNewAnswerRestoresAsCurrent() throws {
    for missingSequence in [false, true] {
        for text in ["15", "14"] {
            let url = try repairStoreURL()
            let store = try NotebookStore(url: url)
            var ledger = try TaskEngine.submit(text, to: TaskEngine.open())
            if missingSequence {
                try ledger.append(Event(streamID: ledger.streamID, sequence: ledger.nextSequence + 1,
                    actor: .system, payload: .conditionObserved(.uncertainClock)))
            } else {
                try ledger.record(.conditionObserved(.gapDetected), actor: .system)
            }
            try store.save(ledger: ledger, draft: "")
            let session = try NotebookSession(store: NotebookStore(url: url))
            #expect(session.state.answerCurrency == .unknown)
            #expect(session.evidence.report.result == .unknown)
            session.finish()
            #expect(!session.state.isClosed)
            #expect(session.errorText != nil)
            session.digit(1)
            session.digit(5)
            session.submit()
            #expect(session.state.answerCurrency == .yes)
            #expect(session.evidence.report.result == .yes)
            let restored = try NotebookSession(store: NotebookStore(url: url))
            #expect(restored.ledger == session.ledger)
            #expect(restored.evidence.report.result == .yes)
        }
    }
}

@Test @MainActor func stateAwareHelpAndUndoPersistWithoutSilentReset() throws {
    let url = try repairStoreURL()
    let session = try NotebookSession(store: NotebookStore(url: url))
    place(["b1"], in: .left, session: session)
    let before = session.state.positions
    session.showHelp()
    #expect(session.state.positions == before)
    #expect(session.state.shownSupport == .tenFromNineV1)
    let restored = try NotebookSession(store: NotebookStore(url: url))
    #expect(restored.state.shownSupport == .tenFromNineV1)
    #expect(restored.ledger == session.ledger)
    restored.undo()
    #expect(restored.state.positions == DevelopmentTask.initialPositions)
    #expect(restored.state.shownSupport == nil)
    #expect(restored.state.hasTenSupport)
    restored.showHelp()
    let again = try NotebookSession(store: NotebookStore(url: url))
    #expect(again.state.shownSupport == .tenStep)
    #expect(again.state.supportCount == 2)
    #expect(again.ledger.events.contains { $0.payload == .supportPresented(.tenFromNineV1) })
}

@Test @MainActor func helpPreservesTenAndAlternativeLayoutsAcrossRestart() throws {
    for alternative in [false, true] {
        let url = try repairStoreURL()
        let session = try NotebookSession(store: NotebookStore(url: url))
        if alternative { place(["a1"], in: .spare, session: session) }
        else { place(["b1", "b2"], in: .left, session: session) }
        let positions = session.state.positions
        session.showHelp()
        let restored = try NotebookSession(store: NotebookStore(url: url))
        #expect(restored.state.positions == positions)
        #expect(restored.state.shownSupport == (alternative ? .tenFromDoublesV1 : .tenAlreadyV1))
        #expect(restored.ledger.events.last?.payload == .supportPresented(alternative ? .tenFromDoublesV1 : .tenAlreadyV1))
    }
}

@Test @MainActor func ownDetourReturnAndUndoStayGuidedAcrossRestart() throws {
    for useUndo in [false, true] {
        let url = try repairStoreURL()
        let session = try NotebookSession(store: NotebookStore(url: url))
        place(["b1", "b2"], in: .left, session: session)
        let originalAnchor = session.state.currentTenAnchor
        place(["a1"], in: .spare, session: session)
        session.showHelp()
        if useUndo { session.undo() }
        else { place(["a1"], in: .left, session: session) }
        let restored = try NotebookSession(store: NotebookStore(url: url))
        #expect(restored.state.currentTenAnchor != originalAnchor)
        #expect(restored.evidence.report.tenWithHint == .yes)
        #expect(restored.evidence.report.tenWithoutHint == .no)
        #expect(restored.evidence.report.historicalTenWithoutHint == .yes)
        #expect(restored.ledger == session.ledger)
    }
}

@Test @MainActor func appUndoPersistsOriginalActorAndUnchangedLearnerAnchor() throws {
    let url = try repairStoreURL()
    let store = try NotebookStore(url: url)
    var ledger = try TaskEngine.move(items: ["b1", "b2"], to: .left, in: TaskEngine.open())
    let original = try TaskEngine.replay(ledger).currentTenAnchor
    try ledger.record(.materialMoved(MaterialMove(items: ["a1"], from: .left,
        to: .spare, method: .appDemo)), actor: .app)
    ledger = try TaskEngine.presentSupport(in: ledger)
    try store.save(ledger: ledger, draft: "")
    let session = try NotebookSession(store: store)
    session.undo()
    #expect(session.ledger.events.last?.actor == .app)
    let restored = try NotebookSession(store: NotebookStore(url: url))
    #expect(restored.state.currentTenAnchor == original)
    #expect(restored.evidence.report.tenWithoutHint == .yes)
    #expect(restored.evidence.report.tenWithHint == .no)
}

private enum InjectedSaveError: Error { case refused }

@Test @MainActor func failedSaveRollsBackDiskAndDoesNotPublishHelpOrMoves() throws {
    let url = try repairStoreURL()
    var failWrites = false
    let store = try NotebookStore(url: url, beforeSave: {
        if failWrites { throw InjectedSaveError.refused }
    })
    let session = try NotebookSession(store: store)
    place(["b1"], in: .left, session: session)
    let ledger = session.ledger
    let state = session.state
    let evidence = session.evidence
    failWrites = true
    session.showHelp()
    #expect(session.errorText != nil)
    #expect(session.ledger == ledger)
    #expect(session.state == state)
    #expect(session.evidence == evidence)
    #expect(try store.load()?.validatedLedger() == ledger)
    place(["b2"], in: .left, session: session)
    #expect(session.ledger == ledger)
    #expect(session.state == state)
    let restored = try NotebookSession(store: NotebookStore(url: url))
    #expect(restored.ledger == ledger)
    #expect(restored.state == state)
    failWrites = false
    session.showHelp()
    #expect(session.state.shownSupport == .tenFromNineV1)
}

@Test @MainActor func savedEventsBeforeSessionPublicationAreRecovered() throws {
    let url = try repairStoreURL()
    let store = try NotebookStore(url: url)
    let session = try NotebookSession(store: store)
    let next = try TaskEngine.presentSupport(in: session.ledger)
    // Simulierte Prozessgrenze nach Save, vor Veröffentlichung im alten Sessionobjekt.
    try store.save(ledger: next, draft: "1")
    #expect(session.state.shownSupport == nil)
    let restored = try NotebookSession(store: NotebookStore(url: url))
    #expect(restored.ledger == next)
    #expect(restored.state.shownSupport == .tenStep)
    #expect(restored.draft.text == "1")
}

@Test @MainActor func oldAndUnknownLocalFormatsAreRejectedWithoutReplacement() throws {
    for format in [0, 999] {
        let url = try repairStoreURL()
        let store = try NotebookStore(url: url)
        _ = try NotebookSession(store: store)
        let context = ModelContext(store.container)
        let record = try #require(context.fetch(FetchDescriptor<NotebookArchive>()).first)
        var object = try #require(JSONSerialization.jsonObject(with: record.payload) as? [String: Any])
        object["localFormat"] = format
        let incompatible = try JSONSerialization.data(withJSONObject: object)
        record.payload = incompatible
        try context.save()
        #expect(throws: NotebookStoreError.unsupportedFormat) { try NotebookSession(store: NotebookStore(url: url)) }
        let readback = ModelContext(store.container)
        #expect(try readback.fetch(FetchDescriptor<NotebookArchive>()).first?.payload == incompatible)
    }
}

@Test @MainActor func invalidReadingCannotReplaceLastValidStoredAnswer() throws {
    let url = try repairStoreURL()
    let store = try NotebookStore(url: url)
    let good = try TaskEngine.submit("15", to: TaskEngine.open())
    try store.save(ledger: good, draft: "")
    var invalid = try TaskEngine.open()
    let input = CapturedInput(mode: .handwriting, text: "synthetic-strokes")
    try invalid.record(.inputCaptured(input), actor: .learner)
    try invalid.record(.recognitionProposed(ProposedReading(inputID: input.id, text: "abc")), actor: .app)
    #expect(throws: TaskError.invalidReading) { try store.save(ledger: invalid, draft: "") }
    let restored = try NotebookSession(store: NotebookStore(url: url))
    #expect(restored.ledger == good)
    #expect(restored.evidence.report.result == .yes)
}
