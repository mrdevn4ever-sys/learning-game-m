import CoreDomain
import RecognitionKit
import SwiftUI

@MainActor
struct NotebookView: View {
    @Bindable var session: NotebookSession
    @State private var showingReport = false
    @State private var confirmingReset = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    Text("Synthetisches Profil · Entwicklungsheft")
                        .font(.subheadline).foregroundStyle(.secondary)
                        .accessibilityIdentifier("synthetic-profile")
                    HStack(alignment: .firstTextBaseline) {
                        Text("8 + 7").font(.system(.largeTitle, design: .rounded, weight: .bold))
                            .accessibilityLabel("Acht plus sieben").accessibilityIdentifier("task-title")
                        Spacer()
                        Button(action: session.showHelp) { Label("Hilfe", systemImage: "questionmark.circle") }
                            .buttonStyle(.bordered).controlSize(.large)
                            .disabled(session.state.isClosed || session.state.shownSupport != nil)
                            .accessibilityIdentifier("show-help")
                    }
                    Text("Wähle Plättchen aus. Tippe danach auf «Hier ablegen». Du kannst deinen eigenen Weg legen oder direkt eine Zahl eingeben.")
                    if let support = session.state.shownSupport {
                        Label(support.text, systemImage: "lightbulb")
                            .padding().frame(maxWidth: .infinity, alignment: .leading)
                            .background(.yellow.opacity(0.15), in: RoundedRectangle(cornerRadius: 16))
                            .accessibilityIdentifier("help-text")
                    }
                    MaterialBoardView(session: session)
                    HStack {
                        Button(action: session.undo) { Label("Rückgängig", systemImage: "arrow.uturn.backward") }
                            .disabled(!session.state.canUndo).accessibilityIdentifier("undo")
                        Spacer()
                        Button("Runde beenden", action: session.finish)
                            .disabled(session.state.isClosed || session.state.answer == nil)
                            .accessibilityIdentifier("finish-attempt")
                    }.buttonStyle(.bordered).controlSize(.large)
                    VStack(alignment: .leading, spacing: 8) {
                        Text(session.evidence.report.resultText).font(.headline).accessibilityIdentifier("result-summary")
                        Text(session.evidence.report.pathText).accessibilityIdentifier("path-summary")
                        if session.state.isClosed {
                            Text("Diese Runde ist beendet. Deine Seite bleibt gespeichert.")
                                .accessibilityIdentifier("round-finished")
                        }
                    }.padding().frame(maxWidth: .infinity, alignment: .leading)
                        .background(.quaternary.opacity(0.5), in: RoundedRectangle(cornerRadius: 16))
                    if DisabledRecognizer().status == .notImplemented {
                        Label("Handschrifterkennung ist nicht implementiert und bleibt ausgeschaltet. Nutze den Ziffernblock.", systemImage: "pencil.slash")
                            .font(.footnote).foregroundStyle(.secondary).accessibilityIdentifier("recognition-disabled")
                    }
                }.padding(24).frame(maxWidth: 1000)
                    .frame(maxWidth: .infinity)
            }
            .background(Color(uiColor: .systemGroupedBackground))
            .safeAreaInset(edge: .bottom, spacing: 0) { NumberPadView(session: session) }
            .navigationTitle("Chnobel")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Neues Heft", systemImage: "plus") { confirmingReset = true }
                        .accessibilityIdentifier("new-notebook")
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Bericht", systemImage: "list.bullet.rectangle") { showingReport = true }
                        .accessibilityIdentifier("show-report")
                }
            }
            .sheet(isPresented: $showingReport) { ReportView(session: session) }
            .confirmationDialog("Aktuelle synthetische Seite ersetzen?", isPresented: $confirmingReset, titleVisibility: .visible) {
                Button("Neue synthetische Seite", role: .destructive, action: session.startNewAttempt)
            } message: { Text("Material, Eingaben und Protokoll dieser Seite werden lokal ersetzt.") }
            .alert("Nicht gespeichert", isPresented: Binding(get: { session.errorText != nil }, set: { if !$0 { session.errorText = nil } })) {
                Button("Verstanden") { session.errorText = nil }
            } message: { Text(session.errorText ?? "") }
        }
        .tint(.indigo)
    }
}
