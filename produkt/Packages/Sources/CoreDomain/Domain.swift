import Foundation

/// Kleene-Logik: Fehlende Beobachtung ist nie ein Beleg fuer Abwesenheit.
public enum Truth: String, Codable, Sendable, Equatable {
    case yes, no, unknown

    public var negated: Truth {
        switch self {
        case .yes: .no
        case .no: .yes
        case .unknown: .unknown
        }
    }

    public static func all(_ facts: [Truth]) -> Truth {
        if facts.contains(.no) { return .no }
        if facts.contains(.unknown) { return .unknown }
        return .yes
    }
}

public struct ClaimRule: Sendable {
    public let id: String
    public let required: [Truth]
    public let excluded: [Truth]

    public init(id: String, required: [Truth], excluded: [Truth] = []) {
        self.id = id
        self.required = required
        self.excluded = excluded
    }

    public var decision: Truth { .all(required + excluded.map(\.negated)) }
}

public enum Actor: String, Codable, Sendable { case learner, app, system }
public enum InputMode: String, Codable, Sendable { case numberPad, handwriting }
public enum AnswerOrigin: String, Codable, Sendable { case direct, confirmed, corrected }
public enum Zone: String, CaseIterable, Codable, Sendable { case left, right, spare }
public enum MoveMethod: String, Codable, Sendable { case tap, appDemo }
public enum ClosureReason: String, Codable, Sendable { case finished, abandoned }
public enum ObservationCondition: String, Codable, Sendable { case gapDetected, uncertainClock }

public struct Revision: Codable, Equatable, Sendable {
    public let content: String
    public let rules: String
    public let evaluation: String
    public init(content: String, rules: String, evaluation: String) {
        self.content = content
        self.rules = rules
        self.evaluation = evaluation
    }
    // Neue Kandidatenrevision; alte Ereignisse werden nicht still neu interpretiert.
    public static let development = Revision(content: "local-draft-1", rules: "local-draft-1", evaluation: "local-draft-1")
}
