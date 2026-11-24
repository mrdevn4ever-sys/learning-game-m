# Blocker

Der Agent prüft das Startpaket bei jedem Start (Masterprompt, Abschnitt 3) und aktualisiert diese Liste.

| Baustein | Status | Blockierte Aufgaben | Behoben, wenn |
|---|---|---|---|
| Apple-Developer-Mitgliedschaft und App-Datensatz | ungeprüft | P0-09, P0-10 | API-Abfrage findet die App mit der erwarteten Bundle-ID |
| App-Store-Connect-API-Schlüssel und Signiermaterial | ungeprüft | P0-09, P0-10 | Secrets vorhanden, Test-Signierung erfolgreich |
| Privater Prüfbereich | ungeprüft | P0-06 (Teil: verdeckte Sätze) | Prüf-Identität kann lesen und schreiben, Produkt-Identität nicht |
| macOS-Build-Umgebung | ungeprüft | P0-07, P0-08, P0-09, P0-10 | CI-Job baut ein leeres Xcode-Projekt |
