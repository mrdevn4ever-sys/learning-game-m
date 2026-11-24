import CoreDomain
import Foundation
import LearningEngine
import ObservationLog
import TaskEngine
import Testing

private func ten(_ ledger: EventLedger) throws -> EventLedger {
    try TaskEngine.move(items: ["b1", "b2"], to: .left, in: ledger)
}

@Test func resultHasPositiveNegativeAndUnknownCases() throws {
    let empty = try TaskEngine.open()
    #expect(try LearningEngine.report(from: TaskEngine.submit("15", to: empty)).result == .yes)
    #expect(try LearningEngine.report(from: TaskEngine.submit("14", to: empty)).result == .no)
    #expect(try LearningEngine.report(from: empty).result == .unknown)
}

@Test func answerAloneNeverProvesAPath() throws {
    let report = try LearningEngine.report(from: TaskEngine.submit("15", to: TaskEngine.open()))
    #expect(report.result == .yes)
    #expect(report.tenRepresentation == .no)
    #expect(report.tenWithoutHint == .no)
    #expect(report.doublesRepresentation == .no)
}

@Test func ownTenStepWithoutHintIsRecognized() throws {
    let report = try LearningEngine.report(from: ten(TaskEngine.open()))
    #expect(report.tenRepresentation == .yes)
    #expect(report.tenWithoutHint == .yes)
    #expect(report.tenWithHint == .no)
    #expect(report.result == .unknown)
}

@Test func hintBeforeMoveOnlyAllowsGuidedClaim() throws {
    let report = try LearningEngine.report(from: ten(TaskEngine.presentSupport(in: TaskEngine.open())))
    #expect(report.tenRepresentation == .yes)
    #expect(report.tenWithoutHint == .no)
    #expect(report.tenWithHint == .yes)
}

@Test func hintAfterEffectiveMoveDoesNotRetroactivelyDowngrade() throws {
    let ledger = try TaskEngine.presentSupport(in: ten(TaskEngine.open()))
    let report = try LearningEngine.report(from: ledger)
    #expect(report.tenWithoutHint == .yes)
    #expect(report.tenWithHint == .no)
}

@Test func undoThenRepeatAfterHintIsGuided() throws {
    let moved = try ten(TaskEngine.open())
    let hinted = try TaskEngine.presentSupport(in: moved)
    let undone = try TaskEngine.undo(in: hinted)
    #expect(try LearningEngine.report(from: undone).tenRepresentation == .no)
    let report = try LearningEngine.report(from: ten(undone))
    #expect(report.tenWithoutHint == .no)
    #expect(report.tenWithHint == .yes)
}

@Test func hintBetweenTwoPartialMovesAppliesToSecondMove() throws {
    let first = try TaskEngine.move(items: ["b1"], to: .left, in: TaskEngine.open())
    let hinted = try TaskEngine.presentSupport(in: first)
    let second = try TaskEngine.move(items: ["b2"], to: .left, in: hinted)
    #expect(try LearningEngine.report(from: second).tenWithHint == .yes)
}

@Test func gapKeepsResultButBlocksIndependentPath() throws {
    var ledger = try TaskEngine.open()
    try ledger.record(.conditionObserved(.gapDetected), actor: .system)
    ledger = try TaskEngine.submit("15", to: ten(ledger))
    let report = try LearningEngine.report(from: ledger)
    #expect(report.result == .yes)
    #expect(report.tenRepresentation == .unknown)
    #expect(report.tenWithoutHint == .unknown)
}

@Test func missingSequenceIsUnknownNotHintAbsence() throws {
    var ledger = try TaskEngine.open()
    try ledger.append(Event(streamID: ledger.streamID, sequence: 3, actor: .learner,
                            payload: .materialMoved(MaterialMove(items: ["b1", "b2"], from: .right, to: .left, method: .tap))))
    #expect(try LearningEngine.report(from: ledger).tenWithoutHint == .unknown)
}

