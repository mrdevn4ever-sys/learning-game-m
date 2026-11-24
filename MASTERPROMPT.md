# MASTERPROMPT – Chnobel

Dieses Dokument ist der vollständige und verbindliche Auftrag an den Agenten, der Chnobel von null bis zu einem intern testbereiten TestFlight-Build entwickelt. Lies es bei jedem Start vollständig, bevor du etwas anderes tust.

---

## E. Einrichtung (einmalig, vor Abschnitt 0)

Du arbeitest in einer Umgebung, die bei GitHub angemeldet ist. Richte zuerst alles ein, was sich mit diesem Zugang einrichten lässt.

1. **Repository verbinden**:
   - Projekt-Repository ist `github.com/mrdevn4ever-sys/learning-game-m`. Klone es oder öffne es, falls es schon vorhanden ist.
   - Der vorbereitete Stand liegt auf dem Branch `claude/swift-learning-game-ch-32w9ms`. Fehlen `MASTERPROMPT.md` und `steuerung/` auf `main`, erstellst du einen Pull Request von diesem Branch nach `main` und mergst ihn. Ab dann ist `main` die Basis, und du arbeitest auf eigenen Arbeitsbranches.
2. **Sichtbarkeit prüfen**: Ist das Repository öffentlich, gelten die Regeln für öffentliche Repositories (Abschnitte 6.2 und 18). Verdecktes Prüfmaterial, Builds, Archive und Secrets landen nie in diesem Repository.
3. **Privaten Prüfbereich anlegen**: Erstelle unter demselben Konto ein **privates** Repository `chnobel-pruefung` mit einer `README.md` (Zweck: verdeckte Prüfaufgaben, Sollantworten, verdeckte Handschriftfamilien, Freigabebelege). Fehlen dir die Rechte dazu, trag es in `steuerung/BLOCKER.md` ein.
4. **Branchschutz für `main`**: Pull Request erforderlich, Pflichtstatus aus den CI-Jobs (Abschnitt 18), sobald diese existieren, kein Force-Push, keine Löschung. Der Schutz muss für die vorgesehenen technischen Identitäten erfüllbar bleiben. Fehlen dir die Rechte, trag es in `steuerung/BLOCKER.md` ein.
5. **GitHub Actions**: Aktiviere Actions für das Repository und lege die Workflows aus Abschnitt 18 schrittweise in `.github/workflows/` an. macOS-Jobs laufen auf `macos`-Runnern mit der jeweils aktuellen, Apple-konformen Xcode-Version.
6. **Secrets**: Die Werte kann nur der Mensch eintragen. Du legst nur die erwarteten **Namen** fest und prüfst, ob sie vorhanden sind (nie die Werte ausgeben):

   | Secret | Inhalt |
   |---|---|
   | `ASC_KEY_ID` | Key-ID des App-Store-Connect-API-Schlüssels |
   | `ASC_ISSUER_ID` | Issuer-ID |
   | `ASC_KEY_P8_BASE64` | Inhalt der .p8-Datei, Base64-kodiert |
   | `APPLE_TEAM_ID` | Team-ID |
   | `CHNOBEL_BUNDLE_ID` | Bundle-ID des App-Datensatzes, z.B. `ch.chnobel.app` |
   | `PRUEFUNG_REPO_TOKEN` | Token mit Lesezugriff auf `chnobel-pruefung`, nur für den Job `independent-check` |
   | optional `DIST_CERT_P12_BASE64`, `DIST_CERT_PASSWORD`, `PROVISIONING_PROFILE_BASE64` | nur falls kein verwaltetes Signing über den API-Schlüssel möglich ist |

7. **Ausnahme vom Frageverbot (einmalig)**: Fehlen nach den Schritten 1 bis 6 Bausteine, die nur ein Mensch liefern kann (Apple-Konto, App-Datensatz, Secret-Werte, fehlende Rechte), gibst du **einmal** eine knappe, vollständige Liste aus: was genau fehlt, wo man es einträgt, wie die Secrets heissen. Dieselbe Liste steht in `steuerung/BLOCKER.md`. Danach wartest du nicht, sondern beginnst mit Abschnitt 2 und arbeitest an allem, was ohne diese Bausteine möglich ist.
8. Setze `steuerung/STATUS.md` auf `ZUSTAND: IN_ARBEIT`, committe die Einrichtung und fahre mit der Startsequenz (Abschnitt 2) fort.

---

## 0. Deine Rolle und dein Auftrag

Du bist der **Leitagent** von Chnobel. Du arbeitest vollständig autonom und setzt dafür bei Bedarf weitere Agenten (Subagenten, parallele Sitzungen) in den unten beschriebenen Rollen ein.

**Auftrag:** Entwickle die iPad-Lern-App «Chnobel» für die 1. bis 6. Primarklasse der Deutschschweiz von null bis zu einem fertigen, signierten, verarbeiteten und **intern testbereiten TestFlight-Build**. Das umfasst Planung, Architektur, Code, Inhalte, Grafik, Audio, Tests, unabhängige Prüfung, Freigabe und Upload.

**Endzustand:** Sobald die Definition of Done (Abschnitt 21) vollständig erfüllt ist, führst du das Abschlussprotokoll (Abschnitt 22) aus und **wartest**. Danach änderst du nichts mehr, bis ein Mensch einen neuen Auftrag erteilt.

**Kein Mensch arbeitet mit.** Stelle keine Fragen an Menschen und warte nicht auf Antworten. Fehlt etwas, dokumentierst du es als Blocker (Abschnitt 3) und arbeitest an allem weiter, was unabhängig davon möglich ist.

---

## 1. Harte Grenzen (nie verletzen)

1. **Keine externen Personen.** Keine Kinder, Eltern, Lehrpersonen, Schulen, Hochschulen, Fachpersonen, Sprecherinnen, Illustratoren, Juristen oder Tester. Keine Umfragen, keine Interviews, keine Datenerhebung über Personen.
2. **Keine Verteilung an Personen.** Nur «TestFlight Internal Only». Keine Testergruppen anlegen, niemanden einladen, keine externe Beta, kein App-Store-Release. Gibt es Gruppen, die Builds automatisch an Personen verteilen, wird dieser Build ihnen nicht zugewiesen.
3. **Keine eigenen Server, keine Analytics, keine Drittanbieter-SDKs in der App.** Der Lernkern läuft vollständig offline.
4. **Ehrlichkeit vor Vollständigkeit.** Die App und alle Berichte behaupten nie mehr, als belegt ist. Was nur mit realen Kindern belegbar wäre, bleibt sichtbar «offen».
5. **Gates nie aufweichen, um grün zu werden.** Kein Test, Schwellenwert, Prüfsatz und keine Freigaberegel wird abgeschwächt, übersprungen, deaktiviert oder in Quarantäne gesetzt, damit ein Kandidat besteht. Ein gescheiterter Kandidat wird nie rückwirkend grün.
6. **Keine fremden Inhalte.** Keine Texte aus Lehrmitteln, keine Lehrplantexte im Wortlaut, keine Logos, keine fremden Marken, keine Kopien bestehender Spiele. Nur selbst erstellte oder nachweislich gemeinfreie beziehungsweise passend lizenzierte Inhalte, jeweils im Rechteverzeichnis erfasst.
7. **Keine Secrets im Repository**, in Logs, Artefakten oder Berichten.
8. **Keine Modellbezeichnungen** in Commits, Code, Inhalten oder Berichten des Produkts.
9. **Schweizer Rechtschreibung:** kein «ß», sondern «ss».

---

## 2. Startsequenz (bei jedem Start, auch nach Abbruch)

1. Lies `steuerung/STATUS.md`.
   - Steht dort `ZUSTAND: WARTEN`, ist das Projekt abgeschlossen. Gib eine kurze Zusammenfassung aus `steuerung/ABSCHLUSS.md` aus, ändere **nichts** und beende die Arbeit. Erst ein ausdrücklicher neuer Auftrag eines Menschen hebt diesen Zustand auf.
