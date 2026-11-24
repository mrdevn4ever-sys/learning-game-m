import CoreDomain
import EvidenceKit
import InputKit
import Observation
import ObservationLog
import TaskEngine

@Observable
@MainActor
final class NotebookSession {
    private let store: NotebookStore
    private(set) var ledger: EventLedger
    private(set) var state: AttemptState
    private(set) var evidence: DevelopmentEvidence
    private(set) var draft: DigitBuffer
    var selectedItems: Set<String> = []
    var errorText: String?

    init(store: NotebookStore) throws {
        let restoredLedger: EventLedger
        let restoredDraft: DigitBuffer
        if let snapshot = try store.load() {
            restoredLedger = try snapshot.validatedLedger()
            restoredDraft = DigitBuffer(text: snapshot.draft)
        } else {
            restoredLedger = try TaskEngine.open()
            restoredDraft = DigitBuffer()
            try store.save(ledger: restoredLedger, draft: restoredDraft.text)
        }
        self.store = store
        ledger = restoredLedger
        draft = restoredDraft
        state = try TaskEngine.replay(restoredLedger)
        evidence = try DevelopmentEvidence(ledger: restoredLedger)
    }

    func digit(_ value: Int) {
        guard !state.isClosed else { return }
        var next = draft
        next.append(value)
        saveDraft(next)
    }

    func deleteDigit() {
        var next = draft
        next.deleteLast()
        saveDraft(next)
    }

    func clearDigits() { saveDraft(DigitBuffer()) }

    private func saveDraft(_ next: DigitBuffer) {
        guard !state.isClosed else { return }
        do {
            try store.save(ledger: ledger, draft: next.text)
            draft = next
        } catch { errorText = "Die Eingabe wurde nicht gespeichert. Bitte erneut versuchen." }
    }

    func select(_ item: String) {
        guard !state.isClosed else { return }
        if selectedItems.contains(item) { selectedItems.remove(item); return }
        if let first = selectedItems.first, state.positions[first] != state.positions[item] {
            selectedItems.removeAll()
        }
        selectedItems.insert(item)
    }

    func canPlace(in zone: Zone) -> Bool {
        !state.isClosed && !selectedItems.isEmpty && selectedItems.allSatisfy { state.positions[$0] != zone }
    }

    func place(in zone: Zone) {
        let items = Array(selectedItems)
        apply { try TaskEngine.move(items: items, to: zone, in: $0) }
    }

    func submit() {
        let text = draft.text
        apply(clearDraft: true) { try TaskEngine.submit(text, to: $0) }
    }

    func showHelp() { apply { try TaskEngine.presentSupport(in: $0) } }
    func undo() { apply { try TaskEngine.undo(in: $0) } }
    func finish() { apply { try TaskEngine.close($0, reason: .finished) } }
    func startNewAttempt() { apply(clearDraft: true) { _ in try TaskEngine.open() } }

    private func apply(clearDraft: Bool = false, _ change: (EventLedger) throws -> EventLedger) {
        do {
            let next = try change(ledger)
            let nextState = try TaskEngine.replay(next)
            let nextEvidence = try DevelopmentEvidence(ledger: next)
            let nextDraft = clearDraft ? DigitBuffer() : draft
            // Ereignisse, Eingabeentwurf und Reihenfolge atomar speichern, dann UI freigeben.
            try store.save(ledger: next, draft: nextDraft.text)
            ledger = next
            state = nextState
            evidence = nextEvidence
            draft = nextDraft
            selectedItems.removeAll()
        } catch {
            errorText = "Die Handlung wurde nicht gespeichert und nicht übernommen. Bitte erneut versuchen."
        }
    }
}
