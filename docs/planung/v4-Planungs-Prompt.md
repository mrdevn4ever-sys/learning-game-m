# Kontext und Idee

«Chnobel» ist eine native Lern-App in Swift für die 1. bis 6. Primarklasse in der Deutschschweiz. Chnobel ist ein digitales Arbeitsheft, in dem Kinder ihren Denkweg zeigen. Sie schreiben Antworten von Hand (Finger oder Apple Pencil), legen Material wie Plättchen, Münzen oder Zeiger, oder arbeiten per Ziffernblock, Tastatur oder Antwortauswahl. Eine Reise durch die Schweiz gibt den Kindern einen Grund, das Heft gerne zu öffnen.

Der Kern ist ehrliche Rückmeldung. Chnobel sagt nur, was es tatsächlich beobachtet hat, und wählt bei fehlender Evidenz eine engere Aussage.

Der Leitfall dafür: Eine Erstklässlerin löst 8 + 7. Die App muss vier Fälle auseinanderhalten:
1. «15» geschrieben: Das Ergebnis stimmt.
2. Zwei Plättchen sichtbar zur Acht geschoben: Das Kind hat einen passenden Rechenweg dargestellt.
3. Die App hat die beiden Plättchen vorher aufleuchten lassen: Der Schritt war angeleitet.
4. 7 + 7 + 1 gelegt: ein anderer gültiger Weg.

Liest die App ihre Fünf als Sechs, berichtigt das Kind das mit einem naheliegenden Handgriff. Tage später bekommt es eine faire Gelegenheit, die Strategie selbst zu wählen. Ein System, das diese Fälle auseinanderhält, verdient mehr Vertrauen als eines mit 15'000 formal korrekten Aufgaben.

Zeit und Kosten spielen keine Rolle.

# Grundsatz: Die KI-Agenten erledigen alles

Eine Organisation aus KI-Agenten erledigt das gesamte Projekt autonom bis zu einem intern testbereiten TestFlight-Build. Das umfasst Planung, Code, Inhalte, Grafik, Audio, Tests, Prüfung, Freigabe und Upload. Kein Mensch arbeitet mit, auch ich als Auftraggeber nicht.

Ausgeschlossen sind:
- Kinder, Eltern, Lehrpersonen, Schulen und Fachpersonen
- Datenerhebungen über Personen
- eigene Server
- Einladungen von Testern, externe Tests und öffentliche Verteilung

Was belegbar ist und was nicht:
- **Belegbar**: Die App wertet einen dargestellten Rechenweg korrekt aus, fragt bei unklarer Handschrift nach, funktioniert offline und berechnet den Lernstand nach festgelegten Regeln.
- **Offen**: wie gut diese Regeln das Lernen echter Kinder abbilden.
- **Nicht garantierbar**: wann Apple einen Build verarbeitet.

Offene Punkte bleiben sichtbar als offen gekennzeichnet.

## Einmaliges Startpaket
Diese vier Bausteine müssen vor dem Start bereitstehen. Danach greift kein Mensch mehr ein.
1. **Apple-Developer-Mitgliedschaft**:
   - aktiv, mit akzeptierten aktuellen Verträgen und automatischer Verlängerung
   - App-Datensatz in App Store Connect angelegt, Bundle-ID, Team und Plattformen passen zusammen
   - Spätere Vertragsänderungen, denen der Kontoinhaber zustimmen muss, bleiben eine externe Grenze.
2. **Signier- und Uploadweg**:
   - ein .p8-API-Schlüssel für App Store Connect
   - funktionierendes verwaltetes Signing oder Zertifikat mit privatem Schlüssel und Provisioning-Profil
   - bewusste Wahl zwischen Team- und Einzelschlüssel, da Einzelschlüssel die Provisioning-Endpunkte nicht nutzen können
   - Der Release-Workflow akzeptiert ausschliesslich die Chnobel-App-ID.
3. **Repository mit Agenten- und CI-Identität**:
   - Branchschutz, Schreibrechte und Secrets
   - getrennter Prüfbereich für verdeckte Tests, nicht im öffentlichen Repository
   - Zugang zu den Modellen, die die Agenten tatsächlich brauchen
   - Builds, Archive, Prüfsets und Trainingsartefakte sind nicht öffentlich herunterladbar.
