import InputKit
import RecognitionKit
import Testing

@Test func recognitionIsExplicitlyNotImplemented() {
    let recognizer = DisabledRecognizer()
    #expect(recognizer.status == .notImplemented)
    #expect(recognizer.recognize(StrokeInput(strokes: []), expected: .digits) == .notImplemented)
    #expect(recognizer.recognize(StrokeInput(strokes: [[StrokePoint(x: 0, y: 1, elapsed: 0)]]), expected: .digitsAndOperators) == .notImplemented)
}
