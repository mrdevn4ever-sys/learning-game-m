# Plattformneutraler Swift-6-Entwicklungskern

Sieben explizite Module, keine Drittanbieter-Package-Abhängigkeiten. Testaufruf
vom Repository-Root: `swift test --package-path produkt/Packages`.
Für externe Build-/Cachepfade und native Befehle siehe
[../App/README.md](../App/README.md).

## Grenzen

| Modul | Direkte Abhängigkeiten | Verantwortung |
|---|---|---|
| CoreDomain | keine | Dreiwertige Fakten, einzelne ClaimRule, Akteure/Zonen/Revisionen; keine Lösung |
| ObservationLog | CoreDomain | Typisierte Ereignisse, Hülle, Stream-/ID-/Sequenzintegrität, Idempotenz |
| TaskEngine | CoreDomain, ObservationLog | Synthetische Aufgabe, Anfangsmaterial, definitive Antworten, gültige Bewegungen und Replay |
| LearningEngine | CoreDomain, ObservationLog, TaskEngine | Enge Aussagen aus gültigen wirksamen Ereignissen; keine gespeicherten Leistungswerte |
| EvidenceKit | CoreDomain, ObservationLog, LearningEngine | Entwicklungsansicht mit synthetischem Geltungsbereich und `open`/`none`, keine Abnahme |
| InputKit | keine | Ziffernpuffer, formale Strichpunkte und erwartete Zeichenart; keine Aufgabe |
| RecognitionKit | InputKit | Ausdrücklich `notImplemented`; keine Lesarten und keine Lösung |

RecognitionKit erreicht TaskEngine auch nicht transitiv. Der statische Check
und seine negativen Selbsttests sperren eine solche Änderung. Die App erzeugt
weder `recognition.proposed` noch künstliche Konfidenzen. Solche Ereignisse gibt
es nur als direkt aufgebaute, offene synthetische Regressionen im Testcode.

## Eigene typisierte APIs, noch kein gemeinsamer v1-Vertrag

Dies ist ein isolierter Entwicklungsadapter. Die öffentlichen v0-Beispiele
wurden gelesen, aber weder überschrieben noch zu einem erfundenen v1 erklärt.
Codable-Synthese und Swift-Enum-Fallnamen sind **kein Export-/Austauschformat**.
Es gibt bewusst keinen JSON-v1-Importer, keinen privaten Prüfsatz und keinen
vorgeblichen Referenzprüfer-Abgleich.

- `TaskEngine.open(streamID:) -> EventLedger`: öffnet genau das synthetische
  Profil und eine unvorbereitete 8+7-Materialseite; keine gelöste Darstellung.
- `submit(_:to:)`: validiert direkte ASCII-Ziffern, protokolliert
  `inputCaptured` und `answerCommitted` atomar im zurückgegebenen Ledger.
  Eine ältere aktive Antwort wird zuerst gezielt zurückgenommen. Nur eine
  definitive Antwort kann ein Ergebnis erzeugen. **Abgeben** zählt in dieser
  lokalen API als Ergebnisabgabe; `close(_:reason:)` beendet separat die Runde.
- `move(items:to:in:)`: setzt nur ausdrücklich gewählte existierende Plättchen
  desselben Ursprungsfeldes um. Keine automatische Wahl von zwei Plättchen.
  `undo(in:)` erzeugt eine gezielte Rücknahme, nie eine Historienlöschung.
- `presentSupport(in:)`: protokolliert den tatsächlich angezeigten
  `Support.tenStep` mit versionsgebundenem Text, Ziel, Wirkung und Kanal.
  Die UI persistiert zuerst und zeigt danach genau diesen Text. Erst ein
  unabhängiger Bildschirmabgleich kann die Rendergrenze bestätigen.
- `TaskEngine.replay(_:) -> AttemptState`: prüft Eröffnung, Revision, Akteur,
  Eingabe-/Lesartbezüge, Materialherkunft, Zielzustand und Rücknahmen.
  Semantisch ungültige Spuren werfen Fehler; es gibt keine stille Reparatur.
