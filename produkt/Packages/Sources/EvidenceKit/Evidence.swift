import CoreDomain
import LearningEngine
import ObservationLog

/// Keine Freigabe, kein Leistungsprofil und kein authentisierter Pruefbeleg.
public struct DevelopmentEvidence: Sendable, Equatable {
    public let report: LearningReport
    public let eventCount: Int
    public let streamDescription: String
    public let procedure = "none"
    public let population = "synthetisch"
    public let status = "open"
    public let boundary = "Entwicklungsansicht eines synthetischen Versuchs. Keine Aussage über Kinderleistung, Lernwirksamkeit oder Erkennungsgenauigkeit. Keine Phase-0-Abnahme."

    public init(ledger: EventLedger) throws {
        report = try LearningEngine.report(from: ledger)
        eventCount = ledger.events.count
        streamDescription = ledger.streamID.uuidString
    }
}
