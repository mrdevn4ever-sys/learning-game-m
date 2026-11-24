# iPad-Reparaturversuch 1: lokale Semantik

Ausgangspunkt: `d71acbe65a602f091840ed5fa7e6069a157843c2`.
Der ursprüngliche Kandidat und sein fremdes FAIL-Review bleiben unverändert.
Dies beschreibt einen **neuen, noch nicht fremd freigegebenen** Kandidaten.
Keine Phase-0-/Phase-2-Abnahme, keine Schlussabnahme und kein v1-Adapter.

## Änderungen

- **IPAD-02:** Antwortaktualität ist ein eigenes dreiwertiges Faktum. Explizite
  und Sequenzlücken machen frühere Antworten unbekannt, unabhängig vom
  Zahlenwert. Neue beobachtete Abgaben sind wieder beurteilbar. Abschluss,
  Undo-Auswahl und UI berücksichtigen diese Grenze. Eine historische Rücknahme
  heilt die Lücke nicht und erfindet keine bewiesene Antwortabwesenheit.
- **IPAD-03:** Die protokollierte Hilfe wird aus der aktuellen Materialverteilung
  ausgewählt. 8/7 verlangt zwei Plättchen, 9/6 nur eines; 10/5 verlangt keinen
  weiteren Zug. 7/7/1 bleibt ein passender anderer Weg; ein freiwilliger Wechsel
  wird ausdrücklich beschrieben. Keine Materialänderung durch Hilfe, kein
  stiller Reset. Bewegung/Undo blendet den alten Tipp aus, ohne das protokollierte
  Hilfewissen zu löschen. Neue Hilfe erhält ein neues Ereignis.
- **IPAD-04:** Replay verlangt den Akteur der ursprünglichen Bewegung. Der
  Undo-Helfer übernimmt genau diesen Akteur, auch bei App-Bewegungen. Eine
  Bedienanforderung wird nicht als neue Kind-Materialhandlung ausgegeben.
- **IPAD-05:** Lesarten müssen ASCII-Ziffern im lokalen Zahlenraum sein.
  `confirmed` verlangt denselben Zahlenwert, `corrected` einen anderen.
  `015` ist keine Korrektur von `15`. Ungültige Provenienz ist ein Replayfehler,
  nie eine mathematische Fehlleistung. RecognitionKit bleibt deaktiviert.
- **IPAD-01:** Ein eigener Aktionsanker ergänzt die Materialprovenienz.
  Historische Kind-Handlungen und aktuelle Darstellung sind getrennt.
  Eigener Detour und eigene Rückkehr/Undo nach Hilfe erhalten einen neuen
  angeleiteten Anker. Hilfe allein lässt den alten freien Anker unverändert.
  App-Detour/App-Undo suspendiert und reaktiviert dagegen nur den unveränderten
  Kind-Anker: kein neuer Kind-Zeitpunkt und kein rückwirkender Guided-Claim.
  Das ist ausdrücklich **kein globaler Brett-Zeitanker**.

## Versions- und Speichergrenze

`Revision.development` ist `local-draft-1`, `LocalNotebookSnapshot.localFormat`
ist 1. Beides sind lokale Entwicklungsnummern, keine gemeinsame Vertragsversion.
Format 0/alte Ereignisrevisionen werden mit unverändertem gespeicherten Payload
abgelehnt. Es gibt weder eine stille Migration noch einen automatischen Reset.
Die UI zeigt den bestehenden Nicht-geladen-Zustand; eine echte Migration bleibt
separat zu entwickeln und zu prüfen.

Die ursprünglichen 43 Package-, 4 Session- und 5 UI-Testdefinitionen sowie die
14 statischen Tests sind unverändert. `Tools/repair-baseline.json` bindet die
ursprünglichen Testdateien per normalisiertem SHA-256 an den Ausgangskandidaten.
Neue Regressionen liegen in eigenen Dateien. Keine bestehende Erwartung wurde
geändert, kein Fall entfernt, kein Test deaktiviert.

## Offene semantische Grenzen für fremdes Review

Die im Reparaturauftrag konkret verlangten IPAD-01-Fälle sind als getrennte
native Regressionen vorbereitet. Keine neue Architektur-/Gremiumsentscheidung
wird durch dieses Dokument vorweggenommen.

- **Gemischte Intervention:** Nach App-Detour, zusätzlichem Kind-Detour/eigenem
  Undo und erst danach App-Undo ist der alte Anker nicht mehr unverändert.
  `learnerInterventionCannotResumeSuspendedOldAnchor` verlangt deshalb keinen
  aktuellen freien oder angeleiteten Claim; der historische freie Schritt bleibt.
  Der enge Materialclaim bleibt erreichbar. Diese zusätzliche Grenze muss der
  fremde Review gegen die versionierte gemeinsame Aktionssemantik prüfen.
