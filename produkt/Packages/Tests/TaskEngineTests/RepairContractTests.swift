import CoreDomain
import Foundation
import ObservationLog
import TaskEngine
import Testing

private func proposed(_ text: String) throws -> (EventLedger, CapturedInput, ProposedReading) {
    var ledger = try TaskEngine.open()
    let input = CapturedInput(mode: .handwriting, text: "synthetic-strokes")
    let reading = ProposedReading(inputID: input.id, text: text)
    try ledger.record(.inputCaptured(input), actor: .learner)
    try ledger.record(.recognitionProposed(reading), actor: .app)
    return (ledger, input, reading)
}

@Test func numericReadingsRejectMalformedTextAsIntegrityErrors() throws {
    for text in ["abc", "", " 15", "15 ", "-1", "+15", "1.5", "1e1", "1000", "１５", "١٥"] {
        let (ledger, _, _) = try proposed(text)
        #expect(throws: TaskError.invalidReading) { try TaskEngine.replay(ledger) }
    }
}

@Test func confirmedAndCorrectedOriginsAreDisjointByNumericValue() throws {
    for text in ["15", "015"] {
        let (base, input, reading) = try proposed(text)
        var confirmed = base
        try confirmed.record(.answerCommitted(CommittedAnswer(value: 15, inputID: input.id,
            origin: .confirmed, readingID: reading.id)), actor: .learner)
        #expect(try TaskEngine.replay(confirmed).answer?.answer.origin == .confirmed)
        var falseCorrection = base
        try falseCorrection.record(.answerCommitted(CommittedAnswer(value: 15, inputID: input.id,
            origin: .corrected, readingID: reading.id)), actor: .learner)
        #expect(throws: TaskError.invalidAnswer) { try TaskEngine.replay(falseCorrection) }
    }
}

@Test func changedNumericReadingRequiresCorrectionNotConfirmation() throws {
    let (base, input, reading) = try proposed("16")
    var corrected = base
    try corrected.record(.answerCommitted(CommittedAnswer(value: 15, inputID: input.id,
        origin: .corrected, readingID: reading.id)), actor: .learner)
    #expect(try TaskEngine.replay(corrected).answer?.answer.origin == .corrected)
    var falseConfirmation = base
    try falseConfirmation.record(.answerCommitted(CommittedAnswer(value: 15, inputID: input.id,
        origin: .confirmed, readingID: reading.id)), actor: .learner)
    #expect(throws: TaskError.invalidAnswer) { try TaskEngine.replay(falseConfirmation) }
}

@Test func correctionCannotBorrowAnotherInputsReading() throws {
    var (ledger, _, reading) = try proposed("16")
    let other = CapturedInput(mode: .handwriting, text: "other-synthetic-strokes")
    try ledger.record(.inputCaptured(other), actor: .learner)
    try ledger.record(.answerCommitted(CommittedAnswer(value: 15, inputID: other.id,
        origin: .corrected, readingID: reading.id)), actor: .learner)
    #expect(throws: TaskError.invalidAnswer) { try TaskEngine.replay(ledger) }
}

@Test func undoRetainsTheOriginalMoveActorForBothActors() throws {
    for actor in [CoreDomain.Actor.learner, .app] {
        var ledger = try TaskEngine.open()
        let move = try ledger.record(.materialMoved(MaterialMove(items: ["b1"], from: .right,
            to: .left, method: actor == .app ? .appDemo : .tap)), actor: actor)
        let undone = try TaskEngine.undo(in: ledger)
        #expect(undone.events.last?.actor == actor)
        #expect(undone.events.last?.payload == .actionUndone(eventID: move.id))
        #expect(try TaskEngine.replay(undone).positions == DevelopmentTask.initialPositions)
        var explicit = ledger
        try explicit.record(.actionUndone(eventID: move.id), actor: actor)
        #expect(try TaskEngine.replay(explicit).positions == DevelopmentTask.initialPositions)
    }
}

@Test func undoCannotImpersonateTheOtherActorOrSystem() throws {
    for originalActor in [CoreDomain.Actor.learner, .app] {
        var base = try TaskEngine.open()
        let move = try base.record(.materialMoved(MaterialMove(items: ["b1"], from: .right,
            to: .left, method: originalActor == .app ? .appDemo : .tap)), actor: originalActor)
        for wrong in [CoreDomain.Actor.learner, .app, .system] where wrong != originalActor {
            var ledger = base
            try ledger.record(.actionUndone(eventID: move.id), actor: wrong)
            #expect(throws: TaskError.invalidActor) { try TaskEngine.replay(ledger) }
        }
    }
}

@Test func matchingActorDoesNotPermitDuplicateOrNonLatestUndo() throws {
    let first = try TaskEngine.move(items: ["b1"], to: .left, in: TaskEngine.open())
    let second = try TaskEngine.move(items: ["b2"], to: .left, in: first)
    let firstID = try #require(first.events.last?.id)
    var invalid = second
    try invalid.record(.actionUndone(eventID: firstID), actor: .learner)
    #expect(throws: TaskError.invalidUndo) { try TaskEngine.replay(invalid) }
    var repeated = try TaskEngine.undo(in: first)
    try repeated.record(.conditionObserved(.gapDetected), actor: .system)
    try repeated.record(.actionUndone(eventID: firstID), actor: .learner)
    #expect(throws: TaskError.invalidUndo) { try TaskEngine.replay(repeated) }
}