4. **Verwalteter macOS-Runner mit passendem Xcode**:
   - Deployment Target und Upload-SDK getrennt konfiguriert
   - Apples aktuelle Vorgaben (laut Recherche seit April 2026 Xcode 26 oder neuer) prüft die CI vor jedem Release erneut.
   - Optional: ein automatisiert zugängliches physisches iPad in einer Cloud-Gerätefarm für Hardware-Belege.

# Detaillierter Plan

## 1. Prioritäten
1. **Hoch: Beweisregel für jede Lernstandsaussage.** Jede Aussage hat:
   - die nötige Beobachtung
   - die zulässigen Hilfen
   - alternative Erklärungen
   - mindestens ein Gegenbeispiel, bei dem die App schweigen muss
2. **Hoch: Abnahme organisatorisch und technisch vom Produkt trennen.** Wer Inhalte oder Modelle verbessert, kann verdeckte Prüfaufgaben, deren Lösungen und die Freigaberegeln weder lesen noch ändern.
3. **Hoch: TestFlight-Durchstich an den Anfang.** Ein signiertes Minimalprodukt klärt App-Datensatz, Berechtigungen, Signing und internen Beta-Status, bevor Monate in Inhalte fliessen.
4. **Hoch: Drei Lehrproben vor der Massenproduktion.** Ein Rechenweg, eine Leseaufgabe und ein praktischer Auftrag erzwingen drei verschiedene Antworten auf die Frage, was die App beurteilen darf.
5. **Hoch: Enthaltung als Produktfunktion.** «Ich bin unsicher, welche Zahl du geschrieben hast», «Dein Ergebnis stimmt» und «Hier ist dein Werkstück» sind verschiedene Zustände. Sie bleiben auch nach Absturz, Profilwechsel oder Inhaltsupdate erhalten.
6. **Hoch: Umfang aus dem kantonalen Lehrplan ableiten.** Die Anzahl Module und Aufgaben dient nur der Produktionsplanung. Für die Freigabe zählen die abgedeckten Tätigkeiten, Denkwege und Grenzen.
7. **Mittel: Schweizreise auf Wahlfreiheit und Wiederaufnahme auslegen.** Diese Eigenschaften lassen sich prüfen. Die Aussage «Kinder kehren freiwillig zurück» bleibt unbestätigt.
8. **Tief: Zurückgestellt** sind Ferienautomatik, Avatar-Zubehör, iCloud-Sync und ClassKit. iCloud würde den Nachweis über den Verbleib von Kinderarbeiten erheblich verändern.

## 2. Agenten-Organisation
Fachrollen für die Produktion:
- Orchestrator
- Architekt
- mehrere iOS-Entwickler
- ML-Ingenieur
- Lehrplan-Analyst
- Inhaltsautoren pro Fach
- unabhängige Löser
- Didaktik-Kritiker pro Fach
- Sprachprüfer
- Design-Agent
- Audio-Agent
- Barrierefreiheits-Agent
- Test-Agenten
- Persona-Agenten
- Datenschutz- und Compliance-Agent
- Red-Team-Auditor

Ergänzt werden diese Zuständigkeiten:
- **Dauerhafte Aufgabensteuerung**: Der Orchestrator plant. Eine gewöhnliche Zustandsmaschine (kein Agent) speichert pro Aufgabe Abhängigkeiten, zuständigen Agenten, Frist, Versuchszahl und Ergebnis.
  - Nach einem Neustart übernimmt ein neuer Agent vom letzten bestätigten Zustand.
  - Abgelaufene Aufträge werden neu vergeben.
  - Merge, Publikation und Upload vertragen Wiederholungen.
- **Verantwortlicher für Nachweise**: Er verwaltet die Kette Lernziel → Quelle → Produktregel → Testfall → erlaubte Formulierung im Erwachsenenbericht. Ein CI-Lauf gilt nur als Beleg für die exakte Kombination aus Inhalts-, Modell-, Regel- und Buildversion.
- **Unabhängige Prüfgruppe**: Sie erstellt verdeckte Aufgaben, Gegenbeispiele und Handschriftfamilien in einem getrennten Zugriffsbereich. Produktagenten erhalten bei einem Fehler nur eine untersuchbare Fehlerklasse. Wird ein konkreter Prüffall zur Reparatur offengelegt, wandert er in die Regressionstests und wird im verdeckten Satz ersetzt.
- **Betriebs- und Wiederherstellungsagent**: Er prüft, ob die Arbeit tatsächlich vorankommt und ob CI-Jobs verschwunden sind. Er probt Runner-Ausfall, Modellwechsel, unterbrochenen Upload, Verlust eines Arbeitskontexts und die Wiederherstellung aus gesicherten Artefakten.
- **Release-Agent mit begrenztem Auftrag**: Er darf nur einen bereits geprüften Stand signieren, intern hochladen und den Apple-Status lesen. Signiermaterial steht weder Autoren noch PR-Jobs zur Verfügung.