- **D5/Sollkonflikt bleibt sichtbar:**
  `unrelatedAppMovementIsNotInventedAsATenHint` erwartet nach einer ausschliesslichen
  7/7/1-App-Demo mit Undo vor dem neuen Kind-Zehnerweg weiterhin `unknown` für
  spezifische Hilfefreiheit und spezifisches Guided. Die bestehende Erwartung
  und `hasUnclassifiedDemo` wurden nicht heimlich in eine positive oder negative
  Aussage umgedeutet. Ein anders entschiedener gemeinsamer Sollwert benötigt
  eine explizite Revision und Gegenprüfung, nicht Testlockerung.
- D2 über die Antwortaktualität hinaus (objektweise Material-/Moduskenntnis und
  Undo-Abhängigkeiten nach Lücken), D3 (allgemeiner 5/10-Weg) und D4 (gezielte
  Invalidierungen) sind durch diese lokale Reparatur **nicht erledigt**.
- Ereignishülle, Abgabe/Abschluss, allgemeine Materialprovenienz, Lifecycle,
  v1-Regelimport und Referenzabgleich bleiben die dokumentierten Integrationsgates.

## Prüfdefinitionen und Grenzen

Neue echte Swift-Testing-Definitionen:

- `Packages/Tests/TaskEngineTests/RepairContractTests.swift`: zustandsgerechte
  Hilfen, Undo-Akteure und Fehlakteure, numerische/disjunkte Lesartprovenienz,
  neue Abgabe nach Lücke, strenger Abschluss.
- `Packages/Tests/LearningEngineTests/AnswerCurrencyTests.swift`: beide Lückenarten,
  beide Zahlenwerte, neue Antworten, wiederholte Lücken, historische Rücknahme,
  Lesarten ohne Mathematikfeedback und Integritätsfehler.
- `Packages/Tests/LearningEngineTests/ActorAnchorTests.swift`: historische/aktuelle
  Anker, eigene Rückkehr/Undo, spätere Hilfe, App-Roundtrip, verschachtelte
  App-Handlungen, gemischte Intervention und Replay-Restore.
- `ChnobelTests/RepairSessionTests.swift`: echte SwiftData-Speicheraufrufe mit
  Wiederaufnahme, Hilfe/Undo, Antwortaktualität, App-Akteur und ungültiger Lesart.
  Save-Fehlerinjektion erfolgt nach Änderung des ModelContext, vor `save()`;
  Rollback sowie unveränderte Session und erneut geladener Diskzustand werden
  geprüft. Das ist keine behauptete Speicherknappheits-/Hardware-Absturzprobe.
- `ChnobelUITests/RepairNotebookUITests.swift`: echte Taps auf 9/6, 10/5, 7/7/1,
  Undo, Kind-Detour/Rückkehr und Relaunch; sichtbarer Hilfetext gegen den in der
  Berichtsoberfläche angezeigten Ereignistext. Das ersetzt keinen unabhängigen
  Bildschirm-/Log-Abgleich oder den Nachweis einer eingeschleusten Manipulation.

Die neuen Python-Tests mutieren Quelltexte im Speicher und prüfen statische
Sperren. Sie simulieren weder Swift noch behaupten sie Swift-Semantik-PASS.
`verify_static.py --swift-parser` ergänzt nur einen Grammatikcheck, keinen
Apple-SDK-/Concurrency-Typecheck. Originale und neue statische Tests separat:

```bash
F:/ChnobelRuntime/venv/Scripts/python.exe -B -m unittest discover -s produkt/App/Tools -p test_static.py -v
F:/ChnobelRuntime/venv/Scripts/python.exe -B -m unittest discover -s produkt/App/Tools -p test_repair_static.py -v
F:/ChnobelRuntime/venv/Scripts/python.exe -B produkt/App/Tools/generate_project.py --check
F:/ChnobelRuntime/venv/Scripts/python.exe -B produkt/App/Tools/verify_static.py
```

Laufberichte dieses Versuchs liegen ausschliesslich unter
`F:/ChnobelRuntime/reparaturen/ipad-1`. Swift-Package-Ausführung, SwiftData-/Session-
Ausführung, XCUITest, Debug-/Release-Build und nativer Typecheck bleiben auf
Windows **NOT RUN**. Ein fremder nativer Lauf muss den exakten Kandidaten und
seine eigenen tatsächlich ausgeführten Fallzahlen ausweisen. Kein CI-Dispatch,
kein Push/Merge, keine Apple-Aktion und keine Änderung von Team-/Secretwerten.
`ch.chnobel.app` bleibt unverändert.