@Test func helpForEightSevenAndNineSixLogsTheActualStep() throws {
    let initial = try TaskEngine.open()
    let nine = try TaskEngine.move(items: ["b1"], to: .left, in: initial)
    for (ledger, expected) in [(initial, Support.tenStep), (nine, Support.tenFromNineV1)] {
        let before = try TaskEngine.replay(ledger)
        let hinted = try TaskEngine.presentSupport(in: ledger)
        let after = try TaskEngine.replay(hinted)
        #expect(after.positions == before.positions)
        #expect(after.activeMoves == before.activeMoves)
        #expect(after.shownSupport == expected)
        #expect(hinted.events.last?.payload == .supportPresented(expected))
        #expect(hinted.events.last?.actor == .app)
    }
    let hinted = try TaskEngine.presentSupport(in: nine)
    let completed = try TaskEngine.move(items: ["b2"], to: .left, in: hinted)
    #expect(try TaskEngine.replay(completed).isTenLayout)
    #expect(try TaskEngine.replay(completed).shownSupport == nil)
}

@Test func helpForTenFiveDoesNotAskForAnotherMove() throws {
    let ten = try TaskEngine.move(items: ["b1", "b2"], to: .left, in: TaskEngine.open())
    let helped = try TaskEngine.presentSupport(in: ten)
    #expect(try TaskEngine.replay(helped).positions == TaskEngine.replay(ten).positions)
    #expect(try TaskEngine.replay(helped).shownSupport == .tenAlreadyV1)
    #expect(Support.tenAlreadyV1.text.contains("kein weiteres Plättchen"))
}

@Test func helpForSevenSevenOneKeepsTheAlternativeAndExplainsTheSwitch() throws {
    let alternate = try TaskEngine.move(items: ["a1"], to: .spare, in: TaskEngine.open())
    let hinted = try TaskEngine.presentSupport(in: alternate)
    #expect(try TaskEngine.replay(hinted).isDoublesLayout)
    #expect(try TaskEngine.replay(hinted).shownSupport == .tenFromDoublesV1)
    #expect(Support.tenFromDoublesV1.text.contains("anderer passender Weg"))
    let first = try TaskEngine.move(items: ["a1"], to: .left, in: hinted)
    let completed = try TaskEngine.move(items: ["b1", "b2"], to: .left, in: first)
    #expect(try TaskEngine.replay(completed).isTenLayout)
}

@Test func helpAfterUndoUsesRestoredCountsWithoutErasingEarlierHelp() throws {
    let nine = try TaskEngine.move(items: ["b1"], to: .left, in: TaskEngine.open())
    let helped = try TaskEngine.presentSupport(in: nine)
    let undone = try TaskEngine.undo(in: helped)
    let state = try TaskEngine.replay(undone)
    #expect(state.positions == DevelopmentTask.initialPositions)
    #expect(state.shownSupport == nil)
    #expect(state.hasTenSupport)
    #expect(state.supportCount == 1)
    let rehelped = try TaskEngine.presentSupport(in: undone)
    #expect(try TaskEngine.replay(rehelped).shownSupport == .tenStep)
    #expect(try TaskEngine.replay(rehelped).supportCount == 2)
    #expect(rehelped.events.contains { $0.payload == .supportPresented(.tenFromNineV1) })
}

@Test func stateForeignHelpIsRejectedInsteadOfSilentlyResetting() throws {
    var nine = try TaskEngine.move(items: ["b1"], to: .left, in: TaskEngine.open())
    try nine.record(.supportPresented(.tenStep), actor: .app)
    #expect(throws: TaskError.invalidSupport) { try TaskEngine.replay(nine) }
}

@Test func gapHelpGivesNoUnprovedSpecificMove() throws {
    var ledger = try TaskEngine.open()
    try ledger.record(.conditionObserved(.gapDetected), actor: .system)
    let hinted = try TaskEngine.presentSupport(in: ledger)
    #expect(try TaskEngine.replay(hinted).shownSupport == .tenUnknownV1)
}

@Test func finishedRequiresCurrentAnswerAfterEitherKindOfGap() throws {
    for missingSequence in [false, true] {
        var ledger = try TaskEngine.submit("15", to: TaskEngine.open())
        if missingSequence {
            try ledger.append(Event(streamID: ledger.streamID, sequence: ledger.nextSequence + 1,
                actor: .system, payload: .conditionObserved(.uncertainClock)))
        } else {
            try ledger.record(.conditionObserved(.gapDetected), actor: .system)
        }
        #expect(throws: TaskError.invalidAnswer) { try TaskEngine.close(ledger, reason: .finished) }
        let newAnswer = try TaskEngine.submit("15", to: ledger)
        #expect(try TaskEngine.replay(TaskEngine.close(newAnswer, reason: .finished)).isClosed)
    }
}

@Test func freshCommitAfterGapNeedsNoInventedRetractionOfUnknownActivity() throws {
    var ledger = try TaskEngine.submit("14", to: TaskEngine.open())
    try ledger.record(.conditionObserved(.gapDetected), actor: .system)
    let input = CapturedInput(mode: .numberPad, text: "15")
    try ledger.record(.inputCaptured(input), actor: .learner)
    try ledger.record(.answerCommitted(CommittedAnswer(value: 15, inputID: input.id, origin: .direct)), actor: .learner)
    #expect(try TaskEngine.replay(ledger).answerCurrency == .yes)
    #expect(try TaskEngine.replay(ledger).answer?.answer.value == 15)
    #expect(!ledger.events.contains { if case .responseRetracted = $0.payload { return true }; return false })
}

@Test func secondAnswerWithoutGapOrRetractionStillFails() throws {
    var ledger = try TaskEngine.submit("14", to: TaskEngine.open())
    let input = CapturedInput(mode: .numberPad, text: "15")
    try ledger.record(.inputCaptured(input), actor: .learner)
    try ledger.record(.answerCommitted(CommittedAnswer(value: 15, inputID: input.id, origin: .direct)), actor: .learner)
    #expect(throws: TaskError.invalidAnswer) { try TaskEngine.replay(ledger) }
}