Projektgedächtnis mit fünf getrennt versionierten Wahrheitsstufen:
1. verbindliche Projektgrenzen
2. fachliche Entscheidungen mit Quellen
3. offene Hypothesen
4. aktueller Arbeitszustand
5. unveränderte Prüfergebnisse

Agenten dürfen Hypothesen ergänzen. Zur Tatsache wird eine Hypothese erst mit passendem Nachweis. Jeder Agent liest beim Start nur den für seine Aufgabe gültigen Ausschnitt samt Version, nicht «alles».

Entscheidungsregeln:
- Das Gremium (Architekt, zuständiger Fach-Kritiker, Red-Team) stimmt nur über Produktentscheidungen ab. Ob eine Quelle eine Behauptung trägt, ein Recht vorliegt oder ein Test bestanden ist, entscheidet der Nachweis.
- Das Red-Team berichtet unabhängig und behält seine Befunde auch bei einer Gegenstimme.
- Gate-Änderungen gelten nur für künftige Kandidaten. Sie brauchen einen dokumentierten Grund und werden an früheren Fehlern gegengeprüft. Ein gescheiterter Kandidat wird nie rückwirkend grün.
- **Stillstand**: Nach zwei Reparaturversuchen derselben Fehlerursache verlangt die Steuerung eine andere Hypothese oder eine unabhängige Reproduktion. Bleibt der Nachweis aus, erhält die Aufgabe einen begründeten Blockierzustand, und unabhängige Arbeit läuft weiter. «Niemals auf Menschen warten» bedeutet weder endlose Wiederholung noch automatische Freigabe.
- **Öffentliche Repositories**: Verdeckte Prüfungen und Secrets liegen ausserhalb der öffentlichen Dateien und Logs. Ein einzelner geplanter GitHub-Workflow taugt nicht als alleiniger Wächter, weil GitHub solche Workflows in öffentlichen Repositories nach 60 Tagen ohne Aktivität deaktivieren kann.

## 3. Belegstatus mit zwei Achsen
Jede geprüfte Aussage speichert zwei unabhängige Angaben:
- **Prüfverfahren**: automatischer Test, Simulation, Simulator-Replay, Adapter-Replay oder physisches Gerät
- **Geltungsbereich**: synthetische Eingaben, bestimmte Geräteklasse, bestimmte Version

Der Erwachsenenbericht formuliert entsprechend, zum Beispiel: «Im Simulator mit synthetischen Fingerstrichen geprüft. Genauigkeit bei Kindern offen.» Im Kinderheft steht nur kindgerechter Text wie «Ich habe 16 gelesen. Stimmt das?», ohne Prüfetiketten.

## 4. Definition von «fertig» mit Gegenproben
Jede zentrale Zusage hat eine Gegenprobe, bei der eine zu grosszügige App durchfallen muss:
- **Ergebnis und Lösungsweg**: Zwei Durchläufe enden bei 15, nur einer enthält eine beobachtbare Zerlegung über die Zehn. Beide erhalten Anerkennung für das Ergebnis, nur beim passenden Durchlauf nennt der Bericht den Zehnerweg. Ein alternativer gültiger Weg wird akzeptiert.
- **Selbstständigkeit**: Derselbe Endzustand nach freiem Legen, nach einem visuellen Hinweis und nach einem vorgemachten Teilschritt ergibt drei verschiedene Berichte. Beim freien Erkunden lässt sich eine zwischenzeitlich ungünstige Anordnung folgenlos rückgängig machen.
- **Behalten und Transfer**:
  - Eine zeitversetzte Aufgabe in vertrauter Form prüft die Wiederaufnahme.
  - Eine neue Darstellung mit freier Strategiewahl prüft nahen Transfer.
  - Eine neue Zahl auf derselben Schablone belegt wenig über Transfer.
  - Der Bericht nennt Zeitpunkt, Darstellung und beobachtete Handlung.
