import CoreDomain
import Foundation
import LearningEngine
import ObservationLog
import TaskEngine
import Testing

private func gap(_ original: EventLedger, missingSequence: Bool) throws -> EventLedger {
    var ledger = original
    if missingSequence {
        try ledger.append(Event(streamID: ledger.streamID, sequence: ledger.nextSequence + 1,
            actor: .system, payload: .conditionObserved(.uncertainClock)))
    } else {
        try ledger.record(.conditionObserved(.gapDetected), actor: .system)
    }
    return ledger
}

@Test func explicitGapAfterAnswerMakesBothCorrectAndIncorrectResultsUnknown() throws {
    for text in ["15", "14"] {
        let ledger = try gap(TaskEngine.submit(text, to: TaskEngine.open()), missingSequence: false)
        let state = try TaskEngine.replay(ledger)
        #expect(state.answer?.answer.value == Int(text))
        #expect(state.answerCurrency == .unknown)
        let report = try LearningEngine.report(from: ledger)
        #expect(report.result == .unknown)
        #expect(report.resultText.contains("Beobachtungslücke"))
    }
}

@Test func sequenceGapAfterAnswerMakesBothCorrectAndIncorrectResultsUnknown() throws {
    for text in ["15", "14"] {
        let ledger = try gap(TaskEngine.submit(text, to: TaskEngine.open()), missingSequence: true)
        #expect(try LearningEngine.report(from: ledger).result == .unknown)
        #expect(try TaskEngine.replay(ledger).answerCurrency == .unknown)
    }
}

@Test func newAnswerAfterEitherGapIsAgainNarrowlyAssessable() throws {
    for missingSequence in [false, true] {
        for prior in [String?.none, "15", "14"] {
            var base = try TaskEngine.open()
            if let prior { base = try TaskEngine.submit(prior, to: base) }
            let interrupted = try gap(base, missingSequence: missingSequence)
            for fresh in ["15", "14"] {
                let ledger = try TaskEngine.submit(fresh, to: interrupted)
                #expect(try TaskEngine.replay(ledger).answerCurrency == .yes)
                #expect(try LearningEngine.report(from: ledger).result == (fresh == "15" ? .yes : .no))
                #expect(ledger.events.filter { if case .answerCommitted = $0.payload { return true }; return false }.count == (prior == nil ? 1 : 2))
                let restored = try EventLedger(streamID: ledger.streamID,
                    events: JSONDecoder().decode([Event].self, from: JSONEncoder().encode(ledger.events)))
                #expect(try LearningEngine.report(from: restored) == LearningEngine.report(from: ledger))
            }
        }
    }
}

@Test func anotherGapAfterFreshAnswerAgainMakesItsCurrencyUnknown() throws {
    var ledger = try gap(TaskEngine.submit("14", to: TaskEngine.open()), missingSequence: false)
    ledger = try TaskEngine.submit("15", to: ledger)
    #expect(try LearningEngine.report(from: ledger).result == .yes)
    ledger = try gap(ledger, missingSequence: true)
    #expect(try LearningEngine.report(from: ledger).result == .unknown)
}

@Test func retractingHistoricalAnswerAfterGapDoesNotProveNoCurrentAnswer() throws {
    let answered = try TaskEngine.submit("15", to: TaskEngine.open())
    let answer = try #require(TaskEngine.replay(answered).answer)
    var ledger = try gap(answered, missingSequence: false)
    #expect(try TaskEngine.replay(ledger).canUndo == false)
    try ledger.record(.responseRetracted(eventID: answer.eventID), actor: .learner)
    #expect(try TaskEngine.replay(ledger).answer == nil)
    #expect(try TaskEngine.replay(ledger).answerCurrency == .unknown)
    #expect(try LearningEngine.report(from: ledger).result == .unknown)
    #expect(try LearningEngine.report(from: TaskEngine.submit("15", to: ledger)).result == .yes)
}

@Test func uncertainClockAloneDoesNotInvalidateOrderedAnswer() throws {
    var ledger = try TaskEngine.submit("15", to: TaskEngine.open())
    try ledger.record(.conditionObserved(.uncertainClock), actor: .system)
    #expect(try LearningEngine.report(from: ledger).result == .yes)
}

@Test func validReadingsNeverProduceMathFeedbackBeforeCommit() throws {
    for text in ["0", "14", "15", "16", "015", "999"] {
        var ledger = try TaskEngine.open()
        let input = CapturedInput(mode: .handwriting, text: "synthetic-strokes")
        try ledger.record(.inputCaptured(input), actor: .learner)
        try ledger.record(.recognitionProposed(ProposedReading(inputID: input.id, text: text)), actor: .app)
        #expect(try LearningEngine.report(from: ledger).result == .unknown)
        #expect(try TaskEngine.replay(ledger).answer == nil)
    }
}

@Test func invalidReadingRemainsAnIntegrityErrorEvenBeforeCorrectedAnswer() throws {
    var ledger = try TaskEngine.open()
    let input = CapturedInput(mode: .handwriting, text: "synthetic-strokes")
    let reading = ProposedReading(inputID: input.id, text: "abc")
    try ledger.record(.inputCaptured(input), actor: .learner)
    try ledger.record(.recognitionProposed(reading), actor: .app)
    #expect(throws: TaskError.invalidReading) { try LearningEngine.report(from: ledger) }
    try ledger.record(.answerCommitted(CommittedAnswer(value: 15, inputID: input.id,
        origin: .corrected, readingID: reading.id)), actor: .learner)
    #expect(throws: TaskError.invalidReading) { try LearningEngine.report(from: ledger) }
}
