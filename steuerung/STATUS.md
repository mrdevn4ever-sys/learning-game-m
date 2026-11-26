# Status

ZUSTAND: IN_ARBEIT
BETRIEB: IN_ARBEIT
PHASE: 0 – Betriebsfaehigkeit und Apple-Durchstich
LETZTE_AKTUALISIERUNG: 2026-11-26
FORTSETZUNGSAUFTRAG: ausdruecklicher Nutzerauftrag "Chnobel weiter" vom 2026-11-26, Wiederaufnahme ab Checkpoint 4e31d37; alle Grenzen und die vorgegebene Arbeitsreihenfolge bleiben unveraendert.

## Bestaetigte Wiederaufnahme

Die Nutzerpause vom 2026-11-24 ist durch den ausdruecklichen Fortsetzungsauftrag aufgehoben, nicht durch einen Ruecklauf oder Limitreset. Am 2026-11-26 wurden zuerst alle verlangten Startdateien vollstaendig in der vorgegebenen Reihenfolge gelesen. Die fuenf Worktrees sind sauber; Branch, HEAD und Live-Remote entsprechen exakt den erwarteten Staenden. Main bleibt `9bab69c078f2c7dbfbca3b548ce1c8ef24a9ab61`. Alte FAIL-Commitobjekte und eingefrorener ADR-0003-Hash sind erhalten. WARTEN ist nicht gesetzt, weil die Definition of Done nicht erfuellt ist.

**Anleitung: `steuerung/WIEDERAUFNAHME.md`, zusammen mit dem Fortsetzungsauftrag.** Der Chnobel-Cron `26647d618052` bleibt waehrend interaktiver Arbeit aus; live bestaetigt enabled false, state paused, next_run_at null. Keine lebenden Subagenten bei der Wiederaufnahme. Abgleich abgeschlossen: alle sechs alten Nachreview-/Ratifikationskontexte `interrupted`, alle sechs erwarteten Abschlussberichte fehlen. Kein Urteil. Keine alten Reparaturauftraege erneut starten.

Die abgewiesene AGENTS.md-Erweiterung ist weder im Git-Objekt noch im Arbeitsinhalt enthalten. SHA-256 des unveraenderten vorherigen und aktuellen Git-Blobs: `98bfd757b5d163b1ad172a7fffae2bf20080aab134aa43337cd7b6b43bb0bca6`; der Arbeitsinhalt unterscheidet sich ausschliesslich durch CRLF/LF-Zeilenenden. Geschuetzte Instruktionsdateien bleiben ohne ausdrueckliche Dialogzustimmung unangetastet.

## Aktueller Ruecklaufcheckpoint

- Eigener Wiederaufnahmecommit `d4a66d62c499d6f25c3eb1f8625972976c7c4fd2`, remote zurueckgelesen.
- Historischer Abgleich: `steuerung/gedaechtnis/pruefergebnisse/2026-11-26-wiederaufnahme/abgleich.json`. Original-FAILs/Teilbelege bleiben erhalten.
- Aktive fremde Nachreviews: `deleg_5f23880a`, Steuerung `sa-0-40bc0516`, Referenz `sa-1-1cee643e`, iPad `sa-2-01e3e3c4`. Read-only gegen die unveraenderten drei Reparatur-SHAs; nur neue Runtimebelege erlaubt. Keine Produktwriter gestartet.
- Naechster Schritt nach automatischem Ruecklauf: Berichte und echte Belege gegen die exakten Kandidaten verifizieren; erst danach drei frische Ratifikationsvoten zum eingefrorenen ADR 0003. Keine neue Implementierung bis v2-Manifest eingefroren und fremd geprueft ist.
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
