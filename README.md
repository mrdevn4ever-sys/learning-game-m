# Chnobel

Chnobel ist eine iPad-Lern-App für die 1. bis 6. Primarklasse in der Deutschschweiz und folgt dem Lehrplan 21. Sie funktioniert wie ein digitales Arbeitsheft: Kinder zeigen ihren Denkweg mit Handschrift, Material oder Ziffernblock, und die App gibt ehrliche Rückmeldungen. Sie sagt nur, was sie tatsächlich beobachtet hat.

KI-Agenten entwickeln dieses Repository vollständig autonom, bis ein intern testbereiter TestFlight-Build vorliegt. Danach warten sie auf einen neuen Auftrag.

## Für den Agenten

1. Lies **[`MASTERPROMPT.md`](MASTERPROMPT.md)**. Er ist der vollständige, verbindliche Auftrag.
2. Lies [`steuerung/STATUS.md`](steuerung/STATUS.md). Dort steht, wo die Arbeit steht.
3. Folge der Startsequenz in Abschnitt 2 des Masterprompts.

## Für den Menschen: das einmalige Startpaket

Bevor der Agent startet, müssen diese vier Bausteine bereitstehen. Alles andere erledigen die Agenten. Details stehen in Abschnitt 3 des Masterprompts.

- [ ] **Apple-Developer-Mitgliedschaft**: aktiv, Verträge akzeptiert, App-Datensatz mit Bundle-ID in App Store Connect angelegt
- [ ] **App-Store-Connect-API-Schlüssel** (.p8, Key-ID, Issuer-ID) und Signiermaterial als CI-Secrets
- [ ] **Separater privater Prüfbereich**, z.B. ein privates Repository `chnobel-pruefung`, für verdeckte Prüfaufgaben, auf den nur die Prüf-Identität Zugriff hat
- [ ] **macOS-Build-Umgebung** mit aktuellem Xcode (GitHub-Actions-macOS-Runner oder Xcode Cloud)

Fehlt etwas, trägt der Agent es in [`steuerung/BLOCKER.md`](steuerung/BLOCKER.md) ein und arbeitet an allem weiter, was unabhängig davon möglich ist.

## Agent starten

Öffne in Claude Code (oder einem vergleichbaren Agenten) dieses Repository und gib ein:

> Lies MASTERPROMPT.md und führe den Auftrag aus.

Ist die App fertig und intern in TestFlight testbereit, steht in `steuerung/STATUS.md` `ZUSTAND: WARTEN`, und die Details stehen in `steuerung/ABSCHLUSS.md`.

## Struktur

| Pfad | Inhalt |
|---|---|
| `MASTERPROMPT.md` | Auftrag, Regeln, Spezifikation, Roadmap, Definition of Done |
| `produkt/` | App, Swift-Packages, Inhalte, Verträge (JSON-Schemas), Werkzeuge |
| `pruefung/` | öffentliche Abnahmekriterien und Gegenprobenkatalog. Verdecktes Material liegt getrennt. |
| `steuerung/` | Status, Blocker, Aufträge, Projektgedächtnis, Release-Quittungen |
| `docs/` | Entscheidungen (ADR), Planungshistorie, Datenschutz, Rechteverzeichnis |
