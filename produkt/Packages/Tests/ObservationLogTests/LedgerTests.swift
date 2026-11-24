import CoreDomain
import Foundation
import ObservationLog
import Testing

@Test func duplicateDeliveryIsIdempotent() throws {
    var ledger = try EventLedger(streamID: UUID())
    let event = try ledger.record(.conditionObserved(.gapDetected), actor: .system)
    try ledger.append(event)
    #expect(ledger.events == [event])
}

@Test func sameIDWithChangedPayloadFails() throws {
    var ledger = try EventLedger(streamID: UUID())
    let event = try ledger.record(.conditionObserved(.gapDetected), actor: .system)
    let changed = Event(id: event.id, streamID: event.streamID, sequence: event.sequence,
                        occurredAt: event.occurredAt, actor: event.actor, payload: .conditionObserved(.uncertainClock))
    #expect(throws: LedgerError.conflictingID) { try ledger.append(changed) }
    #expect(ledger.events == [event])
}

@Test func sequenceCollisionAndForeignStreamFail() throws {
    var ledger = try EventLedger(streamID: UUID())
    try ledger.record(.conditionObserved(.gapDetected), actor: .system)
    let collision = Event(streamID: ledger.streamID, sequence: 0, actor: .system, payload: .conditionObserved(.gapDetected))
    #expect(throws: LedgerError.conflictingSequence) { try ledger.append(collision) }
    let foreign = Event(streamID: UUID(), sequence: 1, actor: .system, payload: .conditionObserved(.gapDetected))
    #expect(throws: LedgerError.foreignStream) { try ledger.append(foreign) }
}

@Test func sequenceGapIsNotSilentlyFilled() throws {
    var ledger = try EventLedger(streamID: UUID())
    try ledger.append(Event(streamID: ledger.streamID, sequence: 2, actor: .system, payload: .conditionObserved(.gapDetected)))
    #expect(ledger.hasSequenceGap)
    #expect(ledger.nextSequence == 3)
    let earlier = Event(streamID: ledger.streamID, sequence: 1, actor: .system, payload: .conditionObserved(.gapDetected))
    #expect(throws: LedgerError.outOfOrder) { try ledger.append(earlier) }
}

@Test func invalidSequenceBoundsCannotOverflowReplay() throws {
    var ledger = try EventLedger(streamID: UUID())
    let negative = Event(streamID: ledger.streamID, sequence: -1, actor: .system, payload: .conditionObserved(.gapDetected))
    let overflow = Event(streamID: ledger.streamID, sequence: Int.max, actor: .system, payload: .conditionObserved(.gapDetected))
    #expect(throws: LedgerError.negativeSequence) { try ledger.append(negative) }
    #expect(throws: LedgerError.sequenceOverflow) { try ledger.append(overflow) }
}

@Test func codingRoundTripPreservesIdentityAndOrder() throws {
    var original = try EventLedger(streamID: UUID())
    try original.record(.conditionObserved(.uncertainClock), actor: .system)
    let data = try JSONEncoder().encode(original.events)
    let events = try JSONDecoder().decode([Event].self, from: data)
    let restored = try EventLedger(streamID: original.streamID, events: events)
    #expect(restored == original)
}
