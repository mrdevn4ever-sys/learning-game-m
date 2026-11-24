import InputKit
import Testing

@Test func numberPadDoesNotPreselectAnAnswer() {
    let input = DigitBuffer()
    #expect(input.text.isEmpty)
    #expect(input.value == nil)
}

@Test func digitsDeleteAndClearWork() {
    var input = DigitBuffer()
    input.append(1)
    input.append(5)
    #expect(input.value == 15)
    input.deleteLast()
    #expect(input.value == 1)
    input.clear()
    input.deleteLast()
    #expect(input.value == nil)
}

@Test func bufferIsBoundedAndRejectsNonDigits() {
    var input = DigitBuffer()
    for digit in [1, 0, 2, 3, -1, 10] { input.append(digit) }
    #expect(input.text == "102")
    #expect(DigitBuffer(text: "a１５b20").text == "20")
}