@Test func alternativeSevenSevenOneIsRecognizedSeparately() throws {
    let ledger = try TaskEngine.move(items: ["a3"], to: .spare, in: TaskEngine.open())
    let report = try LearningEngine.report(from: ledger)
    #expect(report.doublesRepresentation == .yes)
    #expect(report.tenRepresentation == .no)
}

@Test func alternatePathAlsoHasNegativeAndUnknownCases() throws {
    #expect(try LearningEngine.report(from: TaskEngine.open()).doublesRepresentation == .no)
    var incomplete = try TaskEngine.open()
    try incomplete.record(.conditionObserved(.gapDetected), actor: .system)
    incomplete = try TaskEngine.move(items: ["a1"], to: .spare, in: incomplete)
    #expect(try LearningEngine.report(from: incomplete).doublesRepresentation == .unknown)
}

@Test func appDemoIsNotAnOwnPathAndRepetitionIsNotIndependent() throws {
    var demo = try TaskEngine.open()
    try demo.record(.materialMoved(MaterialMove(items: ["b1", "b2"], from: .right, to: .left, method: .appDemo)), actor: .app)
    #expect(try LearningEngine.report(from: demo).tenRepresentation == .no)
    let repeated = try ten(TaskEngine.undo(in: demo))
    #expect(try LearningEngine.report(from: repeated).tenWithHint == .yes)
    #expect(try LearningEngine.report(from: repeated).tenWithoutHint == .no)
}

@Test func unrelatedAppMovementIsNotInventedAsATenHint() throws {
    var demo = try TaskEngine.open()
    try demo.record(.materialMoved(MaterialMove(items: ["a1"], from: .left, to: .spare, method: .appDemo)), actor: .app)
    let ownPath = try ten(TaskEngine.undo(in: demo))
    let report = try LearningEngine.report(from: ownPath)
    #expect(report.tenRepresentation == .yes)
    #expect(report.tenWithoutHint == .unknown)
    #expect(report.tenWithHint == .unknown)
}

@Test func proposedMisreadingNeverBecomesAnError() throws {
    var ledger = try TaskEngine.open()
    let input = CapturedInput(mode: .handwriting, text: "synthetic-strokes")
    let reading = ProposedReading(inputID: input.id, text: "16")
    try ledger.record(.inputCaptured(input), actor: .learner)
    try ledger.record(.recognitionProposed(reading), actor: .app)
    #expect(try LearningEngine.report(from: ledger).result == .unknown)
    try ledger.record(.answerCommitted(CommittedAnswer(value: 15, inputID: input.id, origin: .corrected, readingID: reading.id)), actor: .learner)
    #expect(try LearningEngine.report(from: ledger).result == .yes)
}

@Test func duplicateMoveDoesNotChangeEvidence() throws {
    var ledger = try ten(TaskEngine.open())
    let before = try LearningEngine.report(from: ledger)
    try ledger.append(ledger.events[1])
    #expect(try LearningEngine.report(from: ledger) == before)
}

@Test func restoredReportComesFromEventsNotSavedClaims() throws {
    let ledger = try TaskEngine.submit("15", to: TaskEngine.presentSupport(in: ten(TaskEngine.open())))
    let encoded = try JSONEncoder().encode(ledger.events)
    let restored = try EventLedger(streamID: ledger.streamID, events: JSONDecoder().decode([Event].self, from: encoded))
    #expect(try LearningEngine.report(from: restored) == LearningEngine.report(from: ledger))
}

@Test func retractedAnswerIsNoLongerEvaluated() throws {
    let ledger = try TaskEngine.undo(in: TaskEngine.submit("14", to: TaskEngine.open()))
    #expect(try LearningEngine.report(from: ledger).result == .unknown)
}

@Test func abandonedAttemptHasNoInventedAnswer() throws {
    let ledger = try TaskEngine.close(TaskEngine.open(), reason: .abandoned)
    #expect(try LearningEngine.report(from: ledger).result == .unknown)
}