- **Unverständliche Eingabe und Abbruch**: Unklares Zeichen, abgelehnte Kamera, stummes Gerät, Überspringen, Zeitablauf und Absturz haben je einen eigenen Verlauf. Keiner zählt als fachlicher Fehler oder als mangelnde Ausdauer.
- **Offene und soziale Kompetenzen**:
  - Ein Werkstück belegt eine Dokumentation, ein Selbstbericht eine Selbstauskunft.
  - Eine Einzelaufgabe belegt keine Zusammenarbeit.
  - Gültiger Endzustand ist dann «Teilbeitrag verfügbar, Kompetenz digital nicht ausreichend beobachtbar».
- **Zugänglichkeit**:
  - Der Prüfplan umfasst Ansichten und Zustände: Fehlermeldung, Nachfrage, leeres Profil, Wiederaufnahme.
  - Zentrale Wege werden per Antippen, VoiceOver, Tastatur und mit der Alternative zum Ziehen geprüft.
  - Apples Audit prüft nur den jeweils präsentierten Bildschirm. Die Bedienbarkeit für echte Kinder bleibt offen.
- **Korrektur nach Auslieferung**:
  - Eine absichtlich fehlerhafte Aufgabenfassung wird in der Folgeversion zurückgezogen.
  - Die App korrigiert nur die betroffenen Beobachtungen und berechnet abgeleitete Aussagen neu.
  - Ein offline gebliebenes Gerät behält seine alte Fassung, erkennbar im Versionsbericht.

Freigaberegel: Die App ist fertig, wenn sie
- für den gesamten vereinbarten Lehrplanumfang passende Lerngelegenheiten anbietet,
- für jede Leistungsrückmeldung den beobachteten Grund nennen kann
- und bei fehlender Evidenz zuverlässig eine engere Aussage wählt.

## 5. Handschrift
Synthetisch gut nachbildbar sind einzelne Formen, Bewegungsmerkmale und technische Fehler. Offen bleibt, wie häufig diese Merkmale bei echten Kindern zusammen auftreten. EMNIST liefert nur Zeichenbilder ohne zeitlichen Verlauf und ohne Fingerbedienung.

Der Aufbau des Labors:
1. **Familie A: Schreibweisen.** Mehrere unabhängig entworfene Ausgangsformen pro Zeichen:
   - offene und geschlossene Vier
   - Eins mit und ohne Aufstrich, Sieben mit und ohne Querstrich
   - alternative Strichreihenfolgen
   - Ziel: Nicht alle Generatoren verformen denselben Idealpfad.
2. **Familie B: Bewegung.** Ein neuromotorisches Modell (Kandidat: Sigma-Lognormal) erzeugt Beschleunigung, Abbremsen, Pausen, Nachkorrekturen und Absetzen. Eine Geräteschicht erzeugt fehlende oder zusammengefasste Abtastpunkte, Unterbrechungen und die unterschiedlichen Eigenschaften von Finger und Stift.
3. **Familie C: ganze Strichfolgen.** Ein gelerntes Modell, sofern Herkunft und Rechte des Trainingsmaterials passen. Lernt es nur von den Familien A und B, zählt es als Variante derselben Grundlage. Veröffentlichte Forschung darf die Konstruktion informieren.
4. **Verdeckte Abnahme mit unbekannten Konstruktionsprinzipien.** Entwicklung, Kalibrierung und Abnahme sind getrennt nach Pfadherkunft, Generator, Schreibstil und Gerätebedingungen.
   - Getestet werden auch ganze Antworten wie 15 und 51, Korrekturen und leere Eingaben.
   - Derselbe Strich muss bei Aufgaben mit verschiedener Musterlösung dieselben Lesarten erzeugen.
   - Rückfragen dürfen weder durch Auswahl noch durch Vorbelegung die Lösung verraten.
5. **Metrik gegen Ausweichverhalten.**
   - Die 90 % automatische Bewertbarkeit beziehen sich auf alle auswertbaren Testantworten vor jeder Nachfrage.
   - Bestätigung, Korrektur und Wechsel zum Ziffernblock werden separat gezählt.
   - Technisch falsch negative und falsch positive Bewertungen werden getrennt ausgewiesen, je verdeckter Familie und Eingabeart.
   - Für das Ziel von 0,5 % zählt die obere Grenze des 95-%-Vertrauensintervalls. Selbst bei null Fehlern braucht es dafür pro Testgruppe rund 598 unabhängige Fälle, und tausend Varianten desselben Grundstrichs sind nicht unabhängig.