- `LearningEngine.report(from:)`: erzeugt nur Aussagen für diesen Versuch.
  Ergebnis, eigene Materialdarstellung, vorheriger Zehnerhinweis und anderer
  Weg 7+7+1 sind getrennt. Keine ganze Kompetenzstufe wird als erreicht markiert.
- `DevelopmentEvidence(ledger:)`: nennt Ereignisanzahl und offene
  Entwicklungsgrenze. Nicht mit einem signierten Freigabebeleg verwechseln.
- `DisabledRecognizer.recognize(_:expected:)`: liefert ausschliesslich
  `notImplemented`; erwartet Striche/Zeichenart, niemals Aufgabe oder Lösung.

`Event.id` ist die UUID für Bewegungs-/Antwortrücknahmen. `CapturedInput.id`
und `ProposedReading.id` sind separate Referenzen. `actor = learner` bezeichnet
hier einen synthetischen Bedienakteur und ist **nicht** bereits der gemeinsame
Wire-Wert `child`. Der konkrete lokale Anfangszustand und Revisionen sind
streng gebunden. Der einzige Eröffnungsprofilwert ist synthetisch.

`EventLedger` nimmt identische doppelte Zustellung einmal an. Andere Inhalte
bei gleicher ID, gleiche Sequenz mit anderer ID, fremde Streams und rückwärts
laufende Zustellung scheitern. Sequenzlücken werden nicht aufgefüllt: Replay
setzt die Beobachtung auf unvollständig. Eine explizite Lückenmeldung tut das
auch. Ein nachweislich abgegebenes richtiges Ergebnis bleibt erhalten; davon
abhängige Weg-/Unabhängigkeitsaussagen bleiben `unknown`.

## Zeit, Hilfe und wirksame Handlungen

Aussagen hängen an der Ereignisreihenfolge, nicht an ungesicherter Gerätezeit.
Jeder aktive Zug merkt sich den Hilfestand **vor diesem Zug**. Aktuell umgelegte
Plättchen werden auf ihren letzten noch wirksamen Zug zurückgeführt.

- Hinweis nach dem abgeschlossenen Zehnerschritt: freier Schritt bleibt frei.
- Undo und erneuter Zug nach Hinweis: der neue Schritt ist angeleitet.
- App-Demo und Wiederholung: App-Herkunft ist kein eigener Schritt; das durch
  die Demo vermittelte Hilfewissen bleibt auch nach Undo vorhanden.
- Unbekanntes Hilfefaktum ist niemals belegte Abwesenheit.
- Eine Lesart allein erzeugt weder ein richtiges noch ein falsches Ergebnis.
  Erst korrigierte oder bestätigte definitive Antworten werden ausgewertet.
- Ein falscher Zahlenwert erlaubt keine Diagnose seiner Ursache.

Die lokale Wegerkennung ist absichtlich eng: 10+5 aus der ursprünglichen Acht
oder 7+7+1 mit unveränderter Siebenergruppe. Andere Anordnungen werden nicht
als falsch behauptet; ihr Wegnachweis bleibt offen. Dies ist kein allgemeiner
Strategieerkenner, kein Auswahl- oder Adaptionssystem.

## Noch abzugleichen

Der zuständige Vertragsanteil muss Ereignisabbildung, Hilfekanal/-wirkung,
Abgabe-/Abschlusssemantik, Referenzen, Revisionsbindung, Lückenregeln und jede
Claim-Regel gegen den gemeinsamen Vertrag prüfen. Erst danach kann ein
versionierter Adapter eingeführt und mit dem getrennten Referenzprüfer
verglichen werden. Änderungen am lokalen Speicherformat benötigen dann eine
explizite Migration oder einen sichtbaren Inkompatibilitätszustand; historische
Ereignisse und Hilfe dürfen nicht still neu gedeutet werden.

Die Swift-Testing-Dateien sind vorbereitete ausführbare Regressionen, keine
bestandenen Tests auf dem Windows-Host. Kein Beleg über reale Kinder und keine
verdeckte Schlussabnahme wird daraus abgeleitet.
