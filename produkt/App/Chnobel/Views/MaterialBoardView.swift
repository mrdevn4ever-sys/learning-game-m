import CoreDomain
import SwiftUI

@MainActor
struct MaterialBoardView: View {
    @Bindable var session: NotebookSession
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        let layout = horizontalSizeClass == .compact ? AnyLayout(VStackLayout(alignment: .leading, spacing: 12)) : AnyLayout(HStackLayout(alignment: .top, spacing: 12))
        layout {
            ForEach(Zone.allCases, id: \.self) { zone in
                zoneView(zone)
            }
        }
    }

    private func zoneName(_ zone: Zone) -> String {
        switch zone { case .left: "A"; case .right: "B"; case .spare: "C" }
    }

    private func zoneView(_ zone: Zone) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Feld \(zoneName(zone)) · \(session.state.items(in: zone).count) Plättchen")
                .font(.headline).accessibilityIdentifier("zone-count-\(zone.rawValue)")
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 48), spacing: 8)], spacing: 8) {
                ForEach(session.state.items(in: zone), id: \.self) { item in
                    Button { session.select(item) } label: {
                        ZStack {
                            if item.hasPrefix("a") { Circle().fill(.indigo) }
                            else { RoundedRectangle(cornerRadius: 10).fill(.orange) }
                            Text(String(item.dropFirst())).font(.headline).foregroundStyle(item.hasPrefix("a") ? .white : .black)
                            if session.selectedItems.contains(item) {
                                Image(systemName: "checkmark.circle.fill").foregroundStyle(.white, .black)
                                    .offset(x: 14, y: -14)
                            }
                        }.frame(width: 44, height: 44).frame(minWidth: 48, minHeight: 48)
                    }
                    .buttonStyle(.plain).disabled(session.state.isClosed)
                    .accessibilityLabel("\(item.hasPrefix("a") ? "Kreis" : "Quadrat") \(item.dropFirst()), Feld \(zoneName(zone))")
                    .accessibilityValue(session.selectedItems.contains(item) ? "ausgewählt" : "nicht ausgewählt")
                    .accessibilityHint("Auswählen, danach im Zielfeld ablegen")
                    .accessibilityIdentifier("token-\(item)")
                }
            }
            if session.state.items(in: zone).isEmpty {
                Text("Freies Feld").foregroundStyle(.secondary).frame(minHeight: 48)
            }
            Button { session.place(in: zone) } label: {
                Label("Hier ablegen", systemImage: "arrow.down.to.line").frame(maxWidth: .infinity, minHeight: 44)
            }.buttonStyle(.bordered).disabled(!session.canPlace(in: zone))
                .accessibilityLabel("In Feld \(zoneName(zone)) ablegen")
                .accessibilityIdentifier("place-\(zone.rawValue)")
        }
        .padding(12).frame(maxWidth: .infinity, alignment: .topLeading)
        .background(Color(uiColor: .secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 18))
    }
}