6. **Drei technische Beweise getrennt.**
   - Adapter-Replay prüft die Erkennungskette.
   - XCUITest-Gesten prüfen die echte Oberfläche.
   - Messungen auf einem physischen iPad (Gerätefarm) prüfen Latenz und Geräteverhalten.
   - Ein Simulator-Replay belegt weder Handballenkontakt noch Pencil-Druck. Ohne Hardware bleibt genau das offen.
7. **Spiegelverkehrte Ziffern sind kein pauschaler Lernfehler.** Bei «Wie viele sind es?» kann das Mengenverständnis trotz Spiegelung stimmen, beim Lernziel «Ziffer richtig orientiert schreiben» zählt sie. Bei Mehrdeutigkeit fragt die App neutral nach.
8. **Erkennung ohne Kenntnis der Lösung**, durch die Modulabhängigkeiten technisch erzwungen. Der Ziffernblock ist immer erreichbar, die Handschriftbewertung lässt sich pro Profil abschalten.

## 6. Simulation von Lernenden
Drei Modelle werden getrennt simuliert:
- **Fachmodell**: Es löst Aufgaben mit einer bestimmten Strategie oder Fehlvorstellung.
- **Bedienmodell**: Es bedient die veröffentlichte Oberfläche und kennt weder Lösung noch Lernstandsmodell. Die Persona «kann nicht lesen» bekommt keine versteckten Test-IDs oder Beschriftungen als Ersatz fürs Lesen. Die VoiceOver-Persona bekommt genau den Zugang, den VoiceOver bietet.
- **Beobachtermodell**: Es prüft, welche Aussage die beobachteten Ereignisse tatsächlich tragen.

Bibliothek der Fehlvorstellungen, erste Version (jeweils Muster → Gegenprobe):
- **Zahlverständnis**: Eins-zu-eins-Zuordnung unsicher, letztes Zahlwort nicht als Anzahl verstanden → dieselben sieben Plättchen umordnen, erst zählen lassen, dann nach der Gesamtzahl fragen.
- **Stellenwert**: Zehner und Einer als einzelne Ziffern behandelt, leere Stelle verschwindet → 304 aus Material legen und ein anders angeordnetes Bündelbild lesen. Eine vertippte Null bleibt als alternative Erklärung möglich.
- **Gleichheitszeichen**: «=» als Aufforderung zum Ausrechnen gelesen → 8 + 4 = □ + 5 und eine Waage im Bild. Die Antwort 12 allein lässt keine eindeutige Deutung zu.
- **Brüche**: Ein grösserer Nenner wird als grössere Menge gedeutet → Drittel und Fünftel auf gleich langen Streifen vergleichen, dann die Grösse des Ganzen ändern.
- **Schriftspracherwerb**: Buchstabenname und Laut verwechselt, mehrgliedrige Grapheme einzeln gelesen, Raten anhand des Bilds → Laute zuordnen, ein unbekanntes Wort ohne verratendes Bild lesen, Hörverständnis separat prüfen. Eine richtige Bildwahl belegt keine Leseflüssigkeit.
- **NMG**: «Schwere Dinge sinken» als allgemeine Regel → Vorhersage festhalten, Beobachtung zeigen, eine überarbeitete Erklärung zulassen. Die Überarbeitung ist hier selbst Lernziel.
- **Informatik**: Eine Schleife über zwei Aktionen wird als Wiederholung jeder einzelnen Aktion gelesen → dreimal [Schritt, Drehung] mit «drei Schritte, drei Drehungen» vergleichen.

Der wertvollste simulierte Fall ist ein Paar mit gleichem sichtbaren Verhalten und verschiedener Ursache. Ein Kind zählt korrekt und vertippt sich, ein anderes verzählt sich und tippt genau, was es meint. Sind die Daten identisch, besteht die App nur mit offener Formulierung und passender Anschlussaufgabe. Eine sichere Diagnose wäre hier ein Fehler.

Zur Lernsteuerung:
- Ausgangspunkt ist eine einfache, erklärte Wiederholungsregel.
- FSRS, BKT oder IRT müssen sich gegen mehrere fremd entwickelte Lernmodelle bewähren: mit Vergessen, Raten, Abhängigkeit von der Darstellung und wechselnden Strategien.
- Bewertet werden zeitlich spätere Vorhersagen, falsche Zuschreibungen von Beherrschung und unnötige Wiederholungen.
- Die 80 % Erfolg sind ein einstellbarer Übungswert.

