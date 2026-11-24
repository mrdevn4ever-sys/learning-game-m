import InputKit

public enum RecognitionStatus: Equatable, Sendable { case notImplemented }

/// Bewusst keine Lesarten, Platzhalter-Konfidenzen oder Antwortabhaengigkeiten.
/// Eine spaetere lokale Erkennung braucht einen separat geprueften Adapter.
public struct DisabledRecognizer: Sendable {
    public init() {}
    public var status: RecognitionStatus { .notImplemented }
    public func recognize(_ input: StrokeInput, expected: ExpectedSymbols) -> RecognitionStatus {
        .notImplemented
    }
}
