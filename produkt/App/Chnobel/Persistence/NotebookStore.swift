import Foundation
import ObservationLog
import SwiftData
import TaskEngine

@Model
final class NotebookArchive {
    @Attribute(.unique) var key: String
    var payload: Data
    init(key: String, payload: Data) {
        self.key = key
        self.payload = payload
    }
}

struct LocalNotebookSnapshot: Codable {
    // Lokales Speicherformat, ausdrücklich kein gemeinsamer Vertragsstand v1.
    let localFormat: Int
    let streamID: UUID
    let events: [Event]
    let draft: String

    init(ledger: EventLedger, draft: String) {
        self.localFormat = 1
        self.streamID = ledger.streamID
        self.events = ledger.events
        self.draft = draft
    }

    func validatedLedger() throws -> EventLedger {
        guard localFormat == 1 else { throw NotebookStoreError.unsupportedFormat }
        guard draft.count <= 3, draft.allSatisfy({ $0.isASCII && $0.isNumber }) else {
            throw NotebookStoreError.invalidDraft
        }
        let ledger = try EventLedger(streamID: streamID, events: events)
        _ = try TaskEngine.replay(ledger)
        return ledger
    }
}

enum NotebookStoreError: Error, Equatable {
    case unsupportedFormat, invalidDraft, ambiguousArchive
}

/// Nur lokale SwiftData-Datei. Kein CloudKit, kein Konto, kein Netzwerk.
@MainActor
final class NotebookStore {
    let container: ModelContainer
    private let context: ModelContext
    // Native Fehlerprobe innerhalb der Transaktion, standardmässig ohne Eingriff.
    private let beforeSave: (@MainActor () throws -> Void)?
    private static let key = "synthetic-development-notebook"

    init(url: URL, beforeSave: (@MainActor () throws -> Void)? = nil) throws {
        self.beforeSave = beforeSave
        var directory = url.deletingLastPathComponent()
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        var values = URLResourceValues()
        values.isExcludedFromBackup = true
        try directory.setResourceValues(values)
        let schema = Schema([NotebookArchive.self])
        let configuration = ModelConfiguration("ChnobelLocal", schema: schema, url: url, cloudKitDatabase: .none)
        container = try ModelContainer(for: schema, configurations: [configuration])
        context = ModelContext(container)
        context.autosaveEnabled = false
    }

    static func applicationURL(arguments: [String] = ProcessInfo.processInfo.arguments) throws -> URL {
        let base = try FileManager.default.url(for: .applicationSupportDirectory, in: .userDomainMask,
                                                appropriateFor: nil, create: true)
        var namespace = "development"
        #if DEBUG
        // Isolierter synthetischer UI-Teststore; kein Loeschen und kein fremder Dateipfad.
        if let index = arguments.firstIndex(of: "--uitest-store"), arguments.indices.contains(index + 1),
           let id = UUID(uuidString: arguments[index + 1]) {
            namespace = "ui-test-" + id.uuidString
        }
        #endif
        return base.appendingPathComponent("Chnobel", isDirectory: true)
            .appendingPathComponent(namespace, isDirectory: true).appendingPathComponent("notebook.store")
    }

    func load() throws -> LocalNotebookSnapshot? {
        let records = try context.fetch(FetchDescriptor<NotebookArchive>())
        guard records.count <= 1, records.allSatisfy({ $0.key == Self.key }) else {
            throw NotebookStoreError.ambiguousArchive
        }
        guard let record = records.first else { return nil }
        let snapshot = try JSONDecoder().decode(LocalNotebookSnapshot.self, from: record.payload)
        _ = try snapshot.validatedLedger()
        return snapshot
    }

    func save(ledger: EventLedger, draft: String) throws {
        let snapshot = LocalNotebookSnapshot(ledger: ledger, draft: draft)
        _ = try snapshot.validatedLedger()
        let data = try JSONEncoder().encode(snapshot)
        do {
            let records = try context.fetch(FetchDescriptor<NotebookArchive>())
            guard records.count <= 1, records.allSatisfy({ $0.key == Self.key }) else {
                throw NotebookStoreError.ambiguousArchive
            }
            if let record = records.first { record.payload = data }
            else { context.insert(NotebookArchive(key: Self.key, payload: data)) }
            try beforeSave?()
            try context.save()
        } catch {
            context.rollback()
            throw error
        }
    }
}