## 7. Lehrplan 21 und Schweiz
- **Lehrplanbezug von 8 + 7**: MA.1.C.1.b (Summe darstellen und nachvollziehen), MA.1.C.1.c (Rechenweg darstellen und nachvollziehen) und MA.1.A.3 (Stufe a: nichtzählendes Rechnen bis 20, Stufe b: Ergänzen zum nächsten Zehner). Ein einzelner beobachteter Weg deckt jeweils nur einen Ausschnitt ab.
- **Zyklus und Orientierungspunkt**: Zyklus 1 umfasst Kindergarten sowie 1. und 2. Klasse. Der Orientierungspunkt am Ende der 4. Klasse bezeichnet die verbindlich zu bearbeitenden Stufen. Einzelne Fachbereiche haben auch in Zyklus 2 keinen. Das Datenmodell unterscheidet deshalb «fachlich nicht vorgesehen» von «Quelle fehlt». Eigene Klassenempfehlungen sind als solche erkennbar.
- **Kantonsprofile**: Luzern hat Englisch ab der 3. und Französisch ab der 5. Klasse, der deutschsprachige Teil von Bern die umgekehrte Reihenfolge. Bei einem Wechsel wandern datierte Beobachtungen mit, und die Zuordnung zum neuen Profil wird neu berechnet. Eine beobachtete Französischleistung darf weder verschwinden noch auf Englisch übertragen werden.
- **Deutsch**: Hören, Sprechen, Lesen, Schreiben und «Sprache(n) im Fokus» sind sichtbar abgedeckt.
- **NMG**: zwölf Kompetenzbereiche in den Zyklen 1 und 2. Eine schöne Schulweg-Einheit ersetzt keine Abdeckung von Zeit, Wirtschaft oder Zusammenleben.
- **Medien und Informatik**: eigene Kompetenzbereiche plus Anwendungen über die Fächer hinweg.
- **BNE**: als fächerübergreifendes Thema geführt.
- **«Ohne Lesen lösbar»**: Navigation, Auftrag, Hilfe und Rückkehr müssen ohne selbstständiges Lesen verständlich sein. Beim Lernziel Lesen bleibt das zu lesende Wort geschützt. Wird es vorgelesen, ist das ein anderer Nachweis. Dasselbe gilt für Transkripte beim Hörverstehen und für automatische Korrektur im Diktat.
- **Zahlenschreibweise**: 1'000 ist Chnobels Hausstil, aber kein landesweit verbindliches Richtigkeitskriterium. Zahlenwert, Geldbetrag und ausdrücklich verlangte Schreibweise haben getrennte Bewertungsregeln.
- **Praktische und soziale Ziele**: Musik, Gestalten und Bewegung haben eigene Aufträge und Kriterien sowie eine Variante ohne Kamera oder Mikrofon. Die Matrix weist aus, welcher Teil mit einem Einzelgerät überhaupt beobachtbar ist. Aufträge, die Aufsicht erfordern, werden zu sicheren Beobachtungs- oder Planungsaufgaben mit entsprechend engerem Nachweis.
- **Rechte**: eigene Formulierungen, präzise Quellen, sparsame Referenzen.
  - Keine Logos.
  - Die offizielle Lehrplan-Schnittstelle ist keine Voraussetzung der Pipeline, weil sie an eine Geschäftsstelle verweist.
  - Das Rechteverzeichnis umfasst auch Stimmen, Schriften, Karten, Modelle und Audiodateien.

## 8. Lernerlebnis und Schweizreise
- **Wahlfreiheit**: Die Reise hängt am Lernhandeln. Ein Kind findet zwei gleichwertige Wege nach Luzern und wählt selbst, welchen es ins Reisebuch übernimmt. Ein anderes hört den Auftrag dreimal, nutzt Hilfe und erreicht denselben Ort.
- **Abnahme**: Beide Wege stehen offen, eine Runde lässt sich beenden, und nach einer Woche findet das Kind genau seine Seite wieder.
- **Ältere Kinder**: Fahrpläne, Karten und eigene Entscheidungen tragen die Geschichte. Gemessen wird erreichbare Wahlfreiheit. Ob Kinder die Reise mögen, bleibt offen.
- **Keine Manipulation**: keine Werbung, keine Lootboxen, keine In-App-Käufe, keine Serien mit Verlustangst, Pausen ohne Folgen.
- **Barrierefreiheit** in jedem Aufgabentyp: Antippen statt Ziehen, Form oder Muster zusätzlich zur Farbe, visuelle Alternative zu Audio, VoiceOver, Schaltersteuerung, Tastatur, Bedienung für Linkshänder.

