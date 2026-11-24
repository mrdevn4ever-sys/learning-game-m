import EvidenceKit
import TaskEngine
import Testing

@Test func developmentObservationNeverClaimsAcceptance() throws {
    let ledger = try TaskEngine.submit("15", to: TaskEngine.open())
    let evidence = try DevelopmentEvidence(ledger: ledger)
    #expect(evidence.procedure == "none")
    #expect(evidence.population == "synthetisch")
    #expect(evidence.status == "open")
    #expect(evidence.eventCount == ledger.events.count)
    #expect(evidence.boundary.contains("Keine Phase-0-Abnahme"))
}