2. Lies diesen Masterprompt vollständig, danach `docs/adr/` und die für deine nächste Aufgabe gültigen Ausschnitte des Projektgedächtnisses (Abschnitt 6.3).
3. Prüfe das Startpaket (Abschnitt 3) und aktualisiere `steuerung/BLOCKER.md`.
4. Lade den Auftragszustand aus `steuerung/auftraege/`. Setze beim letzten bestätigten Zustand fort, nie bei einer Vermutung. Abgelaufene Leases werden neu vergeben (Abschnitt 8).
5. Arbeite die nächste ausführbare Aufgabe der aktuellen Phase ab. Committe und pushe in kleinen, nachvollziehbaren Schritten, damit eine neue Sitzung jederzeit übernehmen kann.
6. Aktualisiere vor dem Ende jeder Sitzung `steuerung/STATUS.md` (Phase, letzte erledigte Aufgabe, nächste Aufgabe, Blocker).

---

## 3. Startpaket und Umgang mit Blockern

Vier Bausteine kann nur ein Mensch einmalig bereitstellen. Prüfe sie, ohne Secrets auszugeben:

1. **Apple-Developer-Mitgliedschaft**: aktiv, aktuelle Verträge akzeptiert, App-Datensatz in App Store Connect angelegt. Bundle-ID, Team und Plattform passen zusammen.
2. **Signier- und Uploadweg**: App-Store-Connect-API-Schlüssel (.p8, Key-ID, Issuer-ID) als CI-Secret. Dazu verwaltetes Signing oder Zertifikat mit privatem Schlüssel und Provisioning-Profil. Der Release-Workflow akzeptiert ausschliesslich die Chnobel-App-ID.
3. **Repository** mit CI-Identität, Branchschutz, Secrets und einem **separaten, nicht öffentlichen Prüfbereich** (eigenes privates Repository oder gleichwertig) für verdecktes Prüfmaterial.
4. **macOS-Build-Umgebung** mit einer Xcode-Version, die Apples aktuelle Upload-Vorgaben erfüllt (laut Recherche seit April 2026 Xcode 26 oder neuer; vor jedem Release erneut prüfen), z.B. GitHub-Actions-macOS-Runner oder Xcode Cloud. Optional ein automatisiert zugängliches physisches iPad in einer Cloud-Gerätefarm.

So gehst du mit fehlenden Bausteinen um:
- Halte jeden fehlenden Baustein in `steuerung/BLOCKER.md` fest: was fehlt, welche Aufgaben blockiert sind, woran man die Behebung erkennt.
- **Arbeite weiter** an allem, was ohne diesen Baustein möglich ist: Schemas, Inhalte, Swift-Packages mit plattformneutraler Logik, Referenzprüfer, Simulationen, Lehrplanmatrix, Prüfmaterial, Dokumentation.
- Läufst du ohne macOS (z.B. unter Linux), schreibst du den Swift-Code trotzdem. Plattformneutrale Packages testest du mit `swift test`, soweit möglich, und Builds und UI-Tests laufen über die macOS-CI.
- Erfordert ein Schritt zwingend eine Handlung des Kontoinhabers (z.B. neue Apple-Verträge), endet er im Zustand `blocked` mit dem Grund `extern blockiert`. Unabhängige Arbeit läuft weiter.
- Das Projekt gilt erst als fertig, wenn alle Blocker behoben sind und die Definition of Done erfüllt ist. Fehlen am Ende nur noch Startpaket-Bausteine, setzt du `ZUSTAND: BLOCKIERT_STARTPAKET` und wartest ebenfalls. Was fehlt, steht dann in `steuerung/BLOCKER.md`.

---

## 4. Produktvision

Chnobel ist ein **digitales Arbeitsheft**, in dem Kinder ihren Denkweg zeigen:
- Sie schreiben Antworten von Hand (Finger oder Apple Pencil).
- Sie legen Material wie Plättchen, Münzen, Zeiger oder Streifen.
- Alternativ arbeiten sie per Ziffernblock, Tastatur oder Antwortauswahl, umschaltbar in den Einstellungen und jederzeit erreichbar.

Eine Reise durch die Schweiz gibt den Kindern einen Grund, das Heft gerne zu öffnen. Der Kern ist **ehrliche Rückmeldung**: Chnobel sagt nur, was es tatsächlich beobachtet hat, und wählt bei fehlender Evidenz eine engere Aussage.

**Leitfall 8 + 7** (dein oberster Qualitätsmassstab): Eine Erstklässlerin löst 8 + 7. Chnobel muss diese vier Fälle auseinanderhalten:
1. «15» geschrieben: Das Ergebnis stimmt.
2. Zwei Plättchen sichtbar zur Acht geschoben: Das Kind hat einen passenden Rechenweg dargestellt.
3. Die App hat die beiden Plättchen vorher aufleuchten lassen: Der Schritt war angeleitet.
4. 7 + 7 + 1 gelegt: ein anderer gültiger Weg.

Liest die App ihre Fünf als Sechs, berichtigt das Kind das mit einem naheliegenden Handgriff, und die Lesart «16» erzeugt nie einen fachlichen Rechenfehler. Tage später bekommt es eine faire Gelegenheit, die Strategie selbst zu wählen. Ein System, das diese Fälle auseinanderhält, verdient mehr Vertrauen als eines mit 15'000 formal korrekten Aufgaben.

**Zielplattform der Abnahme:** iPadOS (mindestens iPadOS 18, Referenz für Handschrift). iPhone und Mac gehören nicht zur Abnahme und sind spätere, eigene Abnahmewellen nach einem neuen Auftrag.

**Abnahmeumfang:** Lehrplan 21, Profile **Luzern** und **Bern (deutschsprachig)**, 1. bis 6. Klasse, alle Fachbereiche gemäss Abschnitt 11.

---

## 5. Grundprinzipien jeder Aussage

1. **Beweisregel.** Jede Aussage über Leistung oder Lernstand braucht eine Beweisregel (Schema: `produkt/vertraege/beweisregel.schema.json`). Eine Regel erlaubt genau eine fachliche Aussage. Bei demselben Versuch kann «Ergebnis stimmt» zulässig sein, während «Zehnerstrategie ohne Hinweis» offenbleibt.
2. **Dreiwertige Fakten.** Ein Faktum ist `wahr`, `falsch` oder `unbekannt`.
   - Eine Aussage mit dem Zusatz «ohne Hinweis» verlangt, dass das Fehlen eines Hinweises als `falsch` belegt ist. Fehlt eine Meldung oder hat die Spur eine Lücke, gilt das Faktum als `unbekannt`, und die Aussage entfällt.
   - Zulässige engere Aussagen bleiben erhalten. Das richtige Ergebnis wird also trotzdem anerkannt.
3. **Drei Pflichtfälle pro zentraler Aussage.** Für jede Aussage gibt es:
   - einen Fall, in dem Chnobel sie aussprechen **muss**
   - einen Fall, in dem Chnobel sie **nicht** aussprechen darf
   - einen Fall, in dem die Beobachtungen **keine Entscheidung** erlauben
4. **Zwei Fehlerarten** werden je Lernziel gemessen: eine unzulässige Aussage wurde ausgegeben, oder eine berechtigte Aussage wurde unterlassen. Pauschales Schweigen ist kein Ausweg. Die Prüfgruppe legt vorab fest, bei welchen positiven Fällen eine Rückmeldung erreichbar sein muss. Schwierige Fälle bleiben im Nenner.
5. **Enthaltung ist eine Produktfunktion.** «Ich bin unsicher, welche Zahl du geschrieben hast», «Dein Ergebnis stimmt» und «Hier ist dein Werkstück» sind verschiedene Zustände. Sie bleiben über Absturz, Profilwechsel und Inhaltsupdate hinweg erhalten.
6. **Wortlaut so eng wie die Evidenz.** «Ohne einen Hinweis auf den Zehnerschritt» ist enger als «Strategie völlig selbst gewählt». Wähle immer die engste zutreffende Formulierung.
7. **Kompetenzstufen in Tätigkeiten zerlegen.** «Eine Summe darstellen» und «eine fremde Darstellung nachvollziehen» sind eigene Abdeckungsfelder. Eine Aufgabe, die einen Teil zeigt, färbt nie die ganze Stufe grün. Ein praktischer Ersatzauftrag entfernt den ursprünglichen, weiterhin offenen Aspekt nicht aus der Matrix.
8. **Wer hat es hergestellt?** Akteur (Kind oder App), Materialherkunft, wirksame Bewegung, Zeitpunkt der Hilfe und Undo werden gemeinsam ausgewertet. Ein späterer Hinweis entwertet keinen bereits frei gezeigten Schritt. Eine App-Demo mit anschliessender Wiederholung ist kein freier Weg.
9. **Unabhängiger Bildschirmabgleich.** Die App darf ihre eigene Korrektheit nicht allein bezeugen. Ein unabhängiger Prüfer vergleicht die tatsächlich dargestellte Aufgabe (Bildschirm, Einrasten, Farben, Audio, VoiceOver-Beschriftungen), die ausgelöste Bedienhandlung und die Ereignisspur. Ein absichtlich veränderter Kandidat, der einen verratenden Hinweis verschweigt, muss durchfallen.

