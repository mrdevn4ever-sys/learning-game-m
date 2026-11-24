# Chnobel: iPad-Entwicklungsdurchstich

**Entwicklungs-App, keine Phase-0-Abnahme und keine TestFlight-Freigabe.**
Nur ein synthetisches lokales Profil und die eigene Aufgabe 8 + 7. Keine
Konten, echte Kinderprofile, Netzwerkfunktionen, Erkennungsleistung oder
Aussagen über Lernwirksamkeit. Signing bleibt ausgeschaltet.

## Bedienung

- Das Heft beginnt mit acht Kreisen in Feld A und sieben Quadraten in Feld B.
  Feld C ist frei. Kein Zehnerrahmen, keine vorausgewählten Plättchen, kein
  automatisch gelegter Lösungsweg.
- Ein oder mehrere Plättchen desselben Feldes antippen, dann im Zielfeld
  **Hier ablegen**. Farbe und Form unterscheiden die ursprünglichen Gruppen.
  So sind unter anderem 10 und 5 sowie 7, 7 und 1 selbst darstellbar.
- Der **Ziffernblock** bleibt im unteren sicheren Bereich. Es gibt keine
  Antwortvorbelegung. Zifferntasten unterstützen auch Hardware-Tastenkürzel.
  **Abgeben** schreibt Eingabe und definitive Antwort in einer Transaktion.
- **Hilfe** zeigt den zum aktuellen Materialzustand gewählten `Support.text`. Genau diese
  Hilfe wird als `support.presented` protokolliert, vor der UI-Freigabe
  gespeichert und nicht als Materialzug ausgeführt. Solange der Zustand passt,
  erzeugt ein erneuter Knopfdruck keine Scheinpräsentation. Ein Materialzug oder
  Undo blendet den alten Tipp aus; danach kann eine neue, passende Hilfe gewählt
  werden. Beide Hilfen bleiben unverändert im Protokoll, Hilfewissen bleibt erhalten.
- **Rückgängig** nimmt die zeitlich letzte noch wirksame Antwort oder Bewegung
  zurück. Die Historie wird nicht gelöscht. Hilfewissen wird nicht rückgängig
  gemacht. Eine spätere Hilfe entwertet keinen bereits wirksamen freien Zug.
- **Bericht** zeigt Ergebnis, engen Materialnachweis und die Ereignisnamen.
  Aktuelle Darstellung und früherer eigener Zehnerschritt sind getrennt.
  Eine Antwort vor einer späteren Lücke wird als historisch beobachtet mit
  offener Aktualität angezeigt, nicht als aktueller Erfolg oder Fehler.
  **Zum Ziffernblock** führt jederzeit zurück. Der Bericht ist ausdrücklich
  kein gesicherter Erwachsenenbereich; die Rollen sind synthetisch.
- **Runde beenden** schliesst einen abgegebenen Versuch. Er bleibt nach Neustart
  lesbar. **Neues Heft** ersetzt nach Bestätigung nur diese synthetische Seite.

## Speicherung und Fehler

`NotebookStore` speichert eine atomare SwiftData-Zeile mit Ereignissen und
noch nicht abgegebenem Ziffernentwurf. Berichte werden nie gespeichert,
sondern nach jedem Start neu aus dem Log berechnet. CloudKit ist explizit
`none`; das lokale Verzeichnis wird von Backups ausgeschlossen. Ein einziges
Fenster verhindert konkurrierende Schreibadapter in dieser Entwicklungsstufe.
Die Hauptansicht übernimmt einen neuen Zustand erst nach erfolgreichem Save.
Bei Schreibfehlern bleibt die vorherige Seite gültig. Beschädigte, unbekannte
oder semantisch ungültige Archive werden nicht still gelöscht oder ersetzt.

Der Debug-Startparameter `--uitest-store <UUID>` wählt einen isolierten
synthetischen Store im App-Sandbox-Verzeichnis, ohne automatische Löschung.
Release ignoriert diesen Parameter. Tests verwenden pro Test eine neue UUID
und beim Relaunch dieselbe UUID. UI-/Unit-Teststores verschwinden mit der
Deinstallation der Entwicklungs-App. Es gibt keine Exportfunktion.

