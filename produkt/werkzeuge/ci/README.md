# Oeffentliche Entwicklungs-CI: gebundene native Diagnose

Kein Freigabedienst. Nur offene synthetische Regressionen, `contents: read`,
keine persistierten Checkout-Credentials, Secrets, privilegierten Trigger,
Artefaktuploads, Signing- oder Apple-Aktionen. Builddateien/xcresult bleiben
im temporaeren Runner. Nur offene Compiler-/Testlogs und Zaehler werden sichtbar.

- `preflight`: JSON/Schemadefinitionen, Syntax, offene Referenztests inklusive
  gepinnter RFC-3339-Abhaengigkeiten, App-Quelltests, Rechteinventar,
  Credentialmuster, Workflowsecurity-Mutationen und CI-Helfertests.
- `product-check`: unabhaengige echte Swift-Tests, SwiftData und XCUITest auf
  einem vorhandenen iPad-Simulator, danach unsignierter Release-Simulatorbuild.
  Bei Produktfehlern werden Folgegates NOT RUN ausgewiesen, nicht uebersprungen
  und als Erfolg umgedeutet. Originalquellen werden nicht repariert.
- `recovery-drill`: lokale deterministische Proben mit synthetischen Wirkungen;
  kein Apple-Uploadtest und keine Aufhebung des archivierten Restore-Befunds.
- `integration-review-block`: eigener deterministischer FAIL-Job. Er prueft den
  unveraenderten Index und die drei Originalberichte einschliesslich Container-
  und UTF-8-Inhaltsdigests und Kandidatenbindung. Die bekannten drei FAILs sperren
  Integration; ein gruener nativer Lauf kann diese Urteile nicht ueberstimmen.
  Dieser Job ist bewusst keine Abhaengigkeit der nativen Diagnose.

## Vorab gebundene Erwartungen

`native-contract.json` uebernimmt die exakten Snapshotinputs; keine beweglichen
Reparaturbranches werden eingelesen. Die vor jedem Lauf geprueften Quelltrees und
Dateibytes binden die **43 Package-, 4 SwiftData- und 5 UI-Testdefinitionen**.
Dateien, Funktionsnamen und erwartete Fallzahlen sind vor Ausfuehrung festgehalten.
Tatsaechliche Ausfuehrung wird davon getrennt aus Swift-Testing-xUnit bzw.
xcresult-Summary **und** Testbaum gezaehlt. Fehlende, fremde, doppelte, leere,
uebersprungene oder suitefehlerhafte Tests sperren. Kein Mindestwert 1 als Ersatz.
Die SwiftPM-XCTest-Ausgabe (keine XCTest-Package-Definitionen) ist kein Ersatz
fuer die separate `swift-swift-testing.xml` mit den 43 Swift-Testing-Faellen.

Der Workflow checkt beim PR explizit dessen Head-SHA aus und vergleicht ihn vor
Ausfuehrung mit dem Ereignis. Die native Abschlusszeile `NATIVE_DIAGNOSIS` bindet
Quell-SHA, Run-ID, Versuch, Toolchain, Simulator, erwartete/ausgefuehrte Zahlen,
Stufen und Logdigests. Nicht lesbare Ergebnisse bleiben unbekannt, nicht gruen.
Keine Logs/Builds werden als Repositorydateien oder Actions-Artefakte hochgeladen.

Toolchainquelle live gelesen: `actions/runner-images`,
`images/macos/xcode-27-arm64-Readme.md`, Image `20261104.0337.1`.
`xcode-27` ist ein macOS-arm64-Runner; explizite Installation
`/Applications/Xcode_27.2.app`, SDK 27.2. Der native Lauf verifiziert die Auswahl
und waehlt einen tatsaechlich verfuegbaren kompatiblen iPad-UDID. Kein Hardwarebeleg.

## Lokale Pruefung

```sh
python -m pip install -r produkt/werkzeuge/ci/requirements.txt -r produkt/werkzeuge/referenz/requirements.txt
python produkt/werkzeuge/ci/run_suite.py produkt/werkzeuge/ci/tests
python produkt/werkzeuge/ci/preflight.py
python produkt/werkzeuge/ci/snapshot.py --local-inputs F:/ChnobelRuntime/verification/native-snapshot-inputs.json
python produkt/werkzeuge/ci/review_gate.py # Erwartet Exit 1: drei originale FAILs
bash -n produkt/werkzeuge/ci/native.sh
```

Private Abnahme, freeze-build, issue-verdict, release-internal und echter externer
reconcile-Dienst sind nicht implementiert/freigegeben. Keine Dummyjobs,
keine Auftrags- oder Statusaenderung, kein Merge. Ein Diagnose-PASS ist weder
Phase-0-Abnahme noch Freigabe eines integrierten Kandidaten.
