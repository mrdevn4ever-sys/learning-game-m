# Red-Team-Register

Ausgangskandidat: `144c9b3f8a2b03907cca41ed30ac81fdc196d91d`, Basis `53b73ebd765fb9ab2c2a63940ec16912ca95a0e7`.
Unabhaengiger Kontext, kein technischer Freigabedienst. Historische Befunde werden nicht rueckwirkend geaendert.

## RT-01 — hoch — offen
Gemeinsame Adminidentitaet kann Produkt und privaten Pruefbereich lesen. Secret-Namen/Jobbezeichnungen erzwingen keine Isolation. PR-Schutz ist keine Rollentrennung. Sperrt private Abnahme und Release. Abhilfe: getrennte Credentials/ACLs und positive wie negative Zugriffsnachweise.

## RT-02 — hoch — offen
Freigabeservice, authentisierte Aussteller, positive Fallzahlen und exakte Artefaktbindung fehlen. Startgraph P0-08 bis P0-10 bindet P0-05/P0-06 nicht ein. Belegschema erlaubt passed mit none/leerem Kandidaten/fehlenden Digests. Kein ausfuehrbarer Release-Bypass vorhanden, aber keine Freigabefaehigkeit. Abhilfe: fail-closed Validator, Abhaengigkeitsreparatur fuer neue Revision, unabhaengige Negativtests.

## RT-03 — mittel — offen
v0-Schemas erlauben leere Voraussetzungen, drei gleiche Pflichtfaelle, Abschluss ohne Grund, Korrektur ohne Lesartbezug sowie Kind plus App-Demo/doppelte Plattchen-IDs. Abhilfe: typgebundene v1-Vertraege und semantische Integritaetspruefung. Formale Schemaakzeptanz ist kein fachlicher Nachweis.

## Ergaenzende Fachbefunde
Quellenzuordnung mit "Fassung zu bestimmen" ist nicht geprueft. Ein Zehnerweg erzwingt keine korrekte Ergebniseingabe. Fallback nur mit eigener Regel ausgeben. Spaeter Hinweis entwertet keinen frueheren freien Schritt; Undo entfernt keinen erhaltenen Hinweis. Diese Faelle muessen offene Regressionen werden.

## Entwicklungskandidaten vom 2026-11-24: unabhaengiges FAIL

Originalberichte verlustfrei als `utf-8-lines`-JSON und mit SHA-256 gebunden unter `steuerung/gedaechtnis/pruefergebnisse/2026-11-24-code-reviews/`; `index.json` bindet Container, bytegenau rekonstruierbaren Originalbericht, Basis und Kandidat. Die Original-Markdowndateien bleiben ausserhalb Git unveraendert; ihre bedeutungstragenden Markdown-Zeilenenden werden nicht fuer das unveraenderte Whitespace-Gate umgeschrieben. Alle drei Kandidaten sind fuer Entwicklungsintegration gesperrt. Gruene Bestandslaeufe beseitigen keinen Befund. Die folgenden IDs gelten zusaetzlich, ohne RT-01/02/03 rueckwirkend umzuschreiben.

### Steuerung: `3bf45a586478a1c38ba8563bef7d0e8ad22e06e6`

- **RT-04 / R-01 — mittel — offen:** Restore zieht gespeicherte Retry-/Wirkungsabgleichfristen auf die Restorezeit vor. Zwei unabhaengige Negativtests im Review gescheitert und vom Orchestrator erneut reproduziert. Quarantaene/Unsicherheitsmarker bleiben vorhanden; kein Wiederholungsupload nachgewiesen. Fristen bei Restore erhalten, mit Vor-/An-/Nach-Frist-Kontrollen und unveraenderten Fencing-Gates pruefen.

### Referenz: `b8cd111453b2c44d28a5fc21125c4f9dbc95877e`