Das lokale Codable-Format trägt `localFormat = 1`, die lokale Ereignisrevision
ist `local-draft-1`. Beides ist **kein gemeinsamer v1-Vertrag**. Format 0 und
alte Revisionen werden sichtbar als inkompatibel zurückgewiesen; vorhandene
Seiten bleiben unangetastet. Eine Migration ist nicht implementiert, und der
neue Kandidat behauptet keine rückwirkende Heilung alter Berichte.
Vertragsabgleich, Adapter und Migrationen folgen nach der Vertragsentwicklung;
Details stehen in [../Packages/README.md](../Packages/README.md).

## Build und Tests auf macOS

Voraussetzung: Swift 6, Xcode mit iPadOS-SDK und ein verfügbarer iPad-Simulator
ab iPadOS 18. Der Deployment Target ist 18.0; die tatsächlich verwendete
Xcode-/SDK-Version muss der native Lauf selbst ausweisen. Kein Apple-Konto,
kein Team, kein Provisioning-Profil und keine Signatur erforderlich.
Die kanonische App-ID ist `ch.chnobel.app`, das UI-Test-Target verwendet
`ch.chnobel.app.uitests`; das zusätzliche lokale Unit-Test-Bundle verwendet
`ch.chnobel.app.tests`. Keine Team-ID und keine Secrets werden eingecheckt.
Apple-Registrierung und spätere Signierberechtigung liegen ausschliesslich
beim Orchestrator; dieser Entwicklungsanteil führt keine Portalaktionen aus.

Alle folgenden Befehle starten **im Repository-Root**. Laufzeitdateien bleiben
ausserhalb des Repositorys. Auf dem Windows-Entwicklungsrechner ist dafür
`F:/ChnobelRuntime/ipad` reserviert. Der separate macOS-Runner setzt
`CHNOBEL_RUNTIME` auf seinen eigenen externen Laufzeitpfad. Nicht auf einen
fremden Projektcache zeigen.

```bash
: "${CHNOBEL_RUNTIME:?Externen Laufzeitpfad setzen}"
# Paketaufruf: swift test --package-path produkt/Packages
# Mit explizitem externem Build-/Cachepfad:
swift test --package-path produkt/Packages \
  --scratch-path "$CHNOBEL_RUNTIME/swift-build" \
  --cache-path "$CHNOBEL_RUNTIME/swift-cache"

xcodebuild -project produkt/App/Chnobel.xcodeproj -scheme Chnobel \
  -configuration Debug -sdk iphonesimulator \
  -destination 'generic/platform=iOS Simulator' \
  -derivedDataPath "$CHNOBEL_RUNTIME/DerivedData" \
  -clonedSourcePackagesDirPath "$CHNOBEL_RUNTIME/SourcePackages" \
  CODE_SIGNING_ALLOWED=NO build

# Zuerst eine wirklich vorhandene iPad-UDID ermitteln:
xcrun simctl list devices available
: "${CHNOBEL_IPAD_SIMULATOR_UDID:?iPad-Simulator auswaehlen}"
: "${RUN_LABEL:?Noch nicht vorhandenen Ergebnisnamen setzen}"
xcodebuild -project produkt/App/Chnobel.xcodeproj -scheme Chnobel \
  -configuration Debug -sdk iphonesimulator \
  -destination "platform=iOS Simulator,id=$CHNOBEL_IPAD_SIMULATOR_UDID" \
  -derivedDataPath "$CHNOBEL_RUNTIME/DerivedData" \
  -clonedSourcePackagesDirPath "$CHNOBEL_RUNTIME/SourcePackages" \
  -resultBundlePath "$CHNOBEL_RUNTIME/$RUN_LABEL.xcresult" \
  CODE_SIGNING_ALLOWED=NO test

xcodebuild -project produkt/App/Chnobel.xcodeproj -scheme Chnobel \
  -configuration Release -sdk iphonesimulator \
  -destination 'generic/platform=iOS Simulator' \
  -derivedDataPath "$CHNOBEL_RUNTIME/ReleaseDerivedData" \
  -clonedSourcePackagesDirPath "$CHNOBEL_RUNTIME/SourcePackages" \
  CODE_SIGNING_ALLOWED=NO build
```

Das shared Scheme **Chnobel** enthält `ChnobelTests` (Swift Testing für
SwiftData/Session) und `ChnobelUITests` (XCUITest für Zifferneingabe, Hilfe,
Neustart, Erreichbarkeit in beiden Ausrichtungen und Undo). Package-Tests
laufen separat mit `swift test`; keine Targets sind im Scheme übersprungen.
Binaries, xcresults, Archive und Laufberichte gehören nicht ins öffentliche
Repository und werden von diesem Entwicklungsanteil nicht hochgeladen.

