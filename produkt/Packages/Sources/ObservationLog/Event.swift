import CoreDomain
import Foundation

public struct Opening: Codable, Equatable, Sendable {
    public let profileID: String
    public let taskID: String
    public let initialBoardID: String
    public let revision: Revision
    public init(profileID: String, taskID: String, initialBoardID: String, revision: Revision) {
        self.profileID = profileID
        self.taskID = taskID
        self.initialBoardID = initialBoardID
        self.revision = revision
    }
}

public struct CapturedInput: Codable, Equatable, Sendable {
    public let id: UUID
    public let mode: InputMode
    public let text: String
    public init(id: UUID = UUID(), mode: InputMode, text: String) {
        self.id = id
        self.mode = mode
        self.text = text
    }
}

/// Nur Replay-Schnittstelle. Die Entwicklungs-App erzeugt keine Lesarten.
public struct ProposedReading: Codable, Equatable, Sendable {
    public let id: UUID
    public let inputID: UUID
    public let text: String
    public init(id: UUID = UUID(), inputID: UUID, text: String) {
        self.id = id
        self.inputID = inputID
        self.text = text
    }
}

public struct CommittedAnswer: Codable, Equatable, Sendable {
    public let value: Int
    public let inputID: UUID
    public let origin: AnswerOrigin
    public let readingID: UUID?
    public init(value: Int, inputID: UUID, origin: AnswerOrigin, readingID: UUID? = nil) {
        self.value = value
        self.inputID = inputID
        self.origin = origin
        self.readingID = readingID
    }
}

public struct MaterialMove: Codable, Equatable, Sendable {
    public let items: [String]
    public let from: Zone
    public let to: Zone
    public let method: MoveMethod
    public init(items: [String], from: Zone, to: Zone, method: MoveMethod) {
        self.items = items
        self.from = from
        self.to = to
        self.method = method
    }
}

public enum Support: String, Codable, Sendable {
    /// Unveränderliche Textfassungen. Replay prüft die Auswahl am Materialzustand.
    case tenStep
    case tenFromNineV1, tenAlreadyV1, tenFromDoublesV1, tenCompareV1, tenUnknownV1
    public var text: String {
        switch self {
        case .tenStep:
            "Du kannst zuerst die Acht zur Zehn ergänzen. Lege dafür zwei Plättchen von B nach A."
        case .tenFromNineV1:
            "In A liegen neun Plättchen. Lege noch ein Plättchen von B nach A. Dann liegen dort zehn."
        case .tenAlreadyV1:
            "In A liegen schon zehn Plättchen und in B fünf. Für diesen Zehnerschritt brauchst du kein weiteres Plättchen zu verschieben."
        case .tenFromDoublesV1:
            "7, 7 und 1 ist ein anderer passender Weg. Wenn du stattdessen den Zehnerweg legen möchtest: Lege zuerst das Plättchen aus C nach A und danach zwei Plättchen von B nach A."
        case .tenCompareV1:
            "Für einen Zehnerweg kannst du eine Gruppe mit zehn Plättchen legen. Vergleiche die Anzahl in den Feldern. Deine Plättchen bleiben unverändert liegen."
        case .tenUnknownV1:
            "Die aktuelle Materialspur ist unvollständig. Für einen Zehnerweg brauchst du eine Gruppe mit zehn Plättchen. Ich gebe deshalb keinen bestimmten Zug vor."
        }
    }
    public var version: String { self == .tenStep ? "local-support-0" : "local-support-1" }
    public var target: String { "ten.step" }
    public var channel: String { "visualWithAccessibilityText" }
    public var kind: String { "partialStep" }
}

/// App-lokales Codable-Format, kein gemeinsamer v1-Ereignisvertrag.
public enum EventPayload: Codable, Equatable, Sendable {
    case opened(Opening)
    case inputCaptured(CapturedInput)
    case recognitionProposed(ProposedReading)
    case answerCommitted(CommittedAnswer)
    case responseRetracted(eventID: UUID)
    case materialMoved(MaterialMove)
    case actionUndone(eventID: UUID)
    case supportPresented(Support)
    case conditionObserved(ObservationCondition)
    case closed(ClosureReason)

    public var name: String {
        switch self {
        case .opened: "attempt.opened"
        case .inputCaptured: "input.captured"
        case .recognitionProposed: "recognition.proposed"
        case .answerCommitted: "answer.committed"
        case .responseRetracted: "response.retracted"
        case .materialMoved: "material.moved"
        case .actionUndone: "action.undone"
        case .supportPresented: "support.presented"
        case .conditionObserved: "condition.observed"
        case .closed: "attempt.closed"
        }
    }
}

public struct Event: Codable, Equatable, Sendable, Identifiable {
    public let id: UUID
    public let streamID: UUID
    public let sequence: Int
    public let occurredAt: Date
    public let actor: CoreDomain.Actor
    public let payload: EventPayload

    public init(id: UUID = UUID(), streamID: UUID, sequence: Int, occurredAt: Date = Date(), actor: CoreDomain.Actor, payload: EventPayload) {
        self.id = id
        self.streamID = streamID
        self.sequence = sequence
        self.occurredAt = occurredAt
        self.actor = actor
        self.payload = payload
    }
}
