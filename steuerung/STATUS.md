# Status

ZUSTAND: IN_ARBEIT
BETRIEB: IN_ARBEIT
PHASE: 0 – Betriebsfaehigkeit und Apple-Durchstich
LETZTE_AKTUALISIERUNG: 2026-11-26
FORTSETZUNGSAUFTRAG: ausdruecklicher Nutzerauftrag "Chnobel weiter" vom 2026-11-26, Wiederaufnahme ab Checkpoint 4e31d37; alle Grenzen und die vorgegebene Arbeitsreihenfolge bleiben unveraendert.

## Bestaetigte Wiederaufnahme

Die Nutzerpause vom 2026-11-24 ist durch den ausdruecklichen Fortsetzungsauftrag aufgehoben, nicht durch einen Ruecklauf oder Limitreset. Am 2026-11-26 wurden zuerst alle verlangten Startdateien vollstaendig in der vorgegebenen Reihenfolge gelesen. Die fuenf Worktrees sind sauber; Branch, HEAD und Live-Remote entsprechen exakt den erwarteten Staenden. Main bleibt `9bab69c078f2c7dbfbca3b548ce1c8ef24a9ab61`. Alte FAIL-Commitobjekte und eingefrorener ADR-0003-Hash sind erhalten. WARTEN ist nicht gesetzt, weil die Definition of Done nicht erfuellt ist.

**Anleitung: `steuerung/WIEDERAUFNAHME.md`, zusammen mit dem Fortsetzungsauftrag.** Der Chnobel-Cron `26647d618052` bleibt waehrend interaktiver Arbeit aus; live bestaetigt enabled false, state paused, next_run_at null. Keine lebenden Subagenten bei der Wiederaufnahme. Erster historischer Abgleich: alle sechs alten Nachreview-/Ratifikationskontexte `interrupted`, damals fehlten alle sechs erwarteten Abschlussberichte. Daraus kein Urteil. Die neu abgeschlossenen Nachreviews stehen unten. Keine alten Reparaturauftraege erneut starten.

Die abgewiesene AGENTS.md-Erweiterung ist weder im Git-Objekt noch im Arbeitsinhalt enthalten. SHA-256 des unveraenderten vorherigen und aktuellen Git-Blobs: `98bfd757b5d163b1ad172a7fffae2bf20080aab134aa43337cd7b6b43bb0bca6`; der Arbeitsinhalt unterscheidet sich ausschliesslich durch CRLF/LF-Zeilenenden. Geschuetzte Instruktionsdateien bleiben ohne ausdrueckliche Dialogzustimmung unangetastet.

## Aktueller Ruecklaufcheckpoint