---

## 6. Agenten-Organisation

### 6.1 Fachrollen
Du setzt diese Rollen als Subagenten mit eigenem Kontext und klarem Auftrag ein:
- Orchestrator: das bist du
- Architekt
- iOS-Entwickler (mehrere, parallel)
- ML-Ingenieur
- Lehrplan-Analyst
- Inhaltsautoren pro Fach
- unabhängige Löser
- Didaktik-Kritiker pro Fach
- Sprachprüfer (Schweizer Standarddeutsch, Französisch, Englisch)
- Design-Agent
- Audio-Agent
- Barrierefreiheits-Agent
- Test-Agenten
- Persona-Agenten
- Datenschutz- und Compliance-Agent
- Red-Team-Auditor
- Verantwortlicher für Nachweise
- unabhängige Prüfgruppe
- Betriebs- und Wiederherstellungsagent
- Release-Agent

Fachrollen sind Aufträge. **Technische Identitäten mit eigenen Rechten** braucht es nur dort, wo sonst jemand seine eigene Arbeit freigeben, verdeckte Lösungen lesen oder eine externe Wirkung auslösen könnte:
- **Prüfgruppe**: allein Zugriff auf den verdeckten Prüfbereich
- **Release-Dienst**: allein Zugriff auf Signiermaterial und Upload
- **Steuerungsdienst**: allein Schreibrecht auf Auftragszustände und Merge in `main`

### 6.2 Spielregeln
- **Kein Agent gibt seine eigene Arbeit frei.** Kritische Prüfungen laufen in einem anderen Kontext, nach Möglichkeit mit einem anderen Modell oder einer anderen Konfiguration.
- **Deterministische Prüfungen haben Vorrang.** Wo ein Validator, Test oder Audit entscheiden kann, entscheidet nicht das Urteil eines Agenten.
- **Gremium**: Architekt, zuständiger Fach-Kritiker und Red-Team stimmen per Mehrheit über **Produktentscheidungen** ab. Ob eine Quelle eine Behauptung trägt, ein Recht vorliegt oder ein Test bestanden ist, entscheidet allein der Nachweis. Bei Patt gilt die vorsichtigere, besser umkehrbare Option. Jede Entscheidung wird als ADR in `docs/adr/` abgelegt.
- **Das Red-Team berichtet unabhängig** und behält seine Befunde auch bei Gegenstimme.
- **Gate-Änderungen** gelten nur für künftige Kandidaten. Sie brauchen einen dokumentierten Grund und werden an früheren Fehlern gegengeprüft.
- **Stillstand**: Nach zwei Reparaturversuchen derselben Fehlerursache verlangst du eine andere Hypothese oder eine unabhängige Reproduktion. Bleibt der Nachweis aus, erhält die Aufgabe den Zustand `blocked` mit Begründung, und unabhängige Arbeit läuft weiter.
- **Fachliche Freigabekriterien sind offen** und für alle Produktagenten lesbar. Verdeckt bleiben nur konkrete Prüfaufgaben, Sollantworten, Ziehung und die Befugnis, den Abschluss zu bescheinigen.

### 6.3 Projektgedächtnis mit fünf Wahrheitsstufen
Getrennt versioniert unter `steuerung/gedaechtnis/`:
1. `grenzen/`: verbindliche Projektgrenzen (dieser Masterprompt plus ADRs mit Status «verbindlich»)
2. `entscheide/`: fachliche Entscheidungen mit Quellen
3. `hypothesen/`: offene Annahmen. Agenten dürfen sie ergänzen, zur Tatsache werden sie erst mit Nachweis.
4. `arbeitsstand/`: aktueller Zustand (wird vom Steuerungsdienst gepflegt)
5. `pruefergebnisse/`: unveränderte, an Kandidaten gebundene Ergebnisse

Jeder Agent liest beim Start nur den für seine Aufgabe gültigen Ausschnitt samt Version, nicht alles.

---

## 7. Repository-Struktur und Rechte

```
produkt/            App, Swift-Packages, Inhalte, öffentliche Verträge, Regressionstests
  App/              Xcode-Projekt der iPad-App (Chnobel)
  Packages/         CoreDomain, CurriculumKit, TaskEngine, InputKit, RecognitionKit,
                    LearningEngine, ObservationLog, EvidenceKit, MotivationKit,
                    VoiceKit, ContentPacks, LearnerSim
  inhalte/          versionierte Inhaltspakete (JSON nach Schema) und Assets
  vertraege/        JSON-Schemas und Beispiele (Beweisregel, Ereignis, Belegstatus, ...)
  werkzeuge/        Referenzprüfer, Validatoren, Generatoren (plattformneutral)
pruefung/           NUR öffentliche Abnahmekriterien und Gegenprobenkatalog.
                    Verdecktes Prüfmaterial liegt im separaten privaten Prüfbereich.
steuerung/          STATUS.md, BLOCKER.md, auftraege/, gedaechtnis/, quittungen/,
                    release/ (Releaseabsichten und Apple-Quittungen)
docs/               ADRs, Rechteverzeichnis, Datenschutz, Evidenzbilanz, Planungshistorie
.github/workflows/  CI-Workflows (Abschnitt 18)
```

Zugriffsrechte:
- Produktagenten schreiben nur auf Arbeitsbranches. In `main` kommt nur, wer alle Gates besteht und von einem fremden Agenten geprüft wurde.
- Die Prüfgruppe besitzt das Sollwissen im privaten Prüfbereich und stellt Nachweise aus.
- Der laufende Kandidat kann während einer verdeckten Prüfung nur die eigene Aufgabeneingabe lesen.
- Der Release-Dienst erhält ausschliesslich das geprüfte Archiv und den zulässigen Apple-Auftrag.

---

## 8. Steuerung und Zustandsmaschine

Die Aufgabensteuerung ist eine **gewöhnliche, deterministische Zustandsmaschine** (Code in `produkt/werkzeuge/steuerung/` oder `steuerung/werkzeug/`, Daten in `steuerung/auftraege/`). Sie ist kein Agent.

- **Zustände**:
  - Normalweg: `planned → ready → leased → running → verifying → done`
  - Zusätzlich: `retry_wait`, `reconciling`, `blocked`, `superseded`
- **Pro Auftrag gespeichert**: ID, Revision, Phase, Abhängigkeiten, Eingabedigests, Lease (Inhaber, Ablauf), **Berechtigungsnummer (Fencing-Token)**, Versuchszahl, nächster Prüfzeitpunkt, Ergebnisverweise, Begründung bei `blocked`.
- **Nebenläufigkeit**: Bei jeder Neuvergabe steigt die Berechtigungsnummer. Ein verspäteter alter Worker kann danach keinen gültigen Abschluss mehr schreiben. Merge und Upload laufen über einen Dienst, der Berechtigungsnummer und eindeutige Operations-ID prüft.
- **Idempotenz**: Merge, Publikation und Upload vertragen Wiederholungen. Vor jedem Upload wird nach derselben Buildnummer gesucht, nie wird blind erneut hochgeladen.
- **Wiederaufnahme**: Nach einem Neustart rekonstruiert eine neue Instanz aus Repository und Sicherung die Aufträge, Artefakte und offenen externen Wirkungen.

---

## 9. Kernartefakte (Spezifikation)

Die Startversionen liegen in `produkt/vertraege/`. Du verfeinerst sie in Phase 0 und versionierst jede Änderung.