## 9. Technik, Datenschutz und Betrieb
- **Plattform**: SwiftUI, Swift 6, Observation und SwiftData. iPadOS ist die Referenz.
- **Pakete**: CoreDomain, CurriculumKit, TaskEngine, InputKit, RecognitionKit, LearningEngine, MotivationKit, VoiceKit, ContentPacks, LearnerSim und Feature-Module pro Fach.
- **Beobachtungsprotokoll**: ein versioniertes Ereignisprotokoll zwischen TaskEngine und LearningEngine, zum Beispiel «Eingabe korrigiert → Ergebnis bestätigt → Materialhandlung ohne Fachhilfe beobachtet».
  - Wiederholte Ereignisse, rückgängig gemachte Bewegungen und abgebrochene Aufgaben werden eindeutig verarbeitet.
  - Nach einem Update lassen sich fachlich falsche Wertungen neu berechnen.
  - Rohhandschrift kann nach einer Aufbewahrungsregel gelöscht werden, ohne dass der Entscheidungsweg verloren geht.
  - Eine Profillöschung erfasst alle zugehörigen Beobachtungen und Anhänge.
- **Offline-Garantie**: Getestet wird mit frischer Installation und gesperrtem Netz, ohne heruntergeladene Zusatzstimme, ohne Mikrofonrecht und mit deaktivierter Spracherkennung.
  - Für wesentliche Aufträge gibt es einen mitgelieferten, rechtlich geklärten Audioweg.
  - Lokale Spracherkennung kommt nur zum Einsatz, wenn sie für die konkrete Konfiguration unterstützt ist.
- **Datenfluss**: Geprüft werden SwiftData-Dateien, Anhänge, Vorschaubilder, Backups, Export, Logs und Testberichte.
  - Foto und Stimme sind optional, der Exportumfang ist ausdrücklich definiert.
  - In CI und TestFlight gibt es nur synthetische Profile.
  - TestFlight erhebt eigene Diagnosedaten, und ein Privacy Manifest allein belegt die Datenschutzzusage nicht.
- **Recht**: DSG, räumliche Anwendbarkeit der DSGVO und die Kids-Guidelines sind getrennte Prüffragen. Der Bericht dokumentiert Prüfung und Restrisiken. Ungeklärte Assets werden ersetzt oder weggelassen.
- **Release**: Der Release-Agent prüft Build-ID, Versionsnummer, Verarbeitungszustand, Verteilungsart «TestFlight Internal Only», Export-Compliance und Ablaufdatum (interne Builds sind 90 Tage testbar).
  - Ziel ist ein intern testbereiter Build, zum Beispiel mit dem Status READY_FOR_BETA_TESTING.
  - Bei langsamer Verarbeitung prüft er den Status in wachsenden Abständen und sucht vor jedem erneuten Upload nach derselben Buildnummer.
  - Technisch behebbare Fehler werden repariert. Verschlüsselungsangaben leitet er aus dem tatsächlichen Binary ab.
  - Eine nötige Aktion des Kontoinhabers endet als «extern blockiert».

## 10. Roadmap
- **Phase 0: Betriebsfähigkeit und Apple-Durchstich**
  - Inhalt: Agentenrechte, Zustandsmaschine, Neustartverfahren, getrennter Prüfbereich, minimale iPad-App.
  - Kriterium: Ein Agent setzt einen unterbrochenen Auftrag fort. Ein signierter Minimalbuild erreicht den internen TestFlight-Zielzustand.
- **Phase 1: drei vollständige Lehrproben**
  - Inhalt: 8 + 7 mit freiem Weg, eine Laut- und Leseaufgabe, ein praktischer Auftrag mit optionaler Dokumentation.
  - Kriterium: Alternativlösung, Fehllesung, verratender Hinweis, fehlende Berechtigung und unzureichender Nachweis ergeben jeweils die vorgesehenen Aussagen.
- **Phase 2: Handschrift und Bedienung**
  - Inhalt: unabhängige Generatoren, verdeckte Abnahme, Fingerbedienung, Ziffernblock, zugängliche Alternativen.
  - Kriterium: Fehler- und Abdeckungsgrenzen pro Testgruppe bestanden. Simulator-, Adapter- und Hardwarebelege sind getrennt ausgewiesen.
