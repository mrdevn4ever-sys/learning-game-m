# v0 – unveränderte historische Startverträge

Diese drei Schemas und drei Beispiele sind bytegleich zum Vertragsstand in
`db3bb5ac177bf54d3f5652cb50bf8abe52c4dd41`. Sie wurden ausschliesslich in dieses
Versionsverzeichnis verschoben. Die historischen `$id`-Werte bleiben Teil des
Snapshots; nicht zusammen mit den aktiven Root-Einstiegspunkten in denselben
Schema-Resolver registrieren. Tests vergleichen die ursprünglichen Digests.

**Nicht für neue Kandidaten benutzen.** Die dokumentierten Lücken bleiben:
`passed` mit `none`/leerer Bindung, unvollständige Payloads, unbelegte Fallbacks,
fehlender Korrekturbezug, Kind mit App-Demo und fehlende Pflichtfallvielfalt.
Die Quellenplätze «Fassung zu bestimmen» sind keine geprüften LP-Referenzen.
Die damaligen Gegenprobenpfade wurden nicht nachträglich mit v1-Ergebnissen befüllt.

Die v1-Verträge, eigenen offenen Regressionen und der Referenzprüfer behandeln
neue Eingaben. Das macht keine historische Prüfung rückwirkend erfolgreich.