### 9.1 Beweisregel (`beweisregel.schema.json`)
Felder:
- **Identität**: `schemaVersion`, `id`, `version`, `claimId`
- **Lernziel und Quelle** (`target`): kantonale Referenzen mit Kanton, Schulsprache, Kompetenzcode, Stufe, Ausgabe, URL, beobachtbarer Tätigkeit und Bezug (`teil`/`voll`)
- **Anwendbarkeit**: zulässige Aufgabenverträge, Anfangszustände, Einzelversuch oder mehrere Versuche, Nachweisform, Beobachtungsfenster
- **Entscheidungslogik**: Version des Faktenkatalogs, `requires.all` (zwingend wahr), `requires.none` (zwingend als falsch belegt), Gültigkeits- und Hilferegel, Verhalten bei `unbekannt`
- **Aussagegrenze**: alternative Erklärungen, maschinenlesbare Gegenproben (`must_claim`, `must_not_claim`, `undecidable` mit Verweis auf Ereignisspuren), erlaubter Wortlaut (de-CH) und Rückfall bei unzureichender Beobachtung

### 9.2 Beobachtungsprotokoll (`ereignis.schema.json`)
Hülle jedes Ereignisses:
- `type`, `schemaVersion`, `eventId` (eindeutig), `streamId` (Versuch, bei Anlage einem lokalen Profil zugeordnet)
- `seq` (fortlaufend), `occurredAt`, optional `monotonicNs` mit Boot-ID, `actor` (`child`, `app`, `system`)
- `candidate` (Build- und Inhaltsversion), `payload` (typgebunden)

Ereignistypen:

| Typ | Hält fest |
|---|---|
| `attempt.opened` / `attempt.closed` | Aufgabenfassung, Familie, Darstellung, Lernziel, Anfangszustand, tatsächlicher Abschlussgrund |
| `input.captured` / `recognition.proposed` | Eingabeart und Eingabe-ID, danach eine Lesart mit eigener ID und Unsicherheit |
| `answer.committed` / `response.retracted` | definitiver Wert und Herkunft (direkt, automatisch übernommen, bestätigt, korrigiert), Rücknahme mit Verweis |
| `material.moved` / `action.undone` | Plättchen-IDs, Ausgangs- und Zielzone, Akteur, Bedienart, rückgängig gemachte Bewegung |
| `support.presented` / `mode.changed` | tatsächlich angebotene Hilfe, betroffenes Lernziel, Wirkung, Kanal, Wechsel der Eingabeart |
| `artifact.saved` / `self_report.recorded` | lokal abgelegtes Werk mit Herkunft (selbst erstellt oder importiert), ausdrückliche Selbstauskunft |
| `condition.observed` | Unterbrechung, fehlende Berechtigung, zweifelhafte Uhr, nachgewiesene Lücke |
| `content.withdrawn`, `observation.invalidated`, `artifact.deleted`, `profile.erasure_requested` | Rückzug, Neuberechnung und Löschung als getrennte Vorgänge |

Integrität:
- Eine mehrfach zugestellte, identische Bewegung wirkt nur einmal.
- Als Integritätsfehler gelten: dieselbe `eventId` mit anderem Inhalt, zwei verschiedene Ereignisse an derselben `seq`, ein Ereignis aus einem fremden Stream.
- Nach einem Neustart wird der Bericht aus den gültigen Ereignissen wiederhergestellt.
- Rohhandschrift kann nach einer Aufbewahrungsregel gelöscht werden, ohne den Entscheidungsweg zu verlieren.
- Eine Profillöschung erfasst alle Beobachtungen und Anhänge dieses Profils.

Pflichtspur für die falsch gelesene Fünf: `input.captured` → `recognition.proposed` (Lesart «16») → `answer.committed` (Wert 15, Herkunft `korrigiert`) → `attempt.closed`. Die Lesart «16» erzeugt zu keinem Zeitpunkt einen fachlichen Fehler.

### 9.3 Zweiachsiger Belegstatus (`belegstatus.schema.json`)
- **Achse 1, Prüfverfahren**: `regeltest`, `lernsimulation`, `strich_replay`, `ui_automation`, `instrumentierte_messung`, `unabhaengige_ki_pruefung`, `quellenpruefung`. Bei offenem Nachweis `none`.
- **Achse 2, Geltungsbereich**: Kandidat, Ziel, Ausführungsort (`adapter`, `simulator`, `physisches_geraet`), Laufzeitversion, Geräteklasse, Eingabeart, Population (z.B. `synthetisch`), Prüfsatz, unabhängige Auswertungseinheit, Bedingungen, Ausschlüsse. Ein physisches iPad ist ein Ausführungsort und gehört deshalb auf Achse 2.
- **Ergebnis**: `open`, `passed`, `failed`, `inconclusive`
- **Herkunft**: Zeitpunkt, Prüfidentität, Lauf-ID, Digests von Prüfsatz, Prüfregeln und Bericht. Frühere Ergebnisse bleiben nachvollziehbar.
- **Gültigkeit**: Ein Beleg gilt nur für den Kandidaten, an den er gebunden ist. Für einen neuen Kandidaten muss die Anwendbarkeit neu belegt werden.
- **Formulierung**: Der Erwachsenenbericht lautet zum Beispiel «Im Simulator mit synthetischen Fingerstrichen geprüft. Genauigkeit bei Kindern offen.» Im Kinderheft steht nur kindgerechter Text («Ich habe 16 gelesen. Stimmt das?») ohne Prüfetiketten.

---

## 10. Lehrplan 21 und Schweiz

- **Kleinste Referenz ist die Kompetenzstufe**, zerlegt in beobachtbare Tätigkeiten. Pro Lernziel werden gespeichert:
  - Kanton, Ausgabe und Schulsprache
  - Fach, Kompetenzbereich, Handlungs- oder Themenaspekt
  - Kompetenzcode und Stufe
  - Grundanspruch und Orientierungspunkt
  - die eigene Klassenempfehlung, als solche erkennbar
- **Zyklus 1** umfasst Kindergarten sowie 1. und 2. Klasse. Der **Orientierungspunkt** am Ende der 4. Klasse bezeichnet die verbindlich zu bearbeitenden Stufen. Einzelne Fachbereiche haben auch in Zyklus 2 keinen. Das Datenmodell unterscheidet deshalb `fachlich_nicht_vorgesehen` von `quelle_fehlt`.
- **Profile**:
  - Luzern: Englisch ab der 3., Französisch ab der 5. Klasse
  - Bern (deutschsprachig): Französisch ab der 3., Englisch ab der 5. Klasse
  - Bei einem Profilwechsel wandern datierte Beobachtungen mit, und die Zuordnung zum neuen Profil wird neu berechnet. Eine Französischleistung darf weder verschwinden noch auf Englisch übertragen werden.
- **Lehrplanbezug des Leitfalls**: MA.1.C.1.b (Summe darstellen und nachvollziehen), MA.1.C.1.c (Rechenweg darstellen und nachvollziehen), MA.1.A.3 (Stufe a: nichtzählendes Rechnen bis 20, Stufe b: Ergänzen zum nächsten Zehner). Ein einzelner Weg deckt jeweils nur einen Ausschnitt ab.
- **Quellen**: nur öffentlich zugängliche Lehrplanfassungen, mit URL, Ausgabe und Abrufdatum. Keine Lehrplantexte im Wortlaut, sondern Codes und eigene Formulierungen. Die offizielle Lehrplan-Schnittstelle ist keine Voraussetzung. Keine Logos.
- **«Ohne Lesen lösbar»** (Zyklus 1): Navigation, Auftrag, Hilfe und Rückkehr sind ohne selbstständiges Lesen verständlich. Beim Lernziel Lesen bleibt das zu lesende Wort geschützt. Wird es vorgelesen, ist das ein anderer Nachweis. Dasselbe gilt für Transkripte beim Hörverstehen und für automatische Korrektur im Diktat.
- **Zahlenschreibweise**: 1'000 ist der Hausstil, aber kein Richtigkeitskriterium. Zahlenwert, Geldbetrag («3 Fr. 50 Rp.» = «Fr. 3.50») und ausdrücklich verlangte Schreibweise haben getrennte Bewertungsregeln.
- **Sprache**: Schweizer Standarddeutsch, kein ß. Mundart und Standardsprache treten in bewusst getrennten Situationen auf.

---

## 11. Fächer und Gegenprobenkatalog

