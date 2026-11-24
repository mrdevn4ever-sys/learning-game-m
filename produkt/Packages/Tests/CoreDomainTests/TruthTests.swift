import CoreDomain
import Testing

@Test func unknownNeverProvesAbsence() {
    #expect(Truth.unknown.negated == .unknown)
    #expect(ClaimRule(id: "absence", required: [.yes], excluded: [.unknown]).decision == .unknown)
}

@Test func ruleHasThreeOutcomes() {
    #expect(ClaimRule(id: "yes", required: [.yes], excluded: [.no]).decision == .yes)
    #expect(ClaimRule(id: "no", required: [.yes], excluded: [.yes]).decision == .no)
    #expect(ClaimRule(id: "unknown", required: [.unknown], excluded: [.no]).decision == .unknown)
}

@Test func falseDominatesUnknown() {
    #expect(Truth.all([.yes, .unknown, .no]) == .no)
    #expect(Truth.all([.yes, .unknown]) == .unknown)
    #expect(Truth.all([.yes, .yes]) == .yes)
}
