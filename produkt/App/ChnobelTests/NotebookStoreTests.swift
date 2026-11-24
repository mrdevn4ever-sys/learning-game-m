import CoreDomain
import Foundation
import ObservationLog
import SwiftData
import TaskEngine
import Testing
@testable import Chnobel

@MainActor
private func storeURL() throws -> URL {
    let base = try FileManager.default.url(for: .applicationSupportDirectory, in: .userDomainMask, appropriateFor: nil, create: true)
    return base.appendingPathComponent("ChnobelUnitTests/" + UUID().uuidString, isDirectory: true).appendingPathComponent("test.store")
}

@Test @MainActor func swiftDataRoundTripRebuildsTheSameReport() throws {
    let url = try storeURL()
    let store = try NotebookStore(url: url)
    let session = try NotebookSession(store: store)
    session.select("b1")
    session.select("b2")
    session.place(in: .left)
    session.showHelp()
    session.digit(1)
    session.digit(5)
    session.submit()
    let restored = try NotebookSession(store: NotebookStore(url: url))
    #expect(restored.state.positions == session.state.positions)
    #expect(restored.ledger == session.ledger)
    #expect(restored.evidence == session.evidence)
    #expect(restored.evidence.report.tenWithoutHint == .yes)
    #expect(restored.state.answer?.answer.value == 15)
}

@Test @MainActor func pendingDigitsSurviveRestartButAreNotAnAnswer() throws {
    let url = try storeURL()
    let session = try NotebookSession(store: NotebookStore(url: url))
    session.digit(1)
    let restored = try NotebookSession(store: NotebookStore(url: url))
    #expect(restored.draft.text == "1")
    #expect(restored.state.answer == nil)
    #expect(restored.evidence.report.result == .unknown)
}

@Test @MainActor func invalidArchiveIsRejectedRatherThanReplaced() throws {
    let url = try storeURL()
    let store = try NotebookStore(url: url)
    _ = try NotebookSession(store: store)
    let context = ModelContext(store.container)
    let record = try #require(context.fetch(FetchDescriptor<NotebookArchive>()).first)
    let invalid = Data("not-a-notebook".utf8)
    record.payload = invalid
    try context.save()
    #expect(throws: (any Error).self) { try NotebookSession(store: NotebookStore(url: url)) }
    let readback = ModelContext(store.container)
    #expect(try readback.fetch(FetchDescriptor<NotebookArchive>()).first?.payload == invalid)
}

@Test @MainActor func undoIsAlsoPersisted() throws {
    let url = try storeURL()
    let session = try NotebookSession(store: NotebookStore(url: url))
    session.digit(1)
    session.digit(4)
    session.submit()
    session.undo()
    let restored = try NotebookSession(store: NotebookStore(url: url))
    #expect(restored.state.answer == nil)
    #expect(restored.evidence.report.result == .unknown)
    #expect(restored.ledger.events.last?.payload.name == "response.retracted")
}