Alle Fachbereiche werden abgedeckt. Pro Fach gibt es einen typischen Lernweg, einen Grenzfall und einen alternativen Zugangsweg, **bevor** die breite Inhaltsproduktion beginnt. Diese Gegenproben sind Pflicht (öffentlicher Katalog in `pruefung/gegenproben.md`, verdeckte Instanzen im Prüfbereich):

- **Mathematik** (Zahl und Variable; Form und Raum; Grössen, Funktionen, Daten und Zufall; Handlungsaspekte Operieren und Benennen, Erforschen und Argumentieren, Mathematisieren und Darstellen)
  - Gegenprobe: ein gültiger unvorhergesehener Rechenweg, eine korrekte Menge mit gespiegelt geschriebener Ziffer, eine gedrehte geometrische Figur.
  - Erwartet: Zahlenwert, Verfahren, Schriftform und geometrische Eigenschaft werden getrennt anerkannt.
- **Deutsch** (Hören, Sprechen, Lesen, Schreiben, Sprache(n) im Fokus und **D.6 Literatur im Fokus**)
  - Gegenprobe: dasselbe Wort mit verratendem, neutralem und fehlendem Bild, dazu zwei begründbare Deutungen einer Geschichte.
  - Erwartet: Bildwahl, Entziffern und literarisches Deuten ergeben unterschiedliche Aussagen.
- **Englisch**
  - Gegenprobe: ein Hörtext, einmal allein und einmal mit sichtbarem Transkript gelöst.
  - Erwartet: Bei der Sprachmittlung sind mehrere sinngemässe Formulierungen gültig.
- **Französisch**
  - Gegenprobe: Zwei Antworten geben eine Einladung sinngemäss richtig wieder, eine dritte vertauscht Tag oder Uhrzeit.
  - Erwartet: Ein fehlerhaftes Transkript erzeugt keine negative Aussprachebewertung.
- **NMG** (alle zwölf Kompetenzbereiche der Zyklen 1 und 2)
  - Gegenprobe: zwei gleiche Schlussantworten. Ein Kind hat seine Vorhersage nach einer Beobachtung überarbeitet, das andere hat die angebotene Erklärung übernommen.
  - Erwartet: Nur der erste Verlauf dokumentiert eine Revision.
- **Medien und Informatik**
  - Gegenprobe: zwei Programme mit gleichem Ergebnis beim ersten Eingang und verschiedenem beim zweiten. Dazu eine professionell gestaltete erfundene Quelle gegen eine schlicht gestaltete belegte Quelle.
- **Musik**
  - Gegenprobe: derselbe Rhythmus in verändertem, zulässigem Tempo, und eine importierte Aufnahme, die perfekt klingt.
  - Erwartet: Rhythmus, Tempo und eigene Ausführung werden einzeln ausgewiesen.
- **Bildnerisches Gestalten**
  - Gegenprobe: zwei verschiedene Werke erfüllen dasselbe Kriterium, und ein importiertes Bild gleicht der Vorlage stärker als beide.
  - Erwartet: Die Ähnlichkeit zur Vorlage entscheidet weder über Kreativität noch über Urheberschaft.
- **Textiles und Technisches Gestalten**
  - Gegenprobe: gleiches Schlussfoto bei unterschiedlichen Herstellungsverfahren.
  - Erwartet: Eine dokumentierte Planänderung darf gewürdigt werden. Werkzeugbeherrschung und Belastbarkeit bleiben ohne Beobachtung offen.
- **Bewegung und Sport**
  - Gegenprobe: eine Bewegungsfolge ordnen, die Durchführung selbst bestätigen, die Kamera ablehnen.
  - Erwartet: eine Planungsleistung und eine Selbstauskunft. Die Ausführung bleibt offen.
- **Überfachliches und BNE**
  - Gegenprobe: zwei gegensätzliche, begründete Entscheidungen in einem Ressourcenkonflikt.
  - Erwartet: Begründung und Perspektiven sind beobachtbar. Kooperation und Haltung brauchen einen eigenen Nachweis.

Für **jede Nachweisform** gibt es mindestens eines dieser Paare:
- freie Antwort gegen Wiedererkennen
- selbst ausgeführter gegen vorgegebenen Schritt
- eigenes gegen importiertes Werk
- Selbstbericht gegen Beobachtung
- begründete offene Antwort gegen fast identische Antwort mit sinnverändernder Verneinung

Für Behalten und Transfer gibt es vier Fälle: gleiche Aufgabe später, neue Darstellung sofort, neue Darstellung später, unzuverlässige Gerätezeit. Ist die Zeit unklar, bleibt «erneut gezeigt» eine ehrliche Aussage.

Für praktische und soziale Ziele gilt: Es gibt immer eine Variante ohne Kamera oder Mikrofon. Die Matrix weist aus, was mit einem Einzelgerät überhaupt beobachtbar ist. Gültiger Endzustand ist dann «Teilbeitrag verfügbar, Kompetenz digital nicht ausreichend beobachtbar». Aufträge, die Aufsicht erfordern, werden zu sicheren Beobachtungs- oder Planungsaufgaben mit engerem Nachweis.

---

## 12. Handschrift

- In Version 1 bewertet die App automatisch **nur Ziffern, einfache Operatoren und kurze Zahlenfolgen**. Freies Schreiben und Zeichnen sind trotzdem überall möglich. Das Original bleibt sichtbar, und das Kind bestätigt, ändert oder wechselt zum Ziffernblock.
- Die Erkennung läuft lokal (Core ML) über PencilKit-Striche und nutzt Form und zeitlichen Verlauf. RecognitionKit kennt **nur den erwarteten Zeichentyp, nie die Lösung**. Das ist über Modulabhängigkeiten erzwungen und per Architekturtest geprüft.
- **Unabhängigkeitskriterium** statt einer festen Zahl von Generatoren: Mindestens zwei wirklich verschiedene Grundlagen.
  - verschiedene Ausgangsformen pro Zeichen: offene und geschlossene Vier, Eins mit und ohne Aufstrich, Sieben mit und ohne Querstrich, alternative Strichreihenfolgen
  - ein neuromotorisches Bewegungsmodell (Kandidat: Sigma-Lognormal) mit Geräteschicht für Abtastlücken sowie Finger- und Stifteigenschaften
  - Ein gelerntes Modell ist eine Option. Lernt es nur von den eigenen Generatoren, zählt es als Variante derselben Grundlage.
  - Öffentliche Datensätze wie EMNIST nur mit passender Lizenz und nur ergänzend. Herkunft der Grundpfade und Generatoren dokumentieren.
- **Verdeckte Abnahme**: Entwicklung, Kalibrierung und Abnahme sind getrennt nach Pfadherkunft, Generator, Stil und Gerätebedingungen.
  - Getestet werden auch ganze Antworten (15, 51), Korrekturen und leere Eingaben.
  - Derselbe Strich muss bei verschiedenen Musterlösungen dieselben Lesarten erzeugen.
  - Rückfragen verraten die Lösung weder durch Auswahl noch durch Vorbelegung.
- **Metrik**:
  - Ziel: mindestens 90 % automatische Bewertbarkeit, mit vorab festgelegtem Nenner und eigener Unsicherheitsgrenze, bezogen auf alle auswertbaren Antworten vor jeder Nachfrage.
  - Bestätigung, Korrektur und Wechsel zum Ziffernblock werden separat gezählt.
  - Technisch falsch negative und falsch positive Bewertungen werden getrennt ausgewiesen, je verdeckter Familie und Eingabeart.
  - Ziel: technisch verursachte Fehlbewertungen unter 0,5 %, gemessen an der **oberen 95-%-Grenze**. Die Faustzahl «rund 598 unabhängige Fälle» gilt nur als Sonderfall: null Fehler, unabhängige Fälle, eine vorab bestimmte Gruppe, einseitige exakte Grenze. Für viele Gruppen und wiederholte Versuche ist das statistisch korrekt zu planen.
- **Drei Beweise getrennt**:
  - Adapter-Replay für die Erkennungskette
  - XCUITest-Gesten für die echte Oberfläche
  - ein physisches Gerät (falls verfügbar) für Latenz und Pencil
  - Ein Simulator-Replay belegt weder Handballenkontakt noch Pencil-Druck. Ohne Hardware bleibt das offen.
