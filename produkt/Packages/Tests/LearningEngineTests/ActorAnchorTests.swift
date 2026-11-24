import CoreDomain
import Foundation
import LearningEngine
import ObservationLog
import TaskEngine
import Testing

private func freelyLaidTen() throws -> EventLedger {
    try TaskEngine.move(items: ["b1", "b2"], to: .left, in: TaskEngine.open())
}

@Test func ownInitialTokenDetourAndReturnAfterHelpIsCurrentlyGuided() throws {
    let free = try freelyLaidTen()
    let freeAnchor = try #require(TaskEngine.replay(free).currentTenAnchor)
    let detour = try TaskEngine.move(items: ["a1"], to: .spare, in: free)
    #expect(try TaskEngine.replay(detour).currentTenAnchor == nil)
    #expect(try LearningEngine.report(from: detour).tenRepresentation == .no)
    #expect(try LearningEngine.report(from: detour).historicalTenWithoutHint == .yes)
    let hinted = try TaskEngine.presentSupport(in: detour)
    let returned = try TaskEngine.move(items: ["a1"], to: .left, in: hinted)
    let state = try TaskEngine.replay(returned)
    let report = try LearningEngine.report(from: returned)
    #expect(state.currentTenAnchor?.eventID == returned.events.last?.id)
    #expect(state.currentTenAnchor?.eventID != freeAnchor.eventID)
    #expect(state.historicalTenAnchors.first == freeAnchor)
    #expect(state.historicalTenAnchors.count == 2)
    #expect(report.tenRepresentation == .yes)
    #expect(report.tenWithoutHint == .no)
    #expect(report.tenWithHint == .yes)
    #expect(report.historicalTenWithoutHint == .yes)
}

@Test func ownDetourAndUndoAfterHelpHasNewLearnerAnchor() throws {
    let free = try freelyLaidTen()
    let detour = try TaskEngine.move(items: ["b1"], to: .right, in: free)
    let returned = try TaskEngine.undo(in: TaskEngine.presentSupport(in: detour))
    let state = try TaskEngine.replay(returned)
    #expect(state.currentTenAnchor?.eventID == returned.events.last?.id)
    #expect(state.currentTenAnchor?.actor == .learner)
    #expect(state.currentTenAnchor?.tenSupportBefore == .yes)
    let report = try LearningEngine.report(from: returned)
    #expect(report.tenRepresentation == .yes)
    #expect(report.tenWithoutHint == .no)
    #expect(report.tenWithHint == .yes)
    #expect(report.historicalTenWithoutHint == .yes)
}

@Test func laterHelpAloneKeepsExactCurrentAndHistoricalAnchor() throws {
    let free = try freelyLaidTen()
    let original = try TaskEngine.replay(free)
    let hinted = try TaskEngine.presentSupport(in: free)
    let state = try TaskEngine.replay(hinted)
    #expect(state.currentTenAnchor == original.currentTenAnchor)
    #expect(state.historicalTenAnchors == original.historicalTenAnchors)
    #expect(try LearningEngine.report(from: hinted).tenWithoutHint == .yes)
    #expect(try LearningEngine.report(from: hinted).tenWithHint == .no)
}

@Test func appDetourAndAppUndoRestoreUnchangedLearnerAnchorNotGuided() throws {
    for item in ["a1", "b1"] {
        for explicitHelp in [false, true] {
            var ledger = try freelyLaidTen()
            let original = try TaskEngine.replay(ledger)
            try ledger.record(.materialMoved(MaterialMove(items: [item], from: .left,
                to: .spare, method: .appDemo)), actor: .app)
            #expect(try TaskEngine.replay(ledger).currentTenAnchor == nil)
            #expect(try LearningEngine.report(from: ledger).historicalTenWithoutHint == .yes)
            if explicitHelp { ledger = try TaskEngine.presentSupport(in: ledger) }
            ledger = try TaskEngine.undo(in: ledger)
            let state = try TaskEngine.replay(ledger)
            let report = try LearningEngine.report(from: ledger)
            #expect(ledger.events.last?.actor == .app)
            #expect(state.currentTenAnchor == original.currentTenAnchor)
            #expect(state.historicalTenAnchors == original.historicalTenAnchors)
            #expect(report.tenRepresentation == .yes)
            #expect(report.tenWithoutHint == .yes)
            #expect(report.tenWithHint == .no)
            #expect(report.historicalTenWithoutHint == .yes)
        }
    }
}

