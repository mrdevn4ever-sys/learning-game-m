import CoreDomain
import Foundation

public enum LedgerError: Error, Equatable {
    case foreignStream, conflictingID, conflictingSequence, outOfOrder, negativeSequence, sequenceOverflow
}

public struct EventLedger: Sendable, Equatable {
    public let streamID: UUID
    public private(set) var events: [Event]

    public init(streamID: UUID, events: [Event] = []) throws {
        self.streamID = streamID
        self.events = []
        for event in events { try append(event) }
    }

    public var nextSequence: Int { (events.last?.sequence ?? -1) + 1 }
    public var hasSequenceGap: Bool {
        events.enumerated().contains { $0.offset != $0.element.sequence }
    }

    /// Identische Zustellung wirkt einmal, jede Kollision scheitert geschlossen.
    public mutating func append(_ event: Event) throws {
        guard event.streamID == streamID else { throw LedgerError.foreignStream }
        guard event.sequence >= 0 else { throw LedgerError.negativeSequence }
        guard event.sequence < Int.max else { throw LedgerError.sequenceOverflow }
        if let previous = events.first(where: { $0.id == event.id }) {
            guard previous == event else { throw LedgerError.conflictingID }
            return
        }
        guard !events.contains(where: { $0.sequence == event.sequence }) else {
            throw LedgerError.conflictingSequence
        }
        if let last = events.last, event.sequence <= last.sequence { throw LedgerError.outOfOrder }
        events.append(event)
    }

    @discardableResult
    public mutating func record(_ payload: EventPayload, actor: CoreDomain.Actor, at date: Date = Date()) throws -> Event {
        let event = Event(streamID: streamID, sequence: nextSequence, occurredAt: date, actor: actor, payload: payload)
        try append(event)
        return event
    }
}