- Eigener Wiederaufnahmecommit `d4a66d62c499d6f25c3eb1f8625972976c7c4fd2`, remote zurueckgelesen.
- Historischer Abgleich: `steuerung/gedaechtnis/pruefergebnisse/2026-11-26-wiederaufnahme/abgleich.json`. Original-FAILs/Teilbelege bleiben erhalten.
- Fremde Nachreviews `deleg_5f23880a` abgeschlossen und durch Elternkontext nachgeprueft. Berichte bytegenau mit Hashindex archiviert unter `steuerung/gedaechtnis/pruefergebnisse/2026-11-26-nachreviews/`. Steuerung PASS im lokalen Entwicklungsumfang; Referenz FAIL (RT-16), iPad statisch FAIL (RT-17). Original-FAILs bleiben erhalten, keine Gesamtfreigabe.
- Elternnachpruefung: Steuerung 42 unabhaengige Gegenproben bestanden; Referenz vier neue N20-Integritaetsfehler gegen Original und Reparatur echt wiederholt; iPad elf statische Reviewpruefungen, zehn bestanden/eine gescheitert, Swift NOT RUN. Beleg `F:/ChnobelRuntime/verification/2026-11-26-review-parent/evidence/verification.json`, SHA-256 `e557c2af8597cc5f4a09580d6d1fa605f37886e72df71f5e42f9612dbbc2f2f4`. Unterschiedliche Kandidaten/Verfahren, keine Addition.
- Ratifikation `deleg_b54b26ad` abgeschlossen und elternverifiziert: Architekt, Didaktik und Red-Team je COMPLETE/JA zum gesamten unveraenderten Hash `0f97e89acd7cb6a2ad937949db57f704596e36c617af5ac31a655ac407975472`. Drei Rollen, drei JA, keine Bedingung/Textaenderung; Mehrheit maschinell geprueft. ADR 0003 ist damit fuer prospektive Produktentscheidungen verbindlich. Verlustfreies Archiv mit Hashindex: `steuerung/gedaechtnis/entscheide/2026-11-26-adr0003-ratifikation/`. Nur Status-/Entscheidungsvermerk geaendert, normative D1-D6 wortgleich.
- Ratifikation separat committed/gepusht und remote verifiziert: `d84c597a68863929034cff50089e098120c7cb39`. Main unveraendert; kein Actionslauf fuer diesen Commit bei Ruecklese, Dokumentationsbranch ohne offenen PR.
- Manifestdefinition laeuft: `deleg_6bcb2994`, Autor `sa-0-416e4182`, nur neue Runtime-Spezifikation unter `F:/ChnobelRuntime/specification/v2-manifest-draft-01/`. Erwartet: `manifest.json`, `README.md`, konkrete Falldaten/Erwartungen, `handoff.json` mit Mengen/Dateihashes/offenen Punkten. Kein selbst erteiltes Urteil, keine Repo-/Produktwrites, kein CI-Start.
- Naechster Schritt nach automatischem Ruecklauf: Artefakte, vollstaendige Feld-/Falllisten, alte IDs und begruendete Erwartungsdifferenzen gegen ADR und echte Quellen pruefen; RT-16/17 samt positiven Kontrollen behalten. Erst dann Manifest einfrieren/haschen und einem neuen fremden Kontext zur Pruefung geben. Noch kein Freeze, keine Manifestfreigabe und keine Implementierung. Produkt-/Integrations-/Releasegates bleiben gesperrt.
- Kein CI-Run manuell ausgeloest, kein zweiter PR, main-Merge, Auftragsabschluss, Signing oder Upload. Startpaket-Neupruefung bleibt an ihrer vorgegebenen Stelle.

## Gesicherter Stand des Pausencheckpoints

- Reparatur 1 Steuerung: `e4a8f442272b75cfa0e1f7fd46c2d793b1fbd2ca`, `feat/steuerung`, Elternnachtest 83/83 Python-Tests bestanden; alte Tests bytegleich, gepusht und Remote-SHA verifiziert.
- Reparatur 1 Referenz: `107f524a0529e84fb5dad78af7a7204edb6f649e`, `feat/vertraege-referenz`, Elternnachtest 232/232 Python-Tests bestanden; alte Tests/Vertraege bytegleich, gepusht und Remote-SHA verifiziert. F04-F06/Sollrevision weiter offen.
- Reparatur 1 iPad: `c1ad063851f568eb3e376fdb7ca7802a59cb0d1b`, `feat/ipad-kern`, Elternnachtest 40/40 statische Tests bestanden; alte Tests bytegleich, gepusht und Remote-SHA verifiziert. Fuer diesen SHA kein nativer Ausfuehrungsbeleg; 77 Package-/13 SwiftData-/11 UI-Definitionen laut Worker.
- Elternbelege: `steuerung/gedaechtnis/pruefergebnisse/2026-11-24-repair1-parent/`. Drei getrennte Kandidaten, keine gemeinsame Integrationsfreigabe. Original-FAILs unveraendert. Neue fremde Nachreviews nicht abschliessend verarbeitet.
- Erstes Gremium zurueck und unter `steuerung/gedaechtnis/entscheide/2026-11-24-reparatursemantik/` archiviert. ADR 0003 ist nur Entwurf, nicht verbindlich; Ratifikationshash `0f97e89acd7cb6a2ad937949db57f704596e36c617af5ac31a655ac407975472`. Ratifikation und neues Fall-/Revisionsmanifest fehlen.
- Native Diagnose: Draft-PR #3 offen, Head `5246dbeb8e495563d0c04edd17fb24a8cc61ccf9`; Run `45494829002` am selben SHA als completed/failure zurueckgelesen. Keine laufende CI in dieser Branchabfrage, Detailruecklauf noch auszuwerten. Kein nativer PASS oder Merge daraus abgeleitet; Snapshot basiert auf den gesperrten Originalen, nicht den Reparaturen.
- Main zuletzt unveraendert `9bab69c078f2c7dbfbca3b548ce1c8ef24a9ab61`. Keine Produktintegration, Auftragsabschluesse, Signierung oder Apple-Uploads.

