# Öffentliche Verträge

| Pfad | Status und Zweck |
|---|---|
| `v0/` | unveränderte historische Startverträge und Beispiele von Basis `db3bb5ac177bf54d3f5652cb50bf8abe52c4dd41`; bekannte Lücken bleiben dokumentiert |
| `v1/ereignis.schema.json` | geschlossene, typgebundene Ereignisse, UUIDs, Akteursregeln |
| `v1/beweisregel.schema.json` | dreiwertige Regeln mit allen drei Pflichtfällen und offenem Quellenstatus |
| `v1/belegstatus.schema.json` | zweiachsiger Status mit Ausführungszahlen und Digest-Bindung |
| `v1/regeln/` | fünf enge Regeln für den offenen Leitfall 8 + 7 |
| `v1/spuren/` | explizite, selbst erstellte offene Spuren mit Sollentscheidung für jede Aussage |
| `v1/ungueltig/` | absichtlich unzulässige Spuren mit erwarteter Fehlerkategorie |
| `*.schema.json` im Vertragsroot | lokale Einstiegspunkte auf die kanonischen v1-Schemas, keine zusätzliche Vertragsrevision |

Aktive `schemaVersion` und Faktenkatalogversion: **1.0.0**. Keine automatische
Migration alter Ereignisse; ein v0-Datensatz wird nicht durch Umbenennen seiner
Version gültig. Die historischen Regeln `sum15.result` und `sum15.ten` erhalten
in v1 die Regelrevision 2. Neue Regeln beginnen mit Revision 1.

Schemaakzeptanz ersetzt keine semantische Integrität. Referenzen, Dedupe,
wirksame Plättchenherkunft, zeitliche Hilfe, Undo, Korrekturbezug und
Zählerinvarianten prüft der ausführbare
[Referenzprüfer](../werkzeuge/referenz/README.md). Dort stehen API, Faktenkatalog,
Eventvertrag und der verbindliche lokale Testbefehl für den Swift-Abgleich.

Alle Beispiele sind **offene synthetische Entwicklungsregressionen**, kein
verdeckter Prüfsatz und keine unabhängige Freigabe. LP-Zuordnungen für Luzern
und Bern bleiben `offen`; es wird keine kantonale Quelle als geprüft ausgegeben.
Historische Red-Team-Befunde werden nicht rückwirkend geschlossen.
