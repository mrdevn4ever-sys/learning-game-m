import CoreDomain
import Foundation
import ObservationLog

public enum TaskError: Error, Equatable {
    case invalidOpening, unsupportedRevision, invalidActor, closedAttempt
    case invalidInput, invalidReading, invalidAnswer, invalidMove, invalidUndo, invalidRetraction, invalidSupport
}

public enum DevelopmentTask {
    public static let id = "development.sum-8-7"
    public static let boardID = "development.board-8-7"
    public static let profileID = "synthetic-development"
    public static let expectedResult = 8 + 7
    public static var initialPositions: [String: Zone] {
        var result: [String: Zone] = [:]
        for index in 1...8 { result["a\(index)"] = .left }
        for index in 1...7 { result["b\(index)"] = .right }
        return result
    }
}

public struct EffectiveMove: Sendable, Equatable {
    public let event: Event
    public let move: MaterialMove
    /// Hilfe zum Zeitpunkt dieses wirksamen Zugs, nicht zum Berichtzeitpunkt.
    public let tenSupportBefore: Truth
}

public struct ActiveAnswer: Sendable, Equatable {
    public let eventID: UUID
    public let sequence: Int
    public let answer: CommittedAnswer
}

/// Ein beobachtetes Erreichen durch das Kind, kein globaler Brett-Zeitstempel.
public struct RepresentationAnchor: Sendable, Equatable {
    public let eventID: UUID
    public let sequence: Int
    public let actor: CoreDomain.Actor
    public let positions: [String: Zone]
    public let tenSupportBefore: Truth
    public let observationComplete: Truth
}

public struct AttemptState: Sendable, Equatable {
    public var positions: [String: Zone] = DevelopmentTask.initialPositions
    public var activeMoves: [EffectiveMove] = []
    public var answer: ActiveAnswer?
    /// Aktualität der zuletzt beobachteten Antwort, nicht deren Zahlenwert.
    public var answerCurrency: Truth = .no
    public var isClosed = false
    public var hasGap = false
    public var hasTenSupport = false
    public var hasUnclassifiedDemo = false
    public var supportCount = 0
    public var shownSupport: Support?
    public var lastSequence = -1
    public private(set) var currentTenAnchor: RepresentationAnchor?
    public private(set) var historicalTenAnchors: [RepresentationAnchor] = []
    // Nur App-Handlungen dürfen diesen unveränderten Kind-Nachweis suspendieren.
    private var retainedLearnerTenAnchor: RepresentationAnchor?

    var tenSupportNow: Truth {
        hasTenSupport ? .yes : ((hasGap || hasUnclassifiedDemo) ? .unknown : .no)
    }

    mutating func observeGap() {
        hasGap = true
        answerCurrency = .unknown
        shownSupport = nil
        currentTenAnchor = nil
        retainedLearnerTenAnchor = nil
    }

    mutating func anchorMaterialAction(_ event: Event, supportBefore: Truth) {
        let ownLayout = isTenLayout && !contributingMoves.isEmpty &&
            contributingMoves.allSatisfy { $0.event.actor == .learner }
        if event.actor == .learner {
            // Auch Rückkehr eines Anfangsplättchens und eigenes Undo sind neue Handlungen.
            // Eine eigene Handlung beendet die Suspension durch eine App-Handlung.
            currentTenAnchor = nil
            retainedLearnerTenAnchor = nil
            if ownLayout {
                let supports = contributingMoves.map(\.tenSupportBefore) + [supportBefore]
                let support: Truth = supports.contains(.yes) ? .yes : (supports.contains(.unknown) ? .unknown : .no)
                let anchor = RepresentationAnchor(eventID: event.id, sequence: event.sequence, actor: event.actor,
                    positions: positions, tenSupportBefore: support, observationComplete: hasGap ? .unknown : .yes)
                currentTenAnchor = anchor
                retainedLearnerTenAnchor = anchor
                historicalTenAnchors.append(anchor)
            }
        } else if event.actor == .app {
            // App-Detour/App-Undo ist kein neuer Kind-Zug. Nur den unveränderten
            // Kind-Anker wieder sichtbar machen, nie mit heutiger Hilfe neu datieren.
            if ownLayout, let anchor = retainedLearnerTenAnchor, anchor.positions == positions {
                currentTenAnchor = anchor
            } else {
                currentTenAnchor = nil
            }
        }
    }

    public var canUndo: Bool { !isClosed && ((answerCurrency == .yes && answer != nil) || !activeMoves.isEmpty) }
    public func items(in zone: Zone) -> [String] {
        positions.filter { $0.value == zone }.map(\.key).sorted()
    }
    public var isTenLayout: Bool {
        items(in: .left).count == 10 && items(in: .right).count == 5 && items(in: .spare).isEmpty &&
        (1...8).allSatisfy { positions["a\($0)"] == .left }
    }
    public var isDoublesLayout: Bool {
        items(in: .left).count == 7 && items(in: .right).count == 7 && items(in: .spare).count == 1 &&
        (1...7).allSatisfy { positions["b\($0)"] == .right }
    }