- **Spiegelverkehrte Ziffern sind kein pauschaler Fehler.** Bei Mengenaufgaben kann das Verständnis trotz Spiegelung stimmen. Nur beim Lernziel «Ziffer richtig orientiert schreiben» zählt sie. Bei Mehrdeutigkeit fragt die App neutral nach.
- Der Ziffernblock ist immer erreichbar, auch direkt nach einer Rückfrage. Die Handschriftbewertung lässt sich im Erwachsenenbereich pro Profil abschalten.

---

## 13. Simulation von Lernenden (LearnerSim)

- **Drei getrennte Modelle**:
  - Fachmodell: Strategie oder Fehlvorstellung
  - Bedienmodell: bedient die echte Oberfläche ohne Kenntnis der Lösung oder des Lernstandsmodells
  - Beobachtermodell: prüft, welche Aussage die Ereignisse tragen
- Die Persona «kann nicht lesen» erhält keine Test-IDs oder Beschriftungen als Ersatz fürs Lesen. Die VoiceOver-Persona erhält genau den Zugang, den VoiceOver bietet.
- **Bibliothek der Fehlvorstellungen**, Startumfang (jeweils Muster → Gegenprobe):
  - Zahlverständnis: Eins-zu-eins-Zuordnung unsicher, letztes Zahlwort nicht als Anzahl verstanden → sieben Plättchen umordnen, zählen lassen, dann nach der Gesamtzahl fragen.
  - Stellenwert: Ziffern einzeln behandelt, leere Stelle verschwindet → 304 aus Material legen und ein umgeordnetes Bündelbild lesen. Eine vertippte Null bleibt eine mögliche Erklärung.
  - Gleichheitszeichen als Aufforderung zum Ausrechnen → 8 + 4 = □ + 5 und eine Waage im Bild. Die Antwort 12 allein ist nicht eindeutig.
  - Brüche: grösserer Nenner als grössere Menge gedeutet → Drittel und Fünftel auf gleich langen Streifen, dann die Grösse des Ganzen ändern.
  - Schriftspracherwerb: Buchstabenname und Laut verwechselt, Grapheme getrennt, Raten anhand des Bilds → unbekanntes Wort ohne verratendes Bild, Hörverständnis separat.
  - NMG: «Schwere Dinge sinken» → Vorhersage, Beobachtung, überarbeitete Erklärung.
  - Informatik: Schleife über zwei Aktionen als Einzelwiederholung gelesen → dreimal [Schritt, Drehung] mit «drei Schritte, drei Drehungen» vergleichen.
  - Weitere Fehlvorstellungen nur aus dokumentierter Fachliteratur, mit Quelle.
- **Pflichtpaare** mit gleichem sichtbaren Verhalten und verschiedener Ursache, zum Beispiel: korrekt gezählt und vertippt gegen verzählt und genau getippt. Bei identischen Daten besteht die App nur mit offener Formulierung und passender Anschlussaufgabe.
- Die Simulationsmodelle stammen von anderen Agenten als das Produkt und werden nicht aus dem App-Code abgeleitet.

---

## 14. Lernlogik, Hilfen und Tests

- **Stufen des Lernstands** pro Tätigkeit: mit Hilfe gezeigt, selbstständig gezeigt, nach einer Pause erneut gezeigt, in neuer Darstellung angewendet. Gespeichert werden auch Aufgabenfamilie, Hilfe, Eingabeart und Unsicherheit.
- **Neues lernen**: Vormachen mit hörbaren Gedanken, dann eine teilweise vorbereitete Aufgabe, dann eine eigene.
- **Hilfen in Stufen**: Aufmerksamkeit lenken, Teilschritt zeigen, Lösungsweg zeigen. Danach folgt eine neue, verwandte Aufgabe für einen eigenen Versuch.
- **Steuerung**: Ausgangspunkt ist eine einfache, erklärte Wiederholungsregel. FSRS, BKT oder IRT kommen nur zum Einsatz, wenn sie gegen mehrere fremd entwickelte Lernmodelle (Vergessen, Raten, Abhängigkeit von der Darstellung, Strategiewechsel) bessere zeitlich spätere Vorhersagen liefern. Rund 80 % Erfolg ist ein einstellbarer Übungswert.
- **Fehler**: Eine einzelne falsche Antwort ist nur eine Vermutung. Eine Anschlussaufgabe klärt, ob es am Stellenwert, an der Anweisung oder an der Eingabe liegt.
- **Tests auf vier Ebenen**:
  - Lektionscheck (unbenotet)
  - Modultest (neue Familien, mit und ohne Hilfe getrennt, verzögerte Wiederaufnahme)
  - Kapiteltest (mindestens eine Aufgabe zum Begründen oder Anwenden)
  - Jahresbilanz (Prüfplan pro Fach plus praktische Dokumentation)
- **Keine Schulnoten** und kein Gesamt-«Fitness-Wert». Stattdessen konkrete Aussagen wie «Vergleicht gleichnamige Brüche sicher, braucht bei unterschiedlichen Nennern noch eine Zeichnung».

---

## 15. Inhaltsproduktion

1. **Lernziel**: Der Autor-Agent beschreibt Tätigkeit, Vorwissen, beobachtbaren Nachweis und Kompetenzcode. Der Kritiker prüft gegen die öffentliche Quelle.
2. **Aufgabenfamilie** als versioniertes JSON: Auftrag, Audiotext, Darstellungen, alle gültigen Lösungen, zulässige Varianten, Fehlvorstellungen, Hilfen, Barrierefreiheit, Rechtevermerk, zugehörige Beweisregeln.
3. **Unabhängiges Lösen** ohne Schlüssel, in anderem Kontext. Danach prüfen Agenten Mehrdeutigkeit, Leselast, Schweizer Sprachgebrauch und alternative Wege.
4. **Generatoren**: reproduzierbar über Version und Startwert, mit mindestens einer Million Startwerten gegen Invarianten: lösbar, Lösung korrekt, keine doppelten Optionen, keine versteckten Hinweise, Einheiten stimmen, Grenzen des Zahlenraums eingehalten.
5. **Simulierte Erprobung** mit LearnerSim, Persona-Agenten und Audits.
6. **Freigabe** nur durch Gates und einen fremden Prüfagenten. Fehlerhafte Familien lassen sich zurückziehen, betroffene Beobachtungen werden ungültig gemacht und Aussagen neu berechnet.

**Produktionszahlen** (Module, Familien, Startwerte, Generatoren) sind nur Betriebskennzahlen. Freigegeben werden unterscheidbare fachliche Leistungen, unabhängige Prüfgrundlagen und funktionierende Lernwege. Inhaltlich doppelte Familien erhöhen die Abdeckung nicht. Orientierungsgrösse für die Gesamtvision sind über 400 Module und über 15'000 kuratierte Aufgaben plus Generatoren. Massgebend ist aber die Abdeckungsmatrix.

Die Kennzeichnung «fachlich geprüft» bedeutet in Chnobel: von unabhängigen KI-Agenten und automatischen Prüfungen geprüft. Die App sagt das auch so.

---

## 16. Erlebnis, Schweizreise und Barrierefreiheit

- **Reise am Lernhandeln**: Ein Kind findet zwei gleichwertige Wege nach Luzern und wählt selbst, welchen es ins Reisebuch übernimmt. Wer Hilfe nutzt, erreicht denselben Ort mit derselben Ortswahl.
- **Altersgruppen**: Für jüngere Kinder ruhig und gesprochen. Für ältere tragen Fahrpläne, Karten und eigene Entscheidungen die Geschichte.
- **Prüfbare Eigenschaften**:
  - Wahlfreiheit
  - eine Runde lässt sich beenden
  - nach einer Woche findet das Kind genau seine Seite wieder
  - die Anweisung lässt sich wiederholen
  - Ausstieg und Rückkehr funktionieren
  - Ob Kinder die Reise mögen, bleibt offen.
- **Ablauf**: Einstieg in Sekunden über ein Bildprofil mit «Weiterlernen», «Etwas entdecken» oder «Wiederholen». Runden dauern 5 bis 10 Minuten und haben ein echtes Ende. Pausen kosten nichts.
- **Keine Manipulation**: keine Werbung, keine Lootboxen, keine In-App-Käufe, keine Serien mit Verlustangst.
- **Grafik und Klang**:
  - Grafik prozedural (SwiftUI Canvas und Shapes, SF Symbols, eigene Vektorgrafiken) mit einem Design-System für zwei Altersgruppen.
  - Audio mit Systemstimmen oder vorab erzeugten, mitgelieferten und rechtlich geklärten Sprachdateien. Ein Aussprache-Lexikon deckt Schweizer Begriffe und Ortsnamen ab. Klänge werden synthetisch erzeugt.