- **Phase 3: Planungsmatrix Luzern und Bern**
  - Inhalt: Quellenstände, Kompetenzstufen, Nachweisformen und erlaubte Berichtsaussagen, erste Inhalte Mathematik und Deutsch für die 1.–2. Klasse.
  - Kriterium: Jede Kompetenz hat einen zulässigen Nachweis oder eine erklärte Beobachtungsgrenze. Ein Profilwechsel erhält die Beobachtungen.
- **Phase 4: Ausbau nach Nachweisformen**
  - Inhalt: 3.–6. Klasse, Fremdsprachen, NMG, Medien und Informatik, Gestalten, Musik, Bewegung und Sport.
  - Kriterium: Pro Fach funktionieren ein typischer Lernweg, ein Grenzfall und ein alternativer Zugangsweg, bevor die breite Produktion beginnt.
- **Phase 5: breite Inhaltsproduktion**
  - Inhalt: Aufgabenfamilien, Hilfen, Gegenbeispiele, Behalten und Transfer für den ganzen Umfang.
  - Kriterium: Verdeckte Stichproben je Fach, Zyklus und Nachweisform bestehen. Doppelte Familien erhöhen die Abdeckung nicht.
- **Phase 6: unabhängige Schlussabnahme**
  - Inhalt: eingefrorener Kandidat, neue verdeckte Aufgaben, Tests zu Offline, Migration, Löschung und Wiederherstellung, vollständige Evidenzbilanz.
  - Kriterium: keine offenen kritischen oder hohen Befunde. Offene Aussagen über reale Kinder bleiben sichtbar. Der Bericht gilt für genau einen Kandidaten.
- **Phase 7: finaler interner TestFlight-Build**
  - Inhalt: Der geprüfte Kandidat wird signiert, verarbeitet und intern testbereit gemacht.
  - Kriterium: Build-ID, Commit, Inhalts- und Modellversion, Apple-Status und Ablaufdatum stimmen überein. Erst dann meldet der Orchestrator das Projektziel als erreicht.

## 11. Bleibt ohne reale Personen offen
- die Genauigkeit der Handschrifterkennung bei Kindern
- die Verständlichkeit für Sechsjährige
- Motivation und freiwillige Rückkehr
- die Lernwirksamkeit
- Fairness über verschiedene Gruppen von Kindern
- die Feinheiten des Schweizer Sprachgebrauchs aus menschlicher Sicht
- Hardware-Verhalten, sofern kein physisches Gerät angebunden ist

# Meine Frage an dich

Der Plan ist inzwischen weit ausgearbeitet. Prüfe ihn als Abnahmekommission aus einer Schweizer Primarlehrperson, einer Lernforscherin, einem Senior-iOS-Architekten, einer ML-Ingenieurin für Handschrift, einem Game-Designer für Kinder und einem Experten für autonome Multi-Agenten-Systeme. Wie lässt er sich perfektionieren? Weiterhin gilt: nur KI-Agenten, kein Mensch nach dem Startpaket, Kosten und Zeit spielen keine Rolle.

1. Wo kann das System alle Gates formal bestehen und trotzdem inhaltlich versagen? Nenne die gefährlichsten verbleibenden Schlupflöcher und wie man sie schliesst.
2. Spezifiziere die drei Kernartefakte so konkret, dass Agenten sie direkt umsetzen können:
   - das Schema einer Beweisregel (Felder, Beispiel für 8 + 7)
   - die Ereignistypen des Beobachtungsprotokolls
   - das Datenmodell des zweiachsigen Belegstatus
3. Welche Gegenproben fehlen noch im Abnahmekatalog, je Fach und je Nachweisform?
4. Was muss in Phase 0 konkret entstehen (Verzeichnisstruktur, Zustandsmaschine, Rechtekonzept, CI-Workflows, Release-Pipeline), damit die Agenten ab Tag 1 zuverlässig und wiederaufnehmbar arbeiten?
5. Welche Punkte des Plans sind überspezifiziert oder widersprüchlich und sollten vereinfacht oder gestrichen werden?

Antworte mit einer priorisierten Liste (Wirkung hoch/mittel/tief), den konkreten Spezifikationen aus Frage 2 und einer bereinigten, umsetzungsbereiten Fassung von Phase 0. Schlage keine Massnahmen vor, die Menschen erfordern, ausser im einmaligen Startpaket.