    /// Nur die letzten wirksamen Bewegungen der jetzt umgelegten Plättchen.
    public var contributingMoves: [EffectiveMove] {
        let changed = positions.keys.filter { positions[$0] != DevelopmentTask.initialPositions[$0] }
        let ids = Set(changed.compactMap { item in
            activeMoves.last(where: { $0.move.items.contains(item) })?.event.id
        })
        return activeMoves.filter { ids.contains($0.event.id) }
    }
}

public enum TaskEngine {
    public static func open(streamID: UUID = UUID()) throws -> EventLedger {
        var ledger = try EventLedger(streamID: streamID)
        try ledger.record(.opened(Opening(profileID: DevelopmentTask.profileID, taskID: DevelopmentTask.id,
                                         initialBoardID: DevelopmentTask.boardID, revision: .development)), actor: .system)
        return ledger
    }

    /// Strenger semantischer Replay. Unbekannte Formate werden nicht repariert.
    public static func replay(_ ledger: EventLedger) throws -> AttemptState {
        guard let first = ledger.events.first, first.sequence == 0,
              first.actor == .system, case .opened(let opening) = first.payload,
              opening.profileID == DevelopmentTask.profileID,
              opening.taskID == DevelopmentTask.id, opening.initialBoardID == DevelopmentTask.boardID else {
            throw TaskError.invalidOpening
        }
        guard opening.revision == .development else { throw TaskError.unsupportedRevision }
        var state = AttemptState()
        var inputs: [UUID: CapturedInput] = [:]
        var readings: [UUID: ProposedReading] = [:]
        for event in ledger.events {
            if event.sequence != state.lastSequence + 1 { state.observeGap() }
            state.lastSequence = event.sequence
            if event.id == first.id { continue }
            guard !state.isClosed else { throw TaskError.closedAttempt }
            switch event.payload {
            case .opened:
                throw TaskError.invalidOpening
            case .inputCaptured(let input):
                guard event.actor == .learner else { throw TaskError.invalidActor }
                guard inputs[input.id] == nil else { throw TaskError.invalidInput }
                inputs[input.id] = input
            case .recognitionProposed(let reading):
                guard event.actor == .app else { throw TaskError.invalidActor }
                guard let input = inputs[reading.inputID], input.mode == .handwriting,
                      readings[reading.id] == nil, isDirectNumber(reading.text) else { throw TaskError.invalidReading }
                readings[reading.id] = reading
                // Eine Lesart ist ausdrücklich weder Antwort noch fachlicher Fehler.
            case .answerCommitted(let answer):
                guard event.actor == .learner else { throw TaskError.invalidActor }
                guard let input = inputs[answer.inputID], (0...999).contains(answer.value), state.answerCurrency != .yes else {
                    throw TaskError.invalidAnswer
                }
                switch answer.origin {
                case .direct:
                    guard input.mode == .numberPad, answer.readingID == nil,
                          isDirectNumber(input.text), Int(input.text) == answer.value else { throw TaskError.invalidAnswer }
                case .confirmed, .corrected:
                    guard let readingID = answer.readingID, let reading = readings[readingID],
                          reading.inputID == answer.inputID, let proposedValue = Int(reading.text) else { throw TaskError.invalidAnswer }
                    // Herkunft ist disjunkt nach Zahlenwert, nicht nach Schreibweise.
                    guard (answer.origin == .confirmed) == (proposedValue == answer.value) else { throw TaskError.invalidAnswer }
                }
                state.answer = ActiveAnswer(eventID: event.id, sequence: event.sequence, answer: answer)
                state.answerCurrency = .yes
            case .responseRetracted(let target):
                guard event.actor == .learner else { throw TaskError.invalidActor }
                guard state.answer?.eventID == target else { throw TaskError.invalidRetraction }
                // Rücknahme einer alten Referenz beweist nach Lücke nicht, dass
                // im unbeobachteten Intervall keine andere Antwort abgegeben wurde.
                state.answerCurrency = state.answerCurrency == .yes ? .no : .unknown
                state.answer = nil
            case .materialMoved(let move):
                guard event.actor == .learner || event.actor == .app else { throw TaskError.invalidActor }
                guard (event.actor == .app) == (move.method == .appDemo),
                      move.from != move.to, !move.items.isEmpty, Set(move.items).count == move.items.count,
                      move.items.allSatisfy({ state.positions[$0] == move.from }) else { throw TaskError.invalidMove }
                let before = state.tenSupportNow
                for item in move.items { state.positions[item] = move.to }
                if event.actor == .app {
                    // Nur eine tatsaechliche Zehnerdarstellung ist ein belegter Zehnerhinweis.
                    if state.isTenLayout { state.hasTenSupport = true }
                    else { state.hasUnclassifiedDemo = true }
                }
                state.activeMoves.append(EffectiveMove(event: event, move: move, tenSupportBefore: before))
                state.shownSupport = nil
                state.anchorMaterialAction(event, supportBefore: before)
            case .actionUndone(let target):
                guard let last = state.activeMoves.last, last.event.id == target,
                      last.move.items.allSatisfy({ state.positions[$0] == last.move.to }) else { throw TaskError.invalidUndo }
                guard event.actor == last.event.actor else { throw TaskError.invalidActor }
                let before = state.tenSupportNow
                for item in last.move.items { state.positions[item] = last.move.from }
                state.activeMoves.removeLast()
                state.shownSupport = nil
                state.anchorMaterialAction(event, supportBefore: before)
                // Hilfewissen wird durch Undo nicht geloescht.
            case .supportPresented(let support):
                guard event.actor == .app else { throw TaskError.invalidActor }
                guard support == supportForState(state) else { throw TaskError.invalidSupport }
                state.hasTenSupport = true
                state.supportCount += 1
                state.shownSupport = support
            case .conditionObserved(let condition):
                guard event.actor == .system else { throw TaskError.invalidActor }
                if condition == .gapDetected { state.observeGap() }
            case .closed(let reason):
                guard event.actor == .learner else { throw TaskError.invalidActor }
                if reason == .finished && (state.answer == nil || state.answerCurrency != .yes) { throw TaskError.invalidAnswer }
                state.isClosed = true
            }
        }
        return state
    }

