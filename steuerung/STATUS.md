# Status

ZUSTAND: IN_ARBEIT
BETRIEB: PAUSIERT_AUF_NUTZERWUNSCH
PHASE: 0 – Betriebsfaehigkeit und Apple-Durchstich
LETZTE_AKTUALISIERUNG: 2026-11-24

## Verbindliche Pause und aktuelle Uebergabe

Der Nutzer hat wegen des nahen Nutzungslimits Pause und eine gesicherte Anleitung angeordnet. Keine neuen Entwicklungs-, Delegations-, CI-, Portal-, Merge- oder Releaseaktionen bis zu einem ausdruecklichen Fortsetzungsauftrag. Spaete Ruecklaeufe und ein Limitreset heben die Pause nicht auf. WARTEN ist nicht gesetzt, weil die Definition of Done nicht erfuellt ist.

**Vollstaendige aktuelle Anleitung: `steuerung/WIEDERAUFNAHME.md`.** Der Chnobel-Cron `26647d618052` ist verifiziert pausiert, enabled false, ohne naechsten Lauf. Stop fuer alle sechs laufenden Nachreview-/Ratifikationskontexte angefordert; Teilruecklaeufe bleiben unvollstaendige Belege.

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

## Naechste Aufgabe NUR nach ausdruecklicher Fortsetzung
1. `steuerung/WIEDERAUFNAHME.md`, MASTERPROMPT, ADRs, Auftraege und echte lokale/Remote-SHAs lesen. Angehaltene Nachreviews/Ratifikationen und nativen Diagnose-Ruecklauf abgleichen; nichts doppelt beginnen.
2. Fehlende fremde Urteile vervollstaendigen, ADR 0003 gegebenenfalls ratifizieren/korrigieren, explizites Revisionsmanifest vor neuer Umsetzung einfrieren und fremd pruefen. Alte FAILs/v0/v1 bleiben unveraendert.
3. Native Diagnosefehler am exakten SHA auswerten; neue Kandidaten separat nativ pruefen und Swift-/Referenzabgleich erbringen. Pflichtchecks an beobachtete CI-Identitaet binden.
4. Sicherheits-/Appleblocker unabhaengig weiterbearbeiten. Steuerung und Signieren/Upload erst nach gueltigen fremden Gates. Historische Auftraege nicht manuell als erledigt markieren; Cron bei interaktiver Arbeit aus lassen.

## Blocker
Siehe `steuerung/BLOCKER.md`. Keine Signierung, kein Apple-Upload, keine verdeckte Abnahme, keine Phase-0-Abnahme. Native Definitionen und Diagnose-Ruecklauf sind kandidatgebunden wie oben getrennt. Handschrifterkennung deaktiviert. Unabhaengige Arbeit nicht ausgeschoepft; Pause auf Nutzerwunsch, nicht BLOCKIERT_STARTPAKET.

## Wiederaufnahme
Massgebend sind die Pausensperre oben und `steuerung/WIEDERAUFNAHME.md`. Runtimeuebergabe: `F:/ChnobelRuntime/autonomie.json`. Stop angefordert fuer `deleg_87155b84` (Nachreviews) und `deleg_afd52147` (Ratifikation); native Diagnose `deleg_51255299` noch detailliert zu rekonstruieren. Ruecklaeufe niemals als neue Fortsetzungserlaubnis behandeln. WARTEN erst nach vollstaendiger Definition of Done.
