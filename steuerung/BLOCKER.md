# Blocker

Stand: 2026-11-24, nach delegierter Portal-Einrichtung. Keine privaten Schluesselwerte gelesen, erzeugt oder ausgegeben.

## Aktueller Fortschritt und Berechtigung

Der Kontoinhaber hat die angemeldeten Apple-/GitHub-Oberflaechen bereitgestellt und die weitere Einrichtung ausdruecklich delegiert. Routine-Einrichtung ist damit Agentenarbeit; rechtliche Vertragsannahmen, Zahlungen und persoenliche Authentifizierung bleiben davon getrennt. Die historische Liste unten wird nicht erneut als vollstaendig unerledigte Menschenaufgabe ausgegeben.

- Explizite Bundle-ID `ch.chnobel.app` und App-Store-Connect-Datensatz Chnobel, Apple-ID `6838908211`, iOS/iPadOS, Deutsch, SKU `CHNOBEL-IPADOS-001`, eingeschraenkter Benutzerzugriff angelegt und nach Neuladen zurueckgelesen. TestFlight: keine Builds, null Tester; keine Gruppe angelegt, niemand eingeladen.
- Mitgliedschaft/Vertraege noch nicht abschliessend dokumentiert; API-Authentisierung, Signing und Rollen-/Kandidatenisolation nicht nachgewiesen. Neue Environment-Abfrage nach App-Anlage weiterhin leer. Keine Secrets uebertragen.
- Fremde Sicherheitspruefung der technischen Rollen und drei Code-Reviews beauftragt. Drei getrennte Entwicklungsstaende lokal nachgetestet, noch nicht in main integriert. Testzahlen ersetzen keinen gemeinsamen Kandidatenbeleg.
- Portal- und Laufbelege ausserhalb Git unter `F:/ChnobelRuntime/portal/` und `F:/ChnobelRuntime/verification/`. Keine verdeckte Abnahme und kein Upload.

## Historische einmalige Startpaket-Liste (vor Portal-Einrichtung)

1. **Apple-Konto und App-Datensatz nachweisen.** In Apple Developer muss die Mitgliedschaft aktiv sein und der Kontoinhaber muss erforderliche Vertraege akzeptiert haben. In App Store Connect muss ein Chnobel-App-Datensatz fuer iPadOS mit passender Bundle-ID und Team vorhanden sein. Der aktuelle Zugang belegt diese Punkte nicht; es wird nicht behauptet, das Konto fehle.
2. **Signier-/Upload-Secrets hinterlegen.** Erwartete Namen: `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_KEY_P8_BASE64`, `APPLE_TEAM_ID`, `CHNOBEL_BUNDLE_ID`. Optional nur falls verwaltetes Signing nicht funktioniert: `DIST_CERT_P12_BASE64`, `DIST_CERT_PASSWORD`, `PROVISIONING_PROFILE_BASE64`. Ziel: GitHub Settings → Environments → `release-internal` → Environment secrets, erst im technisch isolierten Release-Kontext. Nicht als breit lesbare Repository-Secrets im oeffentlichen Produktrepo hinterlegen. Schluesselwerte nie im Chat, Code, Log oder Bericht.
3. **Getrennte technische Identitaeten bereitstellen.** Produkt, Pruefung, Release und Steuerung benoetigen wirksam getrennte Credentials/ACLs. Aktuell hat dieselbe angemeldete Adminidentitaet Zugriff auf Produkt- und Pruefrepository. Der private Bereich ist deshalb noch keine verdeckte Abnahmeumgebung. Ziel: GitHub Apps oder begrenzte Dienstidentitaeten; Produkt ohne Pruefrepo-/Signingzugriff, Steuerung mit exklusivem Merge-/Zustandsrecht, Release nur mit freigegebenem Archiv und Apple-Auftrag. Keine Personen einladen.
4. **Pruefzugriff hinterlegen.** `PRUEFUNG_REPO_TOKEN` mit minimalem Lesezugriff auf `mrdevn4ever-sys/chnobel-pruefung`, nur im isolierten `independent-check`-Kontext. Ziel: dessen geschuetztes GitHub Environment → Secrets. Kandidatenprozesse duerfen weder Token noch Sollwissen lesen. Der Pruefdienst braucht daneben einen getrennten, geprueften Weg zum Ablegen der Pruefsaetze/Freigabebelege. Die erforderliche Rechtevergabe bleibt extern blockiert.

Alle sechs obligatorischen Secret-Namen waren bei der Repository-Abfrage abwesend; auch keine Environments vorhanden. Namenpraesenz allein wird spaeter keine Funktionspruefung ersetzen. Die Liste wird einmal kommuniziert; unabhaengige Entwicklung geht weiter.

## Blockierte Gates und Behebung

- **B-APPLE / offen, Portalpruefung nicht abgeschlossen:** App-Datensatz und Bundle-ID nachgewiesen. Mitgliedschaft/Vertraege und exakter API-Lesebeleg noch offen. Sperrt P0-09/P0-10 und P7. Nur eine tatsaechlich erforderliche Kontoinhaberhandlung wird als extern blockiert klassifiziert.
- **B-SIGN / offen, Einrichtung delegiert, Release gesperrt:** API-/Signier-Secrets fehlen im vorgesehenen isolierten Kontext. Sperrt Signieren, Export und Upload. Behoben durch Namensinventur, nachgewiesene Identitaetsgrenzen, erfolgreiche API-Authentisierung und Signierprobe fuer die ausschliesslich erlaubte App-ID.
- **B-IDENT / offen, Sicherheitspruefung beauftragt, privilegierter Betrieb gesperrt:** Gemeinsamer Bootstrap-Admin hat Zugriff auf Produkt- und Pruefrepository. Privates Repo mit Zweck-README vorhanden, Actions dort deaktiviert. Positive/negative Zugriffstests, Kandidatenisolation und getrennte Befugnisse fuer Pruefung, Release und Steuerung fehlen weiterhin.
- **B-NATIVE / offen, technisch bearbeitbar:** Windows ohne Swift/Xcode. GitHub Actions aktiv; macOS-Build/Simulator noch nicht ausgefuehrt. Behoben durch erfolgreich gebundene native CI. Kein Grund, Codearbeiten zu stoppen.
- **B-GATES / offen, technisch bearbeitbar:** PR-Schutz aktiv, kein Force-Push/Loeschen, Admins einbezogen. Noch keine Pflichtchecks, da Workflows erst aufgebaut werden. Null formale GitHub-Zustimmungen vermeiden eine Selbstreview-Sackgasse mit nur einer technischen Identitaet; fremdes Kontextreview bleibt zwingend, technisch erzwungene Rollentrennung ist nicht belegt. Pflichtchecks mit erwarteter CI-App werden nach ihrer Einfuehrung ergaenzt; kein Release allein auf dieser Basis.

## Getrennte offene Nachweise

Zusaetzlicher technischer Integrationsblocker: Swift-APIs noch nicht mit v1-Referenzvertrag abgeglichen; fremde Code-Reviews und echte native Tests ausstehend. Kein Auftragsabschluss allein aus einem Ruecklauf oder einer Testsumme.

Reale Kinder, Lernwirksamkeit, Motivation, Fairness und menschlicher Sprachgebrauch bleiben gemaess Abschnitt 23 offen. Physisches iPad/Pencil nicht angebunden; kein Hardwarebeleg. Diese Punkte werden nicht als ausgefuehrte Tests dargestellt.