    public static func submit(_ text: String, to original: EventLedger) throws -> EventLedger {
        var ledger = original
        let state = try replay(ledger)
        guard !state.isClosed else { throw TaskError.closedAttempt }
        guard isDirectNumber(text), let value = Int(text) else { throw TaskError.invalidInput }
        if state.answerCurrency == .yes, let previous = state.answer {
            try ledger.record(.responseRetracted(eventID: previous.eventID), actor: .learner)
        }
        let input = CapturedInput(mode: .numberPad, text: text)
        try ledger.record(.inputCaptured(input), actor: .learner)
        try ledger.record(.answerCommitted(CommittedAnswer(value: value, inputID: input.id, origin: .direct)), actor: .learner)
        _ = try replay(ledger)
        return ledger
    }

    public static func move(items: [String], to zone: Zone, in original: EventLedger) throws -> EventLedger {
        let state = try replay(original)
        guard !state.isClosed else { throw TaskError.closedAttempt }
        guard let first = items.first, let from = state.positions[first] else { throw TaskError.invalidMove }
        var ledger = original
        try ledger.record(.materialMoved(MaterialMove(items: items.sorted(), from: from, to: zone, method: .tap)), actor: .learner)
        _ = try replay(ledger)
        return ledger
    }

    public static func presentSupport(in original: EventLedger) throws -> EventLedger {
        let state = try replay(original)
        guard !state.isClosed else { throw TaskError.closedAttempt }
        var ledger = original
        try ledger.record(.supportPresented(supportForState(state)), actor: .app)
        _ = try replay(ledger)
        return ledger
    }

    public static func undo(in original: EventLedger) throws -> EventLedger {
        let state = try replay(original)
        guard state.canUndo else { throw TaskError.invalidUndo }
        var ledger = original
        if state.answerCurrency == .yes, let answer = state.answer,
           answer.sequence > (state.activeMoves.last?.event.sequence ?? -1) {
            try ledger.record(.responseRetracted(eventID: answer.eventID), actor: .learner)
        } else if let move = state.activeMoves.last {
            // Bedienanforderung und fachlicher Akteur der Rücknahme sind getrennt.
            try ledger.record(.actionUndone(eventID: move.event.id), actor: move.event.actor)
        }
        _ = try replay(ledger)
        return ledger
    }

    public static func close(_ original: EventLedger, reason: ClosureReason) throws -> EventLedger {
        var ledger = original
        try ledger.record(.closed(reason), actor: .learner)
        _ = try replay(ledger)
        return ledger
    }

    private static func supportForState(_ state: AttemptState) -> Support {
        if state.hasGap { return .tenUnknownV1 }
        switch (state.items(in: .left).count, state.items(in: .right).count, state.items(in: .spare).count) {
        case (8, 7, 0): return .tenStep
        case (9, 6, 0): return .tenFromNineV1
        case (10, 5, 0): return .tenAlreadyV1
        case (7, 7, 1): return .tenFromDoublesV1
        default: return .tenCompareV1
        }
    }

    private static func isDirectNumber(_ text: String) -> Bool {
        (1...3).contains(text.count) && text.allSatisfy { $0.isASCII && $0.isNumber }
    }
}
