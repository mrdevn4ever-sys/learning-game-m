import CoreDomain
import ObservationLog
import TaskEngine

public struct LearningReport: Sendable, Equatable {
    public let result: Truth
    public let answerCurrency: Truth
    public let tenRepresentation: Truth
    public let tenWithoutHint: Truth
    public let tenWithHint: Truth
    public let historicalTenWithoutHint: Truth
    public let doublesRepresentation: Truth
    public let ruleVersion: String

    public var resultText: String {
        switch result {
        case .yes: "Dein abgegebenes Ergebnis stimmt."
        case .no: "Die abgegebene Zahl passt noch nicht zu 8 + 7. Die Ursache bleibt offen."
        case .unknown: answerCurrency == .unknown
            ? "Ob die letzte Antwort noch gilt, bleibt wegen einer Beobachtungslücke offen."
            : "Noch kein Ergebnis abgegeben."
        }
    }

    public var pathText: String {
        if tenWithoutHint == .yes {
            return "Du hast 10 und 5 gelegt, ohne vorherigen Hinweis der App auf diesen Schritt."
        }
        if tenWithHint == .yes { return "Du hast 10 und 5 nach einem Hinweis auf den Zehnerschritt gelegt." }
        if tenRepresentation == .yes { return "Du hast 10 und 5 gelegt. Ob vorher ein Hinweis kam, bleibt offen." }
        if doublesRepresentation == .yes { return "Du hast den anderen passenden Weg mit 7, 7 und 1 gelegt." }
        return "Zum dargestellten Weg ist noch keine Aussage belegt."
    }

    public var historicalPathText: String {
        if historicalTenWithoutHint == .yes {
            return "Früher in dieser Runde hast du 10 und 5 ohne vorherigen Hinweis auf diesen Schritt gelegt. Das beschreibt die damalige Handlung, nicht jeden späteren Zustand."
        }
        return "Ein früherer Zehnerschritt ohne Hinweis ist nicht belegt."
    }
}

public enum LearningEngine {
    public static func report(from ledger: EventLedger) throws -> LearningReport {
        let state = try TaskEngine.replay(ledger)
        let result: Truth = state.answerCurrency == .yes
            ? (state.answer.map { $0.answer.value == DevelopmentTask.expectedResult ? .yes : .no } ?? .unknown)
            : .unknown
        let moves = state.contributingMoves
        let ownAction: Truth = moves.isEmpty ? .no : (moves.allSatisfy { $0.event.actor == .learner } ? .yes : .no)
        let complete: Truth = state.hasGap ? .unknown : .yes
        let ten: Truth = ClaimRule(id: "local.ten.represented", required: [state.isTenLayout ? .yes : .no, ownAction, complete]).decision
        let doubles: Truth = ClaimRule(id: "local.doubles.represented", required: [state.isDoublesLayout ? .yes : .no, ownAction, complete]).decision
        let support = state.currentTenAnchor?.tenSupportBefore ?? .unknown
        let historicalDecisions = state.historicalTenAnchors.map { anchor in
            ClaimRule(id: "local.ten.historical-without-hint", required: [anchor.observationComplete],
                      excluded: [anchor.tenSupportBefore]).decision
        }
        let historical: Truth = historicalDecisions.contains(.yes) ? .yes :
            ((historicalDecisions.contains(.unknown) || state.hasGap) ? .unknown : .no)
        return LearningReport(
            result: result,
            answerCurrency: state.answerCurrency,
            tenRepresentation: ten,
            tenWithoutHint: ClaimRule(id: "local.ten.without-hint", required: [ten], excluded: [support]).decision,
            tenWithHint: ClaimRule(id: "local.ten.with-hint", required: [ten, support]).decision,
            historicalTenWithoutHint: historical,
            doublesRepresentation: doubles,
            ruleVersion: Revision.development.rules
        )
    }
}
