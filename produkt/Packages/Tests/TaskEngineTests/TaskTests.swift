import CoreDomain
import Foundation
import ObservationLog
import TaskEngine
import Testing

@Test func initialMaterialIsEightAndSevenNotASolution() throws {
    let state = try TaskEngine.replay(TaskEngine.open())
    #expect(state.items(in: .left).count == 8)
    #expect(state.items(in: .right).count == 7)
    #expect(state.items(in: .spare).isEmpty)
    #expect(!state.isTenLayout)
    #expect(state.answer == nil)
    #expect(state.activeMoves.isEmpty)
}

@Test func directAnswerHasCapturedInputAndCommit() throws {
    let ledger = try TaskEngine.submit("15", to: TaskEngine.open())
    #expect(ledger.events.map(\.payload.name) == ["attempt.opened", "input.captured", "answer.committed"])
    #expect(try TaskEngine.replay(ledger).answer?.answer.origin == .direct)
}

@Test func correctionRetractsOldAnswer() throws {
    let initial = try TaskEngine.submit("16", to: TaskEngine.open())
    let corrected = try TaskEngine.submit("15", to: initial)
    #expect(corrected.events.contains { if case .responseRetracted = $0.payload { return true }; return false })
    #expect(try TaskEngine.replay(corrected).answer?.answer.value == 15)
}

@Test func invalidDirectInputsAreRejected() throws {
    let ledger = try TaskEngine.open()
    for text in ["", "-1", "1.5", "1000", " 15", "１５"] {
        #expect(throws: TaskError.invalidInput) { try TaskEngine.submit(text, to: ledger) }
    }
}

@Test func movesAreUserSelectedAndUndoRestoresExactly() throws {
    let initial = try TaskEngine.open()
    let moved = try TaskEngine.move(items: ["b4", "b6"], to: .left, in: initial)
    #expect(try TaskEngine.replay(moved).isTenLayout)
    let undone = try TaskEngine.undo(in: moved)
    #expect(try TaskEngine.replay(undone).positions == DevelopmentTask.initialPositions)
    #expect(undone.events.count > moved.events.count)
}

@Test func invalidMoveDoesNotManufactureMaterial() throws {
    let ledger = try TaskEngine.open()
    #expect(throws: TaskError.invalidMove) { try TaskEngine.move(items: ["b1", "b1"], to: .left, in: ledger) }
    #expect(throws: TaskError.invalidMove) { try TaskEngine.move(items: ["missing"], to: .left, in: ledger) }
    #expect(throws: TaskError.invalidMove) { try TaskEngine.move(items: ["a1", "b1"], to: .spare, in: ledger) }
}

@Test func undoAnswerDoesNotUndoEarlierMove() throws {
    let moved = try TaskEngine.move(items: ["b1", "b2"], to: .left, in: TaskEngine.open())
    let answered = try TaskEngine.submit("15", to: moved)
    let undone = try TaskEngine.undo(in: answered)
    let state = try TaskEngine.replay(undone)
    #expect(state.answer == nil)
    #expect(state.isTenLayout)
}

@Test func helpNeverMovesAnyMaterial() throws {
    let ledger = try TaskEngine.presentSupport(in: TaskEngine.open())
    let state = try TaskEngine.replay(ledger)
    #expect(state.positions == DevelopmentTask.initialPositions)
    #expect(state.shownSupport?.text == Support.tenStep.text)
    #expect(state.supportCount == 1)
}

@Test func closedAttemptHasAnActualEnd() throws {
    let closed = try TaskEngine.close(TaskEngine.submit("15", to: TaskEngine.open()), reason: .finished)
    #expect(try TaskEngine.replay(closed).isClosed)
    #expect(throws: TaskError.closedAttempt) { try TaskEngine.submit("14", to: closed) }
    #expect(throws: TaskError.closedAttempt) { try TaskEngine.presentSupport(in: closed) }
}

@Test func mismatchedActorsAndUnsupportedRevisionsFailClosed() throws {
    var falseHelp = try TaskEngine.open()
    try falseHelp.record(.supportPresented(.tenStep), actor: .learner)
    #expect(throws: TaskError.invalidActor) { try TaskEngine.replay(falseHelp) }
    var future = try EventLedger(streamID: UUID())
    try future.record(.opened(Opening(profileID: DevelopmentTask.profileID, taskID: DevelopmentTask.id,
                                     initialBoardID: DevelopmentTask.boardID,
                                     revision: Revision(content: "unsupported", rules: "unsupported", evaluation: "unsupported"))), actor: .system)
    #expect(throws: TaskError.unsupportedRevision) { try TaskEngine.replay(future) }
}

@Test func orphanCorrectionIsRejected() throws {
    var ledger = try TaskEngine.open()
    try ledger.record(.answerCommitted(CommittedAnswer(value: 15, inputID: UUID(), origin: .corrected, readingID: UUID())), actor: .learner)
    #expect(throws: TaskError.invalidAnswer) { try TaskEngine.replay(ledger) }
}
