import UIKit
import XCTest

final class NotebookUITests: XCTestCase {
    @MainActor
    private func launchNotebook() -> XCUIApplication {
        continueAfterFailure = false
        let app = XCUIApplication()
        app.launchArguments = ["--uitest-store", UUID().uuidString]
        app.launch()
        XCTAssertTrue(app.buttons["digit-1"].waitForExistence(timeout: 15))
        return app
    }

    @MainActor
    private func reveal(_ element: XCUIElement, in app: XCUIApplication) {
        for _ in 0..<6 {
            if element.isHittable { return }
            app.scrollViews.firstMatch.swipeUp()
        }
        XCTAssertTrue(element.isHittable)
    }

    @MainActor
    func testDirectNumberPadSubmission() {
        let app = launchNotebook()
        XCTAssertEqual(app.staticTexts["answer-draft"].label, "Antwort: —")
        app.buttons["digit-1"].tap()
        app.buttons["digit-5"].tap()
        XCTAssertEqual(app.staticTexts["answer-draft"].label, "Antwort: 15")
        app.buttons["submit-answer"].tap()
        app.buttons["show-report"].tap()
        XCTAssertTrue(app.staticTexts["report-answer"].waitForExistence(timeout: 5))
        XCTAssertEqual(app.staticTexts["report-answer"].label, "Abgegebene Zahl: 15")
        XCTAssertEqual(app.staticTexts["report-result"].label, "Dein abgegebenes Ergebnis stimmt.")
        XCTAssertEqual(app.staticTexts["report-path"].label, "Zum dargestellten Weg ist noch keine Aussage belegt.")
    }

    @MainActor
    func testHelpShowsTheLoggedHintWithoutMovingMaterial() {
        let app = launchNotebook()
        app.buttons["show-help"].tap()
        XCTAssertTrue(app.staticTexts["help-text"].exists)
        XCTAssertTrue(app.staticTexts["help-text"].label.contains("zwei Plättchen von B nach A"))
        XCTAssertTrue(app.staticTexts["zone-count-left"].label.contains("8 Plättchen"))
        XCTAssertTrue(app.staticTexts["zone-count-right"].label.contains("7 Plättchen"))
        app.buttons["show-report"].tap()
        XCTAssertTrue(app.staticTexts["report-help-count"].waitForExistence(timeout: 5))
        XCTAssertEqual(app.staticTexts["report-help-count"].label, "Gezeigte Hilfen: 1")
        XCTAssertEqual(app.staticTexts["report-result"].label, "Noch kein Ergebnis abgegeben.")
    }

    @MainActor
    func testRestartRestoresDraftThenAnswerMaterialAndReport() {
        let app = launchNotebook()
        app.buttons["digit-1"].tap()
        app.terminate()
        app.launch()
        XCTAssertTrue(app.buttons["digit-5"].waitForExistence(timeout: 15))
        XCTAssertEqual(app.staticTexts["answer-draft"].label, "Antwort: 1")
        app.buttons["digit-5"].tap()
        app.buttons["submit-answer"].tap()
        reveal(app.buttons["token-b1"], in: app)
        app.buttons["token-b1"].tap()
        app.buttons["token-b2"].tap()
        reveal(app.buttons["place-left"], in: app)
        app.buttons["place-left"].tap()
        app.terminate()
        app.launch()
        XCTAssertTrue(app.buttons["show-report"].waitForExistence(timeout: 15))
        XCTAssertTrue(app.staticTexts["zone-count-left"].label.contains("10 Plättchen"))
        app.buttons["show-report"].tap()
        XCTAssertTrue(app.staticTexts["report-answer"].waitForExistence(timeout: 5))
        XCTAssertEqual(app.staticTexts["report-answer"].label, "Abgegebene Zahl: 15")
        XCTAssertTrue(app.staticTexts["report-path"].label.contains("ohne vorherigen Hinweis"))
    }

    @MainActor
    func testAllDigitsRemainReachableAfterHelpAndReportInBothOrientations() {
        let app = launchNotebook()
        defer { XCUIDevice.shared.orientation = .portrait }
        app.buttons["show-help"].tap()
        for orientation in [UIDeviceOrientation.portrait, .landscapeLeft] {
            XCUIDevice.shared.orientation = orientation
            for digit in 0...9 { XCTAssertTrue(app.buttons["digit-\(digit)"].isHittable) }
            app.buttons["show-report"].tap()
            XCTAssertTrue(app.buttons["return-to-number-pad"].waitForExistence(timeout: 5))
            app.buttons["return-to-number-pad"].tap()
            XCTAssertTrue(app.buttons["digit-7"].isHittable)
            app.buttons["digit-7"].tap()
            app.buttons["digit-clear"].tap()
        }
    }

    @MainActor
    func testUndoRemovesOnlyTheEffectiveMove() {
        let app = launchNotebook()
        reveal(app.buttons["token-b1"], in: app)
        app.buttons["token-b1"].tap()
        app.buttons["token-b2"].tap()
        app.buttons["place-left"].tap()
        reveal(app.buttons["undo"], in: app)
        app.buttons["undo"].tap()
        XCTAssertTrue(app.staticTexts["zone-count-left"].label.contains("8 Plättchen"))
        app.buttons["show-report"].tap()
        XCTAssertTrue(app.staticTexts["report-path"].waitForExistence(timeout: 5))
        XCTAssertEqual(app.staticTexts["report-path"].label, "Zum dargestellten Weg ist noch keine Aussage belegt.")
    }
}
