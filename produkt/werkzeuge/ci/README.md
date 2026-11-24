# Oeffentliche Entwicklungs-CI

Kein Freigabedienst. Nur oeffentliche synthetische Regressionen, `contents: read`, kein persistiertes Checkout-Credential, keine Secrets und keine Artefakt-Uploads. Native Builddateien/xcresult bleiben im temporaeren Runner und werden nicht publiziert. UI-Ergebnisse muessen echte positive Fallzahlen liefern; skipped/leer ist kein Erfolg.

`preflight`: JSON/Schemadefinitionen, Syntax, oeffentliche Referenztests, Quellgrenzen, Rechteinventar, Credential-Muster und CI-Helfertests.
`product-check`: echte Swift-Tests, XCUITest auf real vorhandenem iPad-Simulator und unsignierter Release-Simulatorbuild.
`recovery-drill`: lokale deterministische Betriebsproben mit synthetischen externen Wirkungen. Kein Apple-Uploadtest.

Noch nicht implementiert und nicht bestanden: freeze-build, independent-check, issue-verdict, release-internal und echter externer reconcile-Dienst. Sie werden erst mit technisch getrennten Credentials und sicheren Artefaktwegen aktiviert. Keine Dummyjobs/skip-success.

Toolchainquelle am 2026-11-24: actions/runner-images/images/macos/xcode-27-arm64-Readme.md, stabile Xcode-27.2-Installation `/Applications/Xcode_27.2.app`. `xcode-27` ist ein macOS-Runner; Label und Installation werden nativ verifiziert. Ein Quellcheck ist kein Buildnachweis.

Lokale CI-Helfertests: `python -m unittest discover -s produkt/werkzeuge/ci/tests -v`. Skriptberichte sind Entwicklungsergebnisse, keine authentisierten Freigabebelege. Erwartete endgueltige Fallzahlen und Schwellen muessen vor der unabhaengigen Abnahme unveraenderlich festgelegt werden.
