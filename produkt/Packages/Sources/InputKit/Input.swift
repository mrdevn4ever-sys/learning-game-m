public struct DigitBuffer: Equatable, Sendable {
    public private(set) var text: String
    public static let maximumDigits = 3

    public init(text: String = "") {
        self.text = String(text.filter { $0.isASCII && $0.isNumber }.prefix(Self.maximumDigits))
    }

    public var value: Int? { Int(text) }
    public mutating func append(_ digit: Int) {
        guard (0...9).contains(digit), text.count < Self.maximumDigits else { return }
        text.append(String(digit))
    }
    public mutating func deleteLast() { if !text.isEmpty { text.removeLast() } }
    public mutating func clear() { text = "" }
}

/// Nur Zeichenform und Striche; weder Aufgabe noch Antwortschluessel.
public enum ExpectedSymbols: Sendable { case digits, digitsAndOperators }
public struct StrokePoint: Sendable, Equatable {
    public let x: Double
    public let y: Double
    public let elapsed: Double
    public init(x: Double, y: Double, elapsed: Double) {
        self.x = x
        self.y = y
        self.elapsed = elapsed
    }
}
public struct StrokeInput: Sendable, Equatable {
    public let strokes: [[StrokePoint]]
    public init(strokes: [[StrokePoint]]) { self.strokes = strokes }
}