## Letzte erledigte Aufgaben
- Dokumentations-PR #2 nach fremdem Kontextreview und erneutem Diff-Gate gemergt. Remote-main: `9bab69c078f2c7dbfbca3b548ce1c8ef24a9ab61`. Keine Produkt- oder Releasefreigabe.
- Apple-Portal: explizite Bundle-ID `ch.chnobel.app` registriert und wieder geoeffnet. Unveroeffentlichter Chnobel-App-Datensatz `6838908211`, Plattform iOS/iPadOS, Primaersprache Deutsch, SKU `CHNOBEL-IPADOS-001`, eingeschraenkter Benutzerzugriff angelegt und nach Neuladen zurueckgelesen. TestFlight: keine Builds, null Tester. Keine Gruppen/Einladungen/Publikation.
- Ruecklaeufe auf ihren exakten sauberen Arbeitsbranches selbst nachgeprueft und remote gesichert: Steuerung `3bf45a586478a1c38ba8563bef7d0e8ad22e06e6` mit 71/71 Python-Tests; Vertraege/Referenz `b8cd111453b2c44d28a5fc21125c4f9dbc95877e` mit 165/165 Python-Tests; iPad `d71acbe65a602f091840ed5fa7e6069a157843c2` mit 14/14 statischen Tests. Keine ausgelassenen oder erwarteten Fehler in diesen Laeufen. Keine gemeinsame Kandidatenfreigabe.

