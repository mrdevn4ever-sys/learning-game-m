# Status

ZUSTAND: IN_ARBEIT
PHASE: 0 – Betriebsfaehigkeit und Apple-Durchstich
LETZTE_AKTUALISIERUNG: 2026-11-24

## Letzte erledigte Aufgaben
- Dokumentations-PR #2 nach fremdem Kontextreview und erneutem Diff-Gate gemergt. Remote-main: `9bab69c078f2c7dbfbca3b548ce1c8ef24a9ab61`. Keine Produkt- oder Releasefreigabe.
- Apple-Portal: explizite Bundle-ID `ch.chnobel.app` registriert und wieder geoeffnet. Unveroeffentlichter Chnobel-App-Datensatz `6838908211`, Plattform iOS/iPadOS, Primaersprache Deutsch, SKU `CHNOBEL-IPADOS-001`, eingeschraenkter Benutzerzugriff angelegt und nach Neuladen zurueckgelesen. TestFlight: keine Builds, null Tester. Keine Gruppen/Einladungen/Publikation.
- Ruecklaeufe auf ihren exakten sauberen Arbeitsbranches selbst nachgeprueft und remote gesichert: Steuerung `3bf45a586478a1c38ba8563bef7d0e8ad22e06e6` mit 71/71 Python-Tests; Vertraege/Referenz `b8cd111453b2c44d28a5fc21125c4f9dbc95877e` mit 165/165 Python-Tests; iPad `d71acbe65a602f091840ed5fa7e6069a157843c2` mit 14/14 statischen Tests. Keine ausgelassenen oder erwarteten Fehler in diesen Laeufen. Keine gemeinsame Kandidatenfreigabe.

## Aktuelle Arbeit
- Drei fremde Code-Reviews eingegangen: alle FAIL fuer Entwicklungsintegration der oben genannten Quellcommits. Originalberichte bytegleich und per Digest archiviert unter `steuerung/gedaechtnis/pruefergebnisse/2026-11-24-code-reviews/`; Befunde RT-04 bis RT-15 in `docs/red-team-register.md`. Keine Integration in main und kein Auftragsabschluss.
- Orchestrator hat die zwei Restore-Fristfehler und vier zentrale Referenzgegenproben erneut auf den Originalkandidaten bestaetigt. iPad weiterhin Quellreview, keine erfundene Swift-Ausfuehrung.
- Reparaturversuch 1 laeuft in den drei getrennten Produktworktrees. Architekt, Fachkritik und Red-Team beurteilen parallel D1-D6 zu Akteur/Zeit, Unbekannt, Hilfewirkung und zukuenftiger Vertragsrevision; kein Gremiumsentscheid vorweggenommen.
- Unabhaengige Sicherheitsarchitektur eingegangen und gegen Live-Konfiguration abgeglichen; Entwurf und Grenzen in `docs/planung/identitaetsarchitektur-pruefstand.md`. Zwoelf Rollen-/Sandbox-Testpaare weiterhin NOT RUN. Owner-Adminzugriff bleibt Bootstrapzugriff, kein Isolationsbeleg.
- Privates `independent-check`-Environment ohne Secrets eingerichtet, Branch-Policy ausschliesslich `main` zurueckgelesen. Reviewer-Schutz mit HTTP 422 abgewiesen; Admin-Bypass weiterhin aktiv. Actions im Pruefrepository bleiben aus. Keine privilegierte Freigabe.
- App-Registrierung im sichtbaren Chrome vor Absenden abgebrochen: dort anderes GitHub-Konto als der Projekt-Owner angemeldet, kein bereits angemeldeter Owner im Account-Switcher. Keine App/Schluessel erzeugt.
- Orchestrator-Branch `ci/entwicklungspruefung`: oeffentliche Entwicklungs-CI vorbereitet, native Ausfuehrung NOT RUN. Swift-Referenzabgleich ausstehend.
- Erster eigener Referenzlauf wegen fehlender gepinnter RFC-3339-Abhaengigkeit gescheitert; Originalfehler erhalten. Nach Installation der unveraenderten Requirements separater erfolgreicher Lauf. Kein Test/Gate geaendert.

## Naechste Aufgabe
1. Sicherheitsentwurf durch Gremium/ADR und echte Rollen-/Sandboxproben absichern; App-Registrierung erst im korrekten Owner-Kontext. Apple-Mitgliedschaft/Vertraege abschliessend lesen. Secrets erst nach nachgewiesener Isolation uebertragen.
2. Reparaturruecklaeufe und Gremiumsvoten behandeln; neue exakte Kandidaten nachtesten und fremd reviewen. Zusaetzlich separate, nicht mergefaehige Snapshot-Integration fuer echte macOS-/Simulator-Diagnose vorbereiten. Native Entwicklungslaeufe sind keine Freigabe der bekannten FAIL-Kandidaten. Pflichtchecks anschliessend an beobachtete CI-Identitaet binden.
3. Steuerung erst nach Review in Betrieb nehmen; historische Startauftraege nicht nachtraeglich als erledigt markieren. Signieren/Upload nur nach gueltigen Gates.

## Blocker
Siehe `steuerung/BLOCKER.md`. Keine Signierung, kein Apple-Upload, keine verdeckte Abnahme, keine Phase-0-Abnahme. 43 Package-, vier native SwiftData- und fuenf UI-Tests laut Ruecklauf vorbereitet, nicht ausgefuehrt. Handschrifterkennung deaktiviert. Unabhaengige Arbeit nicht ausgeschoepft; deshalb nicht BLOCKIERT_STARTPAKET.

## Wiederaufnahme
MASTERPROMPT, ADRs, Auftragsdateien und exakte Remote-SHAs lesen. Detailbelege ausserhalb Git unter `F:/ChnobelRuntime/portal/` und `F:/ChnobelRuntime/verification/`. Fortsetzungsjob `26647d618052` bleibt waehrend interaktiver Einrichtung und fremder Reviews pausiert; keine parallelen Schreiber. WARTEN erst nach vollstaendiger Definition of Done.
