# ADR 0001: Grundentscheide

- Status: verbindlich
- Datum: 2026-11-22

## Entscheide
1. **Autonomie**: Ausschliesslich KI-Agenten entwickeln, prüfen und veröffentlichen intern. Nach dem einmaligen Startpaket ist kein Mensch beteiligt.
2. **Endzustand**: ein intern testbereiter TestFlight-Build («Internal Only»), danach Zustand `WARTEN`.
3. **Plattform der Abnahme**: iPadOS 18 oder neuer, SwiftUI, Swift 6, SwiftData. iPhone und Mac sind spätere, eigene Abnahmewellen.
4. **Umfang**: Lehrplan 21, Profile Luzern und Bern (deutschsprachig), 1.–6. Klasse, alle Fachbereiche.
5. **Ehrliche Aussagen**: Jede Lernstandsaussage braucht eine Beweisregel mit dreiwertiger Faktenlogik und drei Pflichtfällen. Enthaltung ist eine Produktfunktion.
6. **Beobachtungsprotokoll**: Aussagen werden aus einem versionierten Ereignisprotokoll abgeleitet und sind nach Updates neu berechenbar.
7. **Belegstatus mit zwei Achsen**: Prüfverfahren und Geltungsbereich. Belege gelten nur für den gebundenen Kandidaten.
8. **Trennung von Produkt und Abnahme**: Verdecktes Prüfmaterial liegt in einem separaten, nicht öffentlichen Prüfbereich.
9. **Offline und Datenschutz**: keine Server, keine Analytics, keine Drittanbieter-SDKs. Daten bleiben auf dem Gerät.
10. **Keine fremden Inhalte**: eigene oder nachweislich gemeinfreie beziehungsweise passend lizenzierte Inhalte, erfasst im Rechteverzeichnis.

## Begründung
Siehe `MASTERPROMPT.md` und die Planungshistorie in `docs/planung/`.