## Statische Prüfungen auf Windows oder macOS

Nur Python-Standardbibliothek für diese Quellprüfungen erforderlich:

```bash
python produkt/App/Tools/generate_project.py --check
python -m unittest discover -s produkt/App/Tools -p test_static.py -v
python -m unittest discover -s produkt/App/Tools -p test_repair_static.py -v
python produkt/App/Tools/verify_static.py
```

`generate_project.py` erzeugt ohne `--check` das eingecheckte Xcode-Projekt und
shared Scheme reproduzierbar. Neue Swift-Dateien erfordern eine Erneuerung.
Die Prüfungen kontrollieren den Modulgraph, Quellenmitgliedschaft, Target- und
Scheme-Referenzen, Signing-Grenze, Privacy-Manifest und verbotene App-APIs.
Negative Selbsttests müssen bewusst verletzte Grenzen ablehnen.
Die ursprünglichen 14 statischen Tests bleiben unverändert. Reparaturgates
prüfen zusätzlich Quellverdrahtung, unveränderte ursprüngliche Testdateien und
neue native Testdefinitionen; sie führen keine Swift-Semantik in Python nach.
Details und verbleibende Grenzen: [REPARATUR-1.md](REPARATUR-1.md).

Optionaler Swift-Grammatikcheck (nur Syntax, **kein** Compiler/Typecheck):

```bash
# Nur ausserhalb des Repositories installieren. Keine App-Abhängigkeit.
# Windows-Pfad des hier benutzten Prüf-Interpreters:
F:/ChnobelRuntime/ipad/static-venv/Scripts/python.exe   produkt/App/Tools/verify_static.py --swift-parser   --report F:/ChnobelRuntime/ipad/static-report.json
```

Dieser Interpreter enthält `tree-sitter` und `tree-sitter-swift`. Python-Cache
über `PYTHONPYCACHEPREFIX` ebenfalls unter `F:/ChnobelRuntime/ipad` ablegen.
Die Grammatikprüfung ersetzt weder Swift-Testing-Ausführung noch SwiftUI- und
SwiftData-Typecheck. Das Werkzeug gibt vorbereitete Testanzahlen ausdrücklich
unter `prepared_tests_not_executed` aus.

## Offene native Gates

Auf dem Windows-Host sind `swift` und `xcodebuild` nicht vorhanden; beide
Aufrufe liefern `command not found` (127). Deshalb **NOT RUN**:

- Package-Tests im echten Swift-6-Compiler;
- unsigned Debug-/Release-Build, Projektauflösung und Apple-SDK-Typecheck;
- native SwiftData-Tests und XCUITests;
- installierte Oberfläche, VoiceOver, Schaltersteuerung, Dynamic Type,
  schmale iPad-Fenster, Hardware-Tastatur und visuelle Prüfung;
- Offline-Lauf bei gesperrtem Netz, Storagefehler/Absturz und Geräteschutz;
- unabhängiger Bildschirm-/Log-Abgleich und Abgleich mit dem Referenzprüfer.

Die Entwicklungs-App hat keinen Store-App-Icon-Satz und keine signierte
Release-/TestFlight-Pipeline. Handschrift ist nicht implementiert, Pencil- und
Kinderleistungsnachweise bleiben offen. Der lokale Source-Check ist kein
Freigabebeleg. Signing, Upload, Personenverwaltung, CI-Dispatch, Statusdateien,
Steuerungswerkzeug und Vertragsdateien wurden hier nicht verändert.

## Datenschutz und Herkunft

Das Privacy Manifest beschreibt: kein Tracking, keine Netzwerkübermittlung,
keine an den Anbieter erhobenen Daten, keine direkt genutzten Required-Reason-
APIs. Es ersetzt keine Prüfung des tatsächlich gebauten Binarys. Die App hat
keine Kamera-, Mikrofon- oder Spracherkennungs-Permissions, Analytics oder
Drittanbieter-Packages. SwiftData verarbeitet ausschliesslich synthetische
lokale Ereignisse. Herkunft und noch nötige zentrale Registrierung:
[RECHTE.md](RECHTE.md).
