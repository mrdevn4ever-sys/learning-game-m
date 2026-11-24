# Verträge 1.0.0

Kanonische Draft-2020-12-Schemas: `ereignis`, `beweisregel`, `belegstatus`.
Die HTTPS-IDs dienen nur als Identitäten. Der Prüfer lädt sie lokal und ruft
keine Website ab. Einbindung anderer Validatoren benötigt aktivierte UUID-
und RFC-3339-Formatprüfung sowie die zusätzlichen semantischen Prüfungen.

`spuren/*.json` ist ein lesbarer Umschlag aus `id`, `description`, `events` und
`expected`. `expected` enthält für alle fünf Aussagen je `must_claim`,
`must_not_claim` oder `undecidable`. `ungueltig/*.json` enthält stattdessen
`expectedError`; für diese Spuren darf kein fachlicher Teilbericht entstehen.
Die eigentlichen Ereignisse stehen jeweils im Feld `events`.

Die Regel-Gegenprobenpfade sind relativ zu diesem v1-Verzeichnis. Der Befehl
`python -m produkt.werkzeuge.referenz --check-open-corpus` prüft Referenzen,
Pflichtfallvielfalt, tatsächlich ausgeführte Spuren und Sollentscheidungen.

[API, Faktenkatalog und Swift-Eventvertrag](../../werkzeuge/referenz/README.md).
Die Quellenzuordnung und eine unabhängige Abnahme bleiben offen.