- **RT-05 / F01 — hoch — offen:** Luecke wird als sichere Inaktivitaet oder unveraenderter Modus/Undo-Zustand verwendet; spaetere gueltige Korrektur/direkte Antwort wird verworfen. Fehlendes Wissen je Objekt von bewiesenem Widerspruch trennen. `inactive_answer` und `mode_mismatch` vom Orchestrator reproduziert.
- **RT-06 / F02 — hoch — offen:** Eine alte Luecke deaktiviert auch frisch erneut belegte Ausgangszonenpruefung. Ungueltige Spur bekommt positiven Ergebnisclaim; vom Orchestrator reproduziert. Neu gewonnenes Einzelwissen muss wieder verbindlich sein.
- **RT-07 / F03 — hoch — offen:** App-Detour mit App-Undo datiert einen unveraendert erhaltenen freien Kind-Zug nach Hilfe um und erfindet einen Guided-Claim; vom Orchestrator reproduziert. Akteur und wirksame Handlung getrennt vom blossen Brettuebergang auswerten.
- **RT-08 / F04 — mittel — offen:** Gleichwertiger 5/10-Zehnerweg wird trotz allgemeinem Wortlaut als nicht dargestellter passender Weg behandelt. Zukuenftige fachliche Vertragskorrektur und unabhaengige Regression erforderlich.
- **RT-09 / F05 — mittel — offen:** Gezielte Invalidierung eines Selbstberichts/Materialbelegs sperrt eine unabhaengige direkte richtige Antwort. Abhaengigkeitsbezogene Neuberechnung statt globaler Sperre; bestehender Sollkonflikt muss prospektiv und versioniert entschieden werden.
- **RT-10 / F06 — mittel — offen:** Jede App-Bewegung wird ohne Zielbeleg zum Zehnerhinweis. Allgemeine Unterstuetzung, konkrete Hilfewirkung und unbekannte Wirkung trennen; keine positive spezifische Aussage ohne Nachweis.
- **O01 — offene Abdeckungsgrenze:** Vollstaendiger Neuaufbau aller Plattchen nach Luecke bleibt dauerhaft unbekannt. Dokumentierte Einschraenkung, kein zusaetzlicher eigenstaendiger Grund fuer das Review-FAIL; neu gewonnenes Wissen kuenftig auswerten.

### iPad: `d71acbe65a602f091840ed5fa7e6069a157843c2`

- **RT-11 / IPAD-01 — hoch — offen:** Kind verlaesst Zehnerdarstellung und erreicht sie nach Hilfe erneut per Zug/Undo, erhaelt aber wieder einen Hilfefreiheitsclaim. Aktuelle Darstellung und historischen freien Schritt akteurbewusst trennen. Kein Widerspruch zu RT-07: dort nimmt ausschliesslich die App ihren eigenen Eingriff zurueck.
- **RT-12 / IPAD-02 — hoch — offen:** Luecke nach Antwort laesst deren positive oder negative aktuelle Bewertung bestehen. Antwortaktualitaet muss unbekannt werden; neue direkte Antwort danach darf eng beurteilbar sein.
- **RT-13 / IPAD-03 — mittel — offen:** Unveraenderter Hilfetext fordert nach Teilzug weitere zwei Plattchen und fuehrt zu 11/4. Hilfeinhalt muss zur tatsaechlichen Seite passen und genau so protokolliert werden.
- **RT-14 / IPAD-04 — mittel — offen:** Undo wird unabhaengig vom Ursprungsakteur dem Kind zugeschrieben; korrekte App-Ruecknahme wird verworfen. Bedienanforderung und Akteur der fachlichen Ruecknahme trennen.
- **RT-15 / IPAD-05 — mittel — offen:** Unveraenderte oder nichtnumerische Lesarten werden als korrigiert akzeptiert. Numerische Lesarten und disjunkte Bestaetigungs-/Korrekturprovenienz validieren; niemals daraus einen Rechenfehler erzeugen.

iPad-Befunde sind Quellbefunde mit reproduzierbaren Python-Erlaeuterungen, keine Swift-Ausfuehrung. Native Reproduktion und alle nativen Gates bleiben offen. Reparaturversuch 1 ist getrennt pro Arbeitsbranch beauftragt; kein Befund geschlossen. Gremium prueft den prospektiven Semantik-/Versionierungsentwurf D1-D6; kein Mehrheitsentscheid vorweggenommen.
