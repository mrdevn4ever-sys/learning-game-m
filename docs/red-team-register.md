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
