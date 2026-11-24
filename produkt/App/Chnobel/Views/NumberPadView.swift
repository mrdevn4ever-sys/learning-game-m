import SwiftUI

@MainActor
struct NumberPadView: View {
    @Bindable var session: NotebookSession
    @Environment(\.dynamicTypeSize) private var typeSize
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        let layout = horizontalSizeClass == .compact || typeSize.isAccessibilitySize
            ? AnyLayout(VStackLayout(spacing: 8))
            : AnyLayout(HStackLayout(alignment: .bottom, spacing: 12))
        VStack(spacing: 8) {
            HStack {
                Text("Ziffernblock").font(.headline).accessibilityIdentifier("number-pad-title")
                Spacer()
                Text(session.draft.text.isEmpty ? "Antwort: —" : "Antwort: \(session.draft.text)")
                    .font(.title3.monospacedDigit()).accessibilityIdentifier("answer-draft")
            }
            layout {
                LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 8), count: 3), spacing: 8) {
                    ForEach(1...9, id: \.self) { digit in digitButton(digit) }
                    Button(action: session.deleteDigit) {
                        Image(systemName: "delete.left").frame(maxWidth: .infinity, minHeight: 48)
                    }.accessibilityLabel("Letzte Ziffer löschen").accessibilityIdentifier("digit-delete")
                    digitButton(0)
                    Button("Leeren", action: session.clearDigits)
                        .frame(maxWidth: .infinity, minHeight: 48).accessibilityIdentifier("digit-clear")
                }.buttonStyle(.bordered)
                Button(action: session.submit) {
                    Label("Abgeben", systemImage: "checkmark")
                        .labelStyle(.titleAndIcon).frame(minWidth: 90, minHeight: 48)
                }
                .buttonStyle(.borderedProminent).controlSize(.large)
                .disabled(session.draft.value == nil || session.state.isClosed)
                .accessibilityIdentifier("submit-answer")
            }
        }
        .disabled(session.state.isClosed)
        .padding(.horizontal, 20).padding(.vertical, 12)
        .frame(maxWidth: typeSize.isAccessibilitySize ? .infinity : 760)
        .frame(maxWidth: .infinity)
        .background(.regularMaterial)
    }

    private func digitButton(_ digit: Int) -> some View {
        Button { session.digit(digit) } label: {
            Text(String(digit)).font(.title2.monospacedDigit()).frame(maxWidth: .infinity, minHeight: 48)
        }
        .keyboardShortcut(KeyEquivalent(Character(String(digit))), modifiers: [])
        .accessibilityLabel("Ziffer \(digit)")
        .accessibilityIdentifier("digit-\(digit)")
    }
}