## Historischer Arbeitsstand vor Reparaturruecklauf
- Drei fremde Code-Reviews eingegangen: alle FAIL fuer Entwicklungsintegration der oben genannten Quellcommits. Originalberichte bytegleich und per Digest archiviert unter `steuerung/gedaechtnis/pruefergebnisse/2026-11-24-code-reviews/`; Befunde RT-04 bis RT-15 in `docs/red-team-register.md`. Keine Integration in main und kein Auftragsabschluss.
- Orchestrator hat die zwei Restore-Fristfehler und vier zentrale Referenzgegenproben erneut auf den Originalkandidaten bestaetigt. iPad weiterhin Quellreview, keine erfundene Swift-Ausfuehrung.
- Damaliger Auftrag: Reparaturversuch 1 in drei getrennten Produktworktrees, parallel Gremium zu D1-D6. Inzwischen eingegangen, nachgetestet und oben aktualisiert; keine neuen Produktwriter laufen daraus.
- Unabhaengige Sicherheitsarchitektur eingegangen und gegen Live-Konfiguration abgeglichen; Entwurf und Grenzen in `docs/planung/identitaetsarchitektur-pruefstand.md`. Zwoelf Rollen-/Sandbox-Testpaare weiterhin NOT RUN. Owner-Adminzugriff bleibt Bootstrapzugriff, kein Isolationsbeleg.
- Privates `independent-check`-Environment ohne Secrets eingerichtet, Branch-Policy ausschliesslich `main` zurueckgelesen. Reviewer-Schutz mit HTTP 422 abgewiesen; Admin-Bypass weiterhin aktiv. Actions im Pruefrepository bleiben aus. Keine privilegierte Freigabe.
- App-Registrierung im sichtbaren Chrome vor Absenden abgebrochen: dort anderes GitHub-Konto als der Projekt-Owner angemeldet, kein bereits angemeldeter Owner im Account-Switcher. Keine App/Schluessel erzeugt.
- Dokumentations-/Steuerungsbranch `ci/entwicklungspruefung` getrennt von `ci/native-phase0` in `F:/Projects/Chnobel-Nativ`. Diagnose-Snapshot `fbb900fd77be98fe02aba73cdaf2382676d1cf5a` enthaelt exakt die drei gesperrten Original-Produktbaeume und aktuelle main-Basis; Tree-Identitaet nachgeprueft. CI-Auftrag fuer ausschliesslich unsignierte macOS-/Simulator-Diagnose mit separater Review-Sperre und Draft-PR beauftragt; noch kein nativer Ausfuehrungsbeleg. Kein main-Merge oder Release daraus erlaubt. Swift-Referenzabgleich ausstehend.
- Erster eigener Referenzlauf wegen fehlender gepinnter RFC-3339-Abhaengigkeit gescheitert; Originalfehler erhalten. Nach Installation der unveraenderten Requirements separater erfolgreicher Lauf. Kein Test/Gate geaendert.

## Naechste Aufgabe nach bestaetigter Fortsetzung, strikt geordnet
1. `steuerung/WIEDERAUFNAHME.md`, MASTERPROMPT, ADRs, Auftraege und echte lokale/Remote-SHAs lesen. Angehaltene Nachreviews/Ratifikationen und nativen Diagnose-Ruecklauf abgleichen; nichts doppelt beginnen.
2. Fehlende fremde Urteile vervollstaendigen, ADR 0003 gegebenenfalls ratifizieren/korrigieren, explizites Revisionsmanifest vor neuer Umsetzung einfrieren und fremd pruefen. Alte FAILs/v0/v1 bleiben unveraendert.
3. Native Diagnosefehler am exakten SHA auswerten; neue Kandidaten separat nativ pruefen und Swift-/Referenzabgleich erbringen. Pflichtchecks an beobachtete CI-Identitaet binden.
4. Sicherheits-/Appleblocker unabhaengig weiterbearbeiten. Steuerung und Signieren/Upload erst nach gueltigen fremden Gates. Historische Auftraege nicht manuell als erledigt markieren; Cron bei interaktiver Arbeit aus lassen.

## Blocker
Siehe `steuerung/BLOCKER.md`. Keine Signierung, kein Apple-Upload, keine verdeckte Abnahme, keine Phase-0-Abnahme. Native Definitionen und Diagnose-Ruecklauf sind kandidatgebunden wie oben getrennt. Handschrifterkennung deaktiviert. Unabhaengige Arbeit nicht ausgeschoepft; nicht BLOCKIERT_STARTPAKET. Startpaket-Neupruefung folgt an der im Fortsetzungsauftrag vorgesehenen Stelle.

## Wiederaufnahme
Massgebend sind der ausdrueckliche Fortsetzungsauftrag, die unveraenderten Projektgrenzen und `steuerung/WIEDERAUFNAHME.md`. Runtimeuebergabe: `F:/ChnobelRuntime/autonomie.json`, nach diesem separaten Statuscommit abzugleichen. Alte Batches: `deleg_87155b84` (Nachreviews), `deleg_afd52147` (Ratifikation), `deleg_51255299` (native Diagnose). Bei erneuter Nutzerpause sofort wieder sperren; Ruecklaeufe heben sie nicht auf. WARTEN erst nach vollstaendiger Definition of Done.
