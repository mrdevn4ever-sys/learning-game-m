import UIKit
import XCTest

final class RepairNotebookUITests: XCTestCase {
    @MainActor
    private func launchNotebook() -> XCUIApplication {
        continueAfterFailure = false
        XCUIDevice.shared.orientation = .portrait
        let app = XCUIApplication()
        app.launchArguments = ["--uitest-store", UUID().uuidString]
        app.launch()
        XCTAssertTrue(app.buttons["digit-1"].waitForExistence(timeout: 15))
        return app
    }

    @MainActor
    private func tap(_ identifier: String, in app: XCUIApplication) {
        let button = app.buttons[identifier]
        for _ in 0..<8 {
            if button.isHittable { button.tap(); return }
            app.scrollViews.firstMatch.swipeDown()
        }
        for _ in 0..<12 {
            if button.isHittable { button.tap(); return }
            app.scrollViews.firstMatch.swipeUp()
        }
        XCTFail("Bedienelement nicht erreichbar: \(identifier)")
    }

    @MainActor
    private func place(_ items: [String], in zone: String, app: XCUIApplication) {
        for item in items { tap("token-" + item, in: app) }
        tap("place-" + zone, in: app)
    }

    @MainActor
    private func counts(_ left: Int, _ right: Int, _ spare: Int, app: XCUIApplication) {
        for (zone, count) in [("left", left), ("right", right), ("spare", spare)] {
            XCTAssertTrue(app.staticTexts["zone-count-" + zone].label.contains("\(count) Plättchen"))
        }
    }

    @MainActor
    private func checkLoggedHelp(_ visible: String, app: XCUIApplication) {
        tap("show-report", in: app)
        XCTAssertTrue(app.staticTexts["report-help-count"].waitForExistence(timeout: 5))
        let logged = app.staticTexts.matching(NSPredicate(format: "identifier BEGINSWITH %@ AND label == %@", "logged-help-", visible)).firstMatch
        for _ in 0..<12 {
            if logged.exists { break }
            app.swipeUp()
        }
        XCTAssertTrue(logged.exists, "Sichtbarer Hilfetext fehlt im Ereignisprotokoll")
        tap("return-to-number-pad", in: app)
    }

    @MainActor
    private func restartAndOpenReport(_ app: XCUIApplication) {
        app.terminate()
        app.launch()
        XCTAssertTrue(app.buttons["show-report"].waitForExistence(timeout: 15))
        tap("show-report", in: app)
        XCTAssertTrue(app.staticTexts["report-path"].waitForExistence(timeout: 5))
    }

    @MainActor
    func testNineSixHelpRequiresOneTokenAndPersistsExactText() {
        let app = launchNotebook()
        place(["b1"], in: "left", app: app)
        counts(9, 6, 0, app: app)
        tap("show-help", in: app)
        let text = app.staticTexts["help-text"].label
        XCTAssertTrue(text.contains("noch ein Plättchen von B nach A"))
        counts(9, 6, 0, app: app)
        checkLoggedHelp(text, app: app)
        place(["b2"], in: "left", app: app)
        counts(10, 5, 0, app: app)
        XCTAssertFalse(app.staticTexts["help-text"].exists)
        restartAndOpenReport(app)
        XCTAssertTrue(app.staticTexts["report-path"].label.contains("nach einem Hinweis"))
        XCTAssertEqual(app.staticTexts["report-help-count"].label, "Gezeigte Hilfen: 1")
    }

    @MainActor
    func testTenFiveHelpDoesNotAskForExtraTokensOrDowngradeFreeAction() {
        let app = launchNotebook()
        place(["b1", "b2"], in: "left", app: app)
        tap("show-help", in: app)
        let text = app.staticTexts["help-text"].label
        XCTAssertTrue(text.contains("kein weiteres Plättchen"))
        counts(10, 5, 0, app: app)
        checkLoggedHelp(text, app: app)
        restartAndOpenReport(app)
        XCTAssertTrue(app.staticTexts["report-path"].label.contains("ohne vorherigen Hinweis"))
    }

    @MainActor
    func testSevenSevenOneHelpPreservesAlternativeWithoutSilentReset() {
        let app = launchNotebook()
        place(["a1"], in: "spare", app: app)
        tap("show-help", in: app)
        let text = app.staticTexts["help-text"].label
        XCTAssertTrue(text.contains("anderer passender Weg"))
        XCTAssertTrue(text.contains("zuerst das Plättchen aus C nach A"))
        counts(7, 7, 1, app: app)
        checkLoggedHelp(text, app: app)
        place(["a1"], in: "left", app: app)
        counts(8, 7, 0, app: app)
        place(["b1", "b2"], in: "left", app: app)
        counts(10, 5, 0, app: app)
        restartAndOpenReport(app)
        XCTAssertTrue(app.staticTexts["report-path"].label.contains("nach einem Hinweis"))
    }

    @MainActor
    func testHelpAfterUndoUsesRestoredEightSevenAndKeepsEarlierLog() {
        let app = launchNotebook()
        place(["b1"], in: "left", app: app)
        tap("show-help", in: app)
        let firstText = app.staticTexts["help-text"].label
        tap("undo", in: app)
        counts(8, 7, 0, app: app)
        XCTAssertFalse(app.staticTexts["help-text"].exists)
        tap("show-help", in: app)
        let secondText = app.staticTexts["help-text"].label
        XCTAssertTrue(secondText.contains("zwei Plättchen von B nach A"))
        counts(8, 7, 0, app: app)
        checkLoggedHelp(firstText, app: app)
        checkLoggedHelp(secondText, app: app)
        restartAndOpenReport(app)
        XCTAssertEqual(app.staticTexts["report-help-count"].label, "Gezeigte Hilfen: 2")
    }

    @MainActor
    func testOwnInitialTokenReturnAfterHelpIsGuidedButHistoricalFreeStepSurvives() {
        let app = launchNotebook()
        place(["b1", "b2"], in: "left", app: app)
        place(["a1"], in: "spare", app: app)
        tap("show-help", in: app)
        counts(9, 5, 1, app: app)
        place(["a1"], in: "left", app: app)
        counts(10, 5, 0, app: app)
        restartAndOpenReport(app)
        XCTAssertTrue(app.staticTexts["report-path"].label.contains("nach einem Hinweis"))
        XCTAssertFalse(app.staticTexts["report-path"].label.contains("ohne vorherigen Hinweis"))
        XCTAssertTrue(app.staticTexts["report-historical-path"].label.contains("Früher in dieser Runde"))
    }

    @MainActor
    func testOwnUndoAfterHelpIsGuidedButHistoricalFreeStepSurvives() {
        let app = launchNotebook()
        place(["b1", "b2"], in: "left", app: app)
        place(["b1"], in: "right", app: app)
        counts(9, 6, 0, app: app)
        tap("show-help", in: app)
        tap("undo", in: app)
        counts(10, 5, 0, app: app)
        restartAndOpenReport(app)
        XCTAssertTrue(app.staticTexts["report-path"].label.contains("nach einem Hinweis"))
        XCTAssertFalse(app.staticTexts["report-path"].label.contains("ohne vorherigen Hinweis"))
        XCTAssertTrue(app.staticTexts["report-historical-path"].label.contains("Früher in dieser Runde"))
    }
}