@Test func nestedAppDetoursDoNotManufactureLearnerActions() throws {
    var ledger = try freelyLaidTen()
    let original = try TaskEngine.replay(ledger)
    for item in ["a1", "a2"] {
        try ledger.record(.materialMoved(MaterialMove(items: [item], from: .left,
            to: .spare, method: .appDemo)), actor: .app)
    }
    ledger = try TaskEngine.presentSupport(in: ledger)
    ledger = try TaskEngine.undo(in: TaskEngine.undo(in: ledger))
    #expect(try TaskEngine.replay(ledger).currentTenAnchor == original.currentTenAnchor)
    #expect(try TaskEngine.replay(ledger).historicalTenAnchors == original.historicalTenAnchors)
    #expect(try LearningEngine.report(from: ledger).tenWithoutHint == .yes)
}

@Test func learnerInterventionCannotResumeSuspendedOldAnchor() throws {
    var ledger = try freelyLaidTen()
    let original = try #require(TaskEngine.replay(ledger).currentTenAnchor)
    try ledger.record(.materialMoved(MaterialMove(items: ["a1"], from: .left,
        to: .spare, method: .appDemo)), actor: .app)
    ledger = try TaskEngine.presentSupport(in: ledger)
    ledger = try TaskEngine.move(items: ["a2"], to: .spare, in: ledger)
    ledger = try TaskEngine.undo(in: ledger)
    ledger = try TaskEngine.undo(in: ledger)
    let state = try TaskEngine.replay(ledger)
    #expect(state.isTenLayout)
    #expect(state.currentTenAnchor == nil)
    #expect(state.historicalTenAnchors.first == original)
    let report = try LearningEngine.report(from: ledger)
    #expect(report.tenRepresentation == .yes)
    #expect(report.tenWithoutHint == .unknown)
    #expect(report.tenWithHint == .unknown)
    #expect(report.historicalTenWithoutHint == .yes)
}

@Test func appRoundTripDoesNotEraseAnAlreadyGuidedLearnerAnchor() throws {
    var ledger = try TaskEngine.move(items: ["b1", "b2"], to: .left,
        in: TaskEngine.presentSupport(in: TaskEngine.open()))
    let original = try TaskEngine.replay(ledger)
    try ledger.record(.materialMoved(MaterialMove(items: ["a1"], from: .left,
        to: .spare, method: .appDemo)), actor: .app)
    ledger = try TaskEngine.undo(in: ledger)
    #expect(try TaskEngine.replay(ledger).currentTenAnchor == original.currentTenAnchor)
    #expect(try LearningEngine.report(from: ledger).tenWithHint == .yes)
    #expect(try LearningEngine.report(from: ledger).historicalTenWithoutHint == .no)
}

@Test func gapDoesNotReuseAnchorOrEraseEarlierObservedHistory() throws {
    var ledger = try freelyLaidTen()
    try ledger.record(.conditionObserved(.gapDetected), actor: .system)
    #expect(try TaskEngine.replay(ledger).currentTenAnchor == nil)
    #expect(try LearningEngine.report(from: ledger).tenWithoutHint == .unknown)
    #expect(try LearningEngine.report(from: ledger).historicalTenWithoutHint == .yes)
}

@Test func childReturnWithoutHintRetainsBothPositiveCases() throws {
    let detour = try TaskEngine.move(items: ["a1"], to: .spare, in: freelyLaidTen())
    for returned in [try TaskEngine.move(items: ["a1"], to: .left, in: detour),
                     try TaskEngine.undo(in: detour)] {
        #expect(try LearningEngine.report(from: returned).tenWithoutHint == .yes)
        #expect(try LearningEngine.report(from: returned).tenWithHint == .no)
        #expect(try TaskEngine.replay(returned).currentTenAnchor?.eventID == returned.events.last?.id)
    }
}

@Test func anchorHistoryRoundTripsThroughEventsNotStoredVerdicts() throws {
    let detour = try TaskEngine.move(items: ["b1"], to: .right, in: freelyLaidTen())
    let ledger = try TaskEngine.undo(in: TaskEngine.presentSupport(in: detour))
    let restored = try EventLedger(streamID: ledger.streamID,
        events: JSONDecoder().decode([Event].self, from: JSONEncoder().encode(ledger.events)))
    #expect(try TaskEngine.replay(restored) == TaskEngine.replay(ledger))
    #expect(try LearningEngine.report(from: restored) == LearningEngine.report(from: ledger))
}