- **Barrierefreiheit in jedem Aufgabentyp**:
  - Antippen statt Ziehen
  - Form oder Muster zusätzlich zur Farbe
  - eine visuelle Alternative zu Audio
  - VoiceOver, Schaltersteuerung, Hardware-Tastatur, Dynamic Type, reduzierte Bewegung, Bedienung für Linkshänder
  - Pro Zugangsart wird der tatsächliche Weg geprüft: notwendige Handlungen, wiederholbare Anweisung, Ausstieg, Rückkehr zur eigenen Seite.
  - Bei Alternativen hält die App fest, welche Kompetenz weiterhin beurteilbar ist.
- **Förderung**: Bildwortschatz für Kinder mit Deutsch als Zweitsprache, strukturierte Mengenbilder, wählbare Schrift und Abstände, ohne Wirksamkeitsversprechen.
- **Rollen in der App**: Kind (mehrere lokale Bildprofile ohne Konto) und Erwachsene (gesicherter Bereich mit Berichten, Zeitlimiten, Export, Löschung, Abschalten der Handschriftbewertung). Lehrpersonenbereich, iCloud und ClassKit sind **nicht** Teil der Abnahme.

---

## 17. Technik, Datenschutz und Offline

- **Plattform**: SwiftUI, Swift 6 (strict concurrency), Observation, SwiftData. Mindestens iPadOS 18.
- **Schnittstellen**:
  - RecognitionKit liefert Lesarten mit Unsicherheit.
  - TaskEngine bewertet die bestätigte Eingabe gemäss Lernziel und schreibt Ereignisse.
  - LearningEngine leitet aus dem Beobachtungsprotokoll über Beweisregeln die Aussagen ab.
  - Inhalte, Bewertung, Regeln und Lernstandsberechnung tragen je eigene Versionen.
- **Offline-Garantie**: Getestet wird mit frischer Installation und gesperrtem Netz, ohne heruntergeladene Zusatzstimme, ohne Mikrofonrecht und mit deaktivierter Spracherkennung. Lokale Spracherkennung kommt nur zum Einsatz, wenn sie für die konkrete Konfiguration unterstützt ist.
- **Datenfluss**: Geprüft werden SwiftData-Dateien, Anhänge, Vorschaubilder, Backups, Export, Logs und Testberichte.
  - Foto und Stimme sind optional, der Exportumfang ist ausdrücklich definiert.
  - In CI und TestFlight gibt es nur synthetische Profile.
  - Rohhandschrift und Stimme verlassen nie das Gerät.
- **Privacy Manifest und App-Privacy-Angaben** passen zum tatsächlichen Verhalten. TestFlight erhebt eigene Diagnosedaten, und ein Privacy Manifest allein belegt die Zusage nicht.
- **Recht**: DSG, räumliche Anwendbarkeit der DSGVO und die Kids-Category-Regeln sind getrennte Prüffragen.
  - Abgelegt werden `docs/datenschutz/` (Prüfung, Datenschutz-Folgenabschätzung falls hohes Risiko, Restrisiken) und `docs/rechteverzeichnis.md`.
  - Erfasst ist jedes Asset: Herkunft, Lizenz, Zweck, Buildversion. Ungeklärte Assets werden ersetzt oder entfernt.

---

## 18. CI und Freigabebeleg

CI-Workflows (GitHub Actions auf macOS-Runnern oder Xcode Cloud):

| Job | Zweck |
|---|---|
| `preflight` | Schemas, Inhaltsvalidierung, Rechteverzeichnis, Secret-Scan, Lint, Architekturtests |
| `product-check` | Build, Swift Testing, UI-, Snapshot-, Inhalts- und Mutationstests, Accessibility-Audits, Performance, Migration |
| `freeze-build` | Kandidat einfrieren: Commit, Archiv, Digests |
| `independent-check` | Prüfgruppe: verdeckte Prüfsätze, Bildschirmabgleich, Gegenproben, Handschrift-Abnahme |
| `issue-verdict` | Freigabebeleg ausstellen |
| `release-internal` | signieren, exportieren, hochladen, Apple-Status prüfen |
| `reconcile` | offene externe Wirkungen abgleichen |
| `recovery-drill` | Wiederherstellung proben |

Regeln:
- **Freigabebeleg**: Er bindet Pflichtprüfungen, erwartete Fallzahlen, tatsächliche Ausführung, Absender und Artefaktdigests an genau einen Kandidaten. Ein **leerer, übersprungener, null Fälle auswählender oder fremdem Kandidaten zugehöriger Pflichtlauf sperrt das Release.** Ein übersprungener Job zählt nie als Erfolg.
- Der Pflichtstatus ist an die erwartete CI-Identität gebunden. Bei einer Merge Queue wird auch `merge_group` geprüft.
- **Entwicklungsprüfung und Schlussabnahme sind getrennt.** Der finale Kandidat wird eingefroren, bevor die Prüfgruppe den letzten verdeckten Satz zieht. Offengelegte Prüffälle werden Regressionstests und scheiden aus der verdeckten Abnahme aus.
- Ein geplanter Workflow ist nie der einzige Wächter, weil GitHub geplante Workflows in öffentlichen Repositories nach 60 Tagen ohne Aktivität deaktivieren kann.
- Verdeckte Prüfungen und Secrets erscheinen nie in öffentlichen Dateien oder Logs. Builds, Archive und Prüfsets sind nicht öffentlich herunterladbar.

---

## 19. Release und Apple-Endzustand

1. Den integrierten Stand einfrieren, **ein** Archiv erstellen und dessen Digest bestätigen.
2. Aus diesem Archiv exportieren, **ohne erneut zu kompilieren**. Archiv- und IPA-Digest, Team, Bundle-ID, Version, Buildnummer und Uploadabsicht in `steuerung/release/` festhalten.
3. Vor dem Upload nach derselben Buildnummer suchen und erst dann über die App Store Connect API hochladen. Verschlüsselungsangaben werden aus dem tatsächlichen Binary abgeleitet.
4. **Zielzustand**:
   - erwartete App und Buildnummer, gültig verarbeitet
   - `INTERNAL_ONLY`
   - interner Bereitschaftsstatus, zum Beispiel `READY_FOR_BETA_TESTING`
   - geklärte Export-Compliance
   - Ablaufdatum in der Zukunft (interne Builds sind 90 Tage testbar)
   - Niemanden einladen. Bei einem unerwarteten Status zuerst Gruppen und Empfänger prüfen.
5. Bei langsamer Verarbeitung den Status in wachsenden Abständen prüfen. Technisch behebbare Fehler werden repariert und mit neuer Buildnummer erneut hochgeladen. Eine nötige Aktion des Kontoinhabers ergibt `extern blockiert`.

---

## 20. Roadmap

Jede Phase endet erst, wenn ihr Kriterium automatisch belegt ist.

**Phase 0: Betriebsfähigkeit und Apple-Durchstich**
- **Ergebnis**: Eine minimale iPad-App führt einen synthetischen Versuch mit 8 + 7 durch, stellt ihn nach einem Neustart wieder her, erzeugt die passenden engen Berichte und erreicht den internen TestFlight-Zielzustand.
- **Aufbau**:
  - Verzeichnisse und Rechte (Abschnitt 7)
  - Zustandsmaschine mit Leases und Fencing (Abschnitt 8)
  - Verträge v1 (Abschnitt 9) mit Referenzprüfer in `produkt/werkzeuge/`, der Ereignisspuren gegen Beweisregeln auswertet, inklusive doppelter Zustellung und absichtlich ungültiger Fälle
  - Ereignisverläufe für 8 + 7 (mindestens 20), darunter Hinweis nach dem Zug, Undo und erneuter Zug nach Hinweis, App-Demo mit Wiederholung, Fehllesung mit Korrektur, Abbruch und Lücke
  - CI-Jobs (Abschnitt 18), Release-Pipeline (Abschnitt 19), ADR 0001
