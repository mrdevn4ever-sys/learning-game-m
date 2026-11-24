import SwiftUI

@main
struct ChnobelApp: App {
    var body: some Scene {
        WindowGroup { NotebookRootView() }
    }
}

@MainActor
private struct NotebookRootView: View {
    @State private var session: NotebookSession?
    @State private var failed = false

    var body: some View {
        Group {
            if let session { NotebookView(session: session) }
            else if failed {
                ContentUnavailableView {
                    Label("Heft nicht geladen", systemImage: "exclamationmark.triangle")
                } description: {
                    Text("Die gespeicherte Seite bleibt unverändert. Ein unbekanntes oder beschädigtes Format wird nicht still ersetzt.")
                } actions: {
                    Button("Erneut laden", action: load).buttonStyle(.borderedProminent)
                }
            } else { ProgressView("Heft öffnen …") }
        }
        .task { if session == nil && !failed { load() } }
    }

    private func load() {
        do {
            let store = try NotebookStore(url: NotebookStore.applicationURL())
            session = try NotebookSession(store: store)
            failed = false
        } catch { failed = true }
    }
}
