import ObservationLog
import SwiftUI

@MainActor
struct ReportView: View {
    @Bindable var session: NotebookSession
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            List {
                Section("Nur dieser synthetische Versuch") {
                    Text(session.evidence.report.resultText).accessibilityIdentifier("report-result")
                    Text(session.evidence.report.pathText).accessibilityIdentifier("report-path")
                    if let answer = session.state.answer {
                        Text("Abgegebene Zahl: \(answer.answer.value)").accessibilityIdentifier("report-answer")
                    }
                    Text("Gezeigte Hilfen: \(session.state.supportCount)").accessibilityIdentifier("report-help-count")
                }
                Section("Aussagegrenze") {
                    Text(session.evidence.boundary)
                    Text("Prüfverfahren: none · Geltungsbereich: synthetisch · Status: open")
                    Text("Rollen und Profil sind synthetisch. Dies ist kein gesicherter Erwachsenenbereich.")
                    Text("Lokale Regelversion: \(session.evidence.report.ruleVersion)")
                }
                Section("Lokales Beobachtungsprotokoll") {
                    Text("Ereignisse: \(session.evidence.eventCount)").accessibilityIdentifier("report-event-count")
                    ForEach(session.ledger.events) { event in
                        VStack(alignment: .leading, spacing: 4) {
                            Text("\(event.sequence) · \(event.payload.name)").font(.body.monospaced())
                            Text("Akteur: \(event.actor.rawValue)").font(.caption).foregroundStyle(.secondary)
                            if case .supportPresented(let support) = event.payload {
                                Text(support.text)
                                Text("\(support.target) · \(support.kind) · \(support.channel)").font(.caption)
                            }
                        }
                    }
                }
            }
            .navigationTitle("Entwicklungsbericht")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Zum Ziffernblock") { dismiss() }.accessibilityIdentifier("return-to-number-pad")
                }
            }
        }
    }
}