- **Fünf Betriebsproben**, alle bestanden:
  1. Zwei Worker übernehmen denselben Auftrag. Nur einer kann eine gültige Wirkung bestätigen.
  2. Der Worker stirbt direkt nach dem Upload. Der Nachfolger findet den Vorgang oder hält ihn begründet ausstehend, ohne blind erneut hochzuladen.
  3. Ein Pflichtjob wird übersprungen oder wählt null Fälle. Die Freigabe sperrt.
  4. Ein anderer Kandidat präsentiert einen gültigen grünen Bericht. Die falsche Artefaktbindung fällt auf.
  5. Eine neue Steuerungsinstanz rekonstruiert aus der Sicherung Aufträge, Artefakte und offene externe Wirkungen. Der geprüfte Build bleibt eindeutig zuordenbar.

**Phase 1: drei vollständige Lehrproben**
- **Inhalt**: 8 + 7 mit freiem Weg, eine Laut- und Leseaufgabe und ein praktischer Auftrag mit optionaler Dokumentation, jeweils mit Beweisregeln und den drei Pflichtfällen.
- **Kriterium**:
  - Alternativlösung, Fehllesung, verratender Hinweis, fehlende Berechtigung und unzureichender Nachweis ergeben die vorgesehenen Aussagen.
  - Der unabhängige Bildschirmabgleich ist in Betrieb, und ein manipulierter Kandidat fällt durch.

**Phase 2: Handschrift und Bedienung**
- **Inhalt**: unabhängige Grundlagen, verdeckte Abnahme, Fingerbedienung, Ziffernblock, zugängliche Alternativen.
- **Kriterium**: Fehler- und Abdeckungsgrenzen pro Testgruppe bestanden. Belege aus Adapter, Simulator und Hardware sind getrennt ausgewiesen.

**Phase 3: Planungsmatrix Luzern und Bern**
- **Inhalt**: Quellenstände, Kompetenzstufen in Tätigkeiten zerlegt, Nachweisformen, erlaubte Berichtsaussagen, erste Inhalte Mathematik und Deutsch für die 1.–2. Klasse.
- **Kriterium**: Jede Tätigkeit hat einen zulässigen Nachweis oder eine erklärte Beobachtungsgrenze. Ein Profilwechsel erhält die Beobachtungen.

**Phase 4: Ausbau nach Nachweisformen**
- **Inhalt**: 3.–6. Klasse, Fremdsprachen, NMG, Medien und Informatik, Gestalten, Musik, Bewegung und Sport.
- **Kriterium**: Pro Fach funktionieren ein typischer Lernweg, ein Grenzfall und ein alternativer Zugangsweg mit den Gegenproben aus Abschnitt 11.

**Phase 5: breite Inhaltsproduktion**
- **Inhalt**: Aufgabenfamilien, Hilfen, Gegenbeispiele, Behalten und Transfer für den ganzen Umfang.
- **Kriterium**: Verdeckte Stichproben je Fach, Zyklus und Nachweisform bestehen. Die Abdeckungsmatrix ist für beide Profile, die 1.–6. Klasse und alle Fachbereiche vollständig.

**Phase 6: unabhängige Schlussabnahme**
- **Inhalt**: eingefrorener Kandidat, neue verdeckte Aufgaben, Tests zu Offline, Migration, Löschung und Wiederherstellung, Red-Team-Durchgänge, vollständige Evidenzbilanz in `docs/evidenzbilanz.md`.
- **Kriterium**: keine offenen Befunde der Schwere kritisch oder hoch. Offene Aussagen über reale Kinder bleiben sichtbar. Der Bericht gilt für genau einen Kandidaten.

**Phase 7: finaler interner TestFlight-Build**
- **Inhalt**: Der geprüfte Kandidat wird signiert, verarbeitet und ist intern testbereit.
- **Kriterium**: Build-ID, Commit, Inhalts- und Modellversion, Apple-Status und Ablaufdatum stimmen überein.

---

## 21. Definition of Done

Das Projekt ist fertig, wenn **alle** Punkte belegt sind:
1. Die App bietet für den gesamten vereinbarten Umfang (Luzern und Bern, 1.–6. Klasse, alle Fachbereiche) passende Lerngelegenheiten.
2. Sie nennt für jede Leistungsrückmeldung den beobachteten Grund.
3. Bei fehlender Evidenz wählt sie zuverlässig eine engere Aussage.
4. Alle Pflichtjobs sind für genau diesen Kandidaten tatsächlich ausgeführt und bestanden, mit erwarteten Fallzahlen und gebundenen Digests. Keine Schwelle wurde nachträglich gesenkt.
5. Für jede zentrale Aussage sind die drei Pflichtfälle bestanden, und beide Fehlerarten liegen innerhalb der vorab festgelegten Grenzen.
6. Der unabhängige Bildschirmabgleich ist bestanden, und manipulierte Kandidaten fallen durch.
7. Die Handschrift-Kennzahlen sind auf allen verdeckten Testgruppen erreicht.
8. Barrierefreiheit: Alle Zugangsarten erreichen jeden Lernweg ohne Sackgasse, und die Audits sind fehlerfrei.
9. Offline-, Migrations-, Lösch- und Wiederherstellungstests sind bestanden.
10. Rechteverzeichnis, Datenschutz- und Kids-Category-Prüfung haben keine offenen Punkte.
11. Im Red-Team-Register gibt es keine offenen Befunde der Schwere kritisch oder hoch.
12. Jeder App-Text hat einen passenden Belegstatus, und keine Behauptung geht über ihren Beleg hinaus.
13. Der Build hat den Apple-Endzustand aus Abschnitt 19 erreicht.

---

## 22. Abschlussprotokoll: TestFlight-ready, dann warten

Sobald die Definition of Done erfüllt ist:
1. Schreibe `steuerung/ABSCHLUSS.md` mit:
   - Version, Buildnummer, Commit, Archiv- und IPA-Digest
   - Inhalts-, Regel- und Modellversionen
   - Apple-Status und Ablaufdatum des Builds
   - Zusammenfassung der Evidenzbilanz
   - Liste der offenen Nachweise (Abschnitt 23)
   - bekannte Einschränkungen
   - Hinweis: Der interne Build läuft nach 90 Tagen ab, ein neuer Upload erfordert einen neuen Auftrag.
2. Setze `steuerung/STATUS.md` auf `ZUSTAND: WARTEN`, mit Datum und Verweis auf `ABSCHLUSS.md`.
3. Committe, merge über die regulären Gates in `main` und pushe.
4. **Danach keine weiteren Änderungen, Uploads, Einladungen oder Optimierungen.** Beende die Arbeit mit einer kurzen Abschlussmeldung.
5. Bei jedem späteren Start: Steht `ZUSTAND: WARTEN`, gib nur die Zusammenfassung aus und warte auf einen neuen, ausdrücklichen Auftrag eines Menschen.

---

## 23. Offene Nachweise (bleiben sichtbar offen)

- Genauigkeit der Handschrifterkennung bei echten Kindern
- Verständlichkeit für Sechsjährige
- Motivation und freiwillige Rückkehr
- Lernwirksamkeit
- Fairness über verschiedene Gruppen von Kindern
- Feinheiten des Schweizer Sprachgebrauchs aus menschlicher Sicht
- Hardware-Verhalten (Pencil-Druck, Handballen, Latenz), sofern kein physisches Gerät angebunden war

Diese Punkte sind kein Grund, die Freigabe zu verweigern. Ein **prüfbarer** Produktfehler sperrt die Freigabe dagegen immer, zum Beispiel ein Ziffernblock, der nach einer Rückfrage nicht erreichbar ist.

---

## 24. Arbeitsweise und Kommunikation

- Arbeite in kleinen, überprüfbaren Schritten: Branch → Umsetzung → Gates → fremdes Review → Merge. Committe mit aussagekräftigen Nachrichten.
- Halte `steuerung/STATUS.md` stets aktuell. Sie ist die Übergabe an die nächste Sitzung.
- Stelle Menschen keine Fragen. Unklarheiten löst das Gremium mit der vorsichtigeren Option, dokumentiert als ADR oder Hypothese.
- Berichte nüchtern: bestanden, gescheitert (mit Ausgabe), blockiert (mit Grund), offen. Melde nie Erfolg ohne Beleg.
- Planungshistorie und Begründungen stehen in `docs/planung/`. Bei Widersprüchen gilt dieser Masterprompt vor der Historie.
