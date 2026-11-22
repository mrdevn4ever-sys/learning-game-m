# Kontext und Idee

Ich plane eine native Lern-App in Swift für Kinder der 1. bis 6. Klasse in der Schweiz (Arbeitstitel «Chnobel»). Ziel ist das beste Lernwerkzeug für die Primarstufe: vollständig am Lehrplan 21 ausgerichtet, alle Schulfächer, adaptiv, spielerisch und werbefrei.

Die Steuerung soll so intuitiv sein wie bei «Dr. Kawashimas Gehirnjogging». Kinder schreiben Antworten von Hand (Ziffern, Buchstaben, Wörter, Formen) mit Finger oder Apple Pencil. In den Einstellungen lässt sich auf Tastatur, Ziffernblock oder Antwortauswahl umschalten. Die Module werden schrittweise schwieriger, nach jedem Modul gibt es einen Test, dazu Kapitel- und Jahrestests. Zeit und Kosten spielen keine Rolle, es zählt nur die Qualität.

# Detaillierter Plan

## 1. Plattform und Technik
- SwiftUI und Swift 6 (strict concurrency). Hauptplattform ist iPadOS wegen des Apple Pencil, dazu iPhone und macOS. Mindestversion iOS/iPadOS 18.
- Persistenz mit SwiftData, lokal zuerst. Optionaler Sync über CloudKit (private Datenbank der Familie).
- State-Management mit dem Observation-Framework (@Observable) und unidirektionalem Datenfluss.
- Modulare Architektur als Swift Packages:
  - **CoreDomain**: Fach, Kompetenz, Modul, Lektion, Aufgabe, Lernstand
  - **CurriculumKit**: Kompetenzbaum nach Lehrplan 21, Konfiguration pro Kanton
  - **TaskEngine**: Aufgabentypen, Generatoren, Bewertung, Fehleranalyse
  - **InputKit**: Handschrift-Canvas, Tastatur, Ziffernblock, Auswahl, Drag & Drop, Sprache
  - **RecognitionKit**: Core-ML-Modelle und Vision
  - **LearningEngine**: Adaptivität, Spaced Repetition, Mastery
  - **MotivationKit**: Belohnungen, Spielwelt, Avatar
  - **VoiceKit**: Vorlesen (TTS) und Audioaufnahmen
  - **ContentPacks**: versionierte Inhaltspakete (JSON und Assets)
  - **Feature-Module** pro Fach (UI)
- Tests: Swift Testing, Snapshot- und UI-Tests, automatische Prüfung aller Inhalte, eigene Evaluationsdatensätze für die ML-Modelle. CI über Xcode Cloud oder GitHub Actions (macOS).

## 2. Eingabe (Kernerlebnis)
- Handschrift auf einem PencilKit-Canvas (Finger und Pencil), mit Kästchen pro Ziffer wie im Schulheft und zusätzlich einem freien Schreibfeld.
- Erkennung von Ziffern, Operatoren und Buchstaben durch ein eigenes Core-ML-Modell, komplett auf dem Gerät und mit weniger als 20 ms Latenz. Trainiert wird mit EMNIST und einem eigenen Datensatz echter Kinderhandschrift aus Schweizer Schulen (mit Einwilligung). Der Datensatz deckt Schweizer Eigenheiten ab: «1» mit Aufstrich, «7» mit Querstrich, Basisschrift Schweiz oder Schnürlischrift je nach Kanton.
- Wörter und Sätze erkennt Vision (VNRecognizeTextRequest, Deutsch), mit einer Toleranzlogik: Gross- und Kleinschreibung wird nur bewertet, wenn sie Lernziel ist.
- Beim Schreibenlernen werden die Striche analysiert (Richtung, Reihenfolge, Proportionen) und mit Referenzpfaden verglichen.
- Ist die Erkennung unsicher, fragt die App nach («Meintest du 7?»), statt die Antwort falsch zu werten.
- Einstellungen: Eingabemodus global und pro Fach wählbar (Handschrift, Tastatur, Ziffernblock, Auswahl, Sprache), Linkshänder-Modus, Hardware-Tastatur, Unterstützung für Schaltersteuerung und VoiceOver.
- Spracheingabe mit dem Speech-Framework (de-CH, auf dem Gerät) für Leseflüssigkeit und Aussprache in den Fremdsprachen, optional.

## 3. Curriculum (Lehrplan 21)
- Hierarchie: Fach → Kompetenzbereich → Kompetenz (Lehrplan-21-Code, z.B. MA.1.A.2) → Modul → Lektion → Aufgabe.
- Zyklus 1 umfasst Kindergarten bis 2. Klasse, Zyklus 2 die 3. bis 6. Klasse. Jeweils mit Grundansprüchen und erweiterten Ansprüchen.
- Beim Start wird der Kanton gewählt. Er bestimmt:
  - die Reihenfolge der Fremdsprachen: in den Passepartout-Kantonen (BE, BL, BS, SO, FR, VS) Französisch ab der 3. und Englisch ab der 5. Klasse, in den meisten anderen Deutschschweizer Kantonen Englisch ab der 3. und Französisch ab der 5. Klasse, Sonderfälle wie Graubünden mit Italienisch oder Rätoromanisch
  - die Schulschrift
  - die Fachbezeichnungen und die Schulferien
- Fächer und Inhalte:
  - **Mathematik**:
    - Zahl und Variable: Zahlenraum 20 → 100 → 1000 → 1 Million, Einmaleins, schriftliche Verfahren, Brüche, Dezimalzahlen, Teilbarkeit
    - Form und Raum: Geometrie, Spiegeln, Körper, Netze, Simulation von Geodreieck und Zirkel
    - Grössen, Funktionen, Daten: Franken und Rappen, Längen, Gewichte, Zeit, Uhr, Massstab, Diagramme, Proportionalität, Kombinatorik
    - dazu Kopfrechnen-Sprints und Schweizer Schreibweisen (1'000, Fr. 3.50)
  - **Deutsch**:
    - Hören, Lesen (Leseflüssigkeit, Leseverständnis), Sprechen
    - Schreiben: Buchstaben, Schulschrift, Diktate mit Audio
    - Sprache(n) im Fokus: Wortarten, Fälle, Zeitformen, Rechtschreibung nach Schweizer Regeln (kein ß)
    - Literatur, Unterschied Mundart und Standardsprache
  - **Fremdsprachen** (Französisch, Englisch): Wortschatz, Hörverstehen, Aussprache, Lesen, Schreiben, Bezug zur Romandie
  - **NMG** (Natur, Mensch, Gesellschaft):
    - Natur und Technik: Tiere, Pflanzen, Körper, Wetter, Stoffe, Energie, Technik
    - Zeit und Geschichte: Schweizer Geschichte, altersgerecht
    - Räume: Kantone, Hauptorte, Flüsse, Seen, Pässe, Karten lesen
    - Wirtschaft, Konsum, Ethik, Religionen
    - Gemeinschaft: Gemeinde, Kanton, Bund, direkte Demokratie
  - **Medien und Informatik**: Algorithmen mit Blockprogrammierung, Datenstrukturen, Medienkompetenz, Sicherheit im Netz
  - **Musik**: Rhythmus, Gehörbildung, Notenlesen, Schweizer Lieder
  - **Bildnerisches, Textiles und Technisches Gestalten**: Farbenlehre, Formen, Zeichenaufgaben auf dem Canvas, Bildbetrachtung
  - **Bewegung und Sport**: Theorie, Bewegungspausen, Verkehrserziehung (Velo, Verkehrsregeln Schweiz)
  - **Fächerübergreifend**: Lernstrategien, Konzentrations- und Gedächtnistraining
- Ziel für den Umfang: über 400 Module, über 15'000 von Hand kuratierte Aufgaben, dazu unbegrenzt generierte Aufgaben (vor allem in Mathematik, Rechtschreibung und Wortschatz).

## 4. Aufgaben-Engine
- Rund 40 generische Aufgabentypen, zum Beispiel: Eingabe, Auswahl, Zuordnen, Sortieren, Lückentext, Zahlenstrahl, Hunderterfeld, Stellenwerttafel, Uhr stellen, Geld legen, Ort auf der Karte antippen, Diktat, Zeichnen und Konstruieren, Rhythmus klopfen, Blockprogrammierung.
- Inhalte sind Daten nach einem JSON-Schema, nicht Code. So können Autorenteams unabhängig von der Entwicklung arbeiten.
- Parametrische Generatoren mit Bedingungen, z.B. «Addition mit Zehnerübergang im Zahlenraum 100».
- Fehleranalyse erkennt typische Fehlermuster (vertauschte Stellenwerte, vergessener Zehnerübergang, fehlende Doppelkonsonanten) und löst gezielte Förderaufgaben und Erklärungen aus.
- Hilfen in Stufen: Hinweis → Teilschritt → animierter Lösungsweg.

## 5. Lernlogik und Schwierigkeit
- Wissensmodell pro Kompetenz (Bayesian Knowledge Tracing oder Elo/IRT). Angestrebt wird eine Erfolgsquote von rund 80 %.
- Mastery Learning: Ein Modul gilt erst als gemeistert, wenn die Leistung über mehrere Sitzungen stabil ist.
- Spaced Repetition (FSRS) für Faktenwissen wie Einmaleins, Wörter und Hauptorte.
- Gemischtes Üben (Interleaving) und tägliche Mischrunden.
- Einstufungstest beim Start. Der Lernpfad passt sich an, auch über Klassenstufen hinweg (überspringen oder nachholen).
- Tests auf vier Ebenen: kurzer Check nach jeder Lektion, Modultest nach jedem Modul, Kapiteltest pro Kompetenzbereich, Semester- oder Jahrestest pro Fach. Ergebnisse als Kompetenzstufen, optional auch auf der Schweizer Notenskala 1–6.

## 6. Spiel und Motivation
- Tagestraining in der Art von Gehirnjogging (5–10 Minuten) mit Kopfrechnen, Lesen und Gedächtnis. Dazu ein persönlicher «Fitness-Wert» mit Verlauf, als eigenes Konzept ohne fremde Marken oder Begriffe.
- Rahmenwelt ist eine Reise durch die Schweiz: Regionen und Kantone werden freigeschaltet, dazu gibt es Sammelobjekte (Tiere, Wahrzeichen, Fakten).
- Avatar, Abzeichen pro Kompetenz und Serien ohne Druck (Pausentage sind erlaubt).
- Keine Werbung, keine Lootboxen, keine In-App-Käufe für Kinder, keine manipulativen Muster. Eltern können Zeitlimiten setzen.
- Hochwertige Illustrationen, Animationen und Sounds. Vorlesen mit Schweizer Sprecherinnen und Sprechern (Hochdeutsch mit Schweizer Färbung).

## 7. Rollen
- **Kind**: mehrere Profile pro Gerät, Anmeldung per Bild statt Passwort.
- **Eltern**: geschützter Bereich mit Fortschritt, Einstellungen und Zeitlimiten.
- **Lehrperson** (später): Klassen verwalten, Aufgaben zuweisen, Auswertungen. Integration mit Apple School Manager, Schoolwork und Shared iPad.

## 8. Barrierefreiheit und Inklusion
- VoiceOver, Dynamic Type, Vorlesefunktion für jeden Text.
- Legasthenie-freundliche Schrift, Modus für Farbschwäche, reduzierte Animationen.
- Förderpfad bei Dyskalkulie.
- Unterstützung für Deutsch als Zweitsprache (DaZ) mit Bildwörterbuch.

## 9. Datenschutz und Recht
- Einhaltung von Schweizer DSG und DSGVO sowie der Regeln der Apple Kids Category.
- Daten bleiben auf dem Gerät, es gibt keine Tracker von Drittanbietern. Sync nur über die iCloud der Familie.
- Ein allfälliger Server für den Lehrermodus wird in der Schweiz gehostet. Die Eltern geben ihre Einwilligung.
- Keine Inhalte aus Lehrmitteln kopieren (Urheberrecht). Alle Inhalte werden selbst erstellt und an den Kompetenzen ausgerichtet.

## 10. Qualitätssicherung der Inhalte
- Ein Fachdidaktik-Team pro Fach (Lehrpersonen, Dozierende der Pädagogischen Hochschulen) mit Vier-Augen-Prinzip.
- Automatische Prüfung aller Inhalte.
- Pilotklassen und anonyme A/B-Tests.
- Wirksamkeitsstudie zusammen mit einer Pädagogischen Hochschule.

## 11. Roadmap und Team
- **Phase 0** (Monat 1–3): Architektur, Design-System, Prototyp der Handschrifterkennung, Start der Datensammlung, Schema für die Inhalte.
- **Phase 1** (Monat 4–9): Mathematik 1.–2. Klasse komplett, Tagestraining, Profile, Elternbereich, danach Pilot in Schulklassen.
- **Phase 2** (Monat 10–15): Deutsch 1.–2. Klasse, Mathematik 3.–4. Klasse, verfeinerte Lernlogik.
- **Phase 3** (Monat 16–24): Mathematik und Deutsch bis zur 6. Klasse, NMG, Fremdsprachen.
- **Phase 4** (Monat 25–30): Medien und Informatik, Musik, Gestalten, Sporttheorie, Lehrermodus.
- **Phase 5** (ab Monat 30): Romandie (PER, französische Oberfläche), Tessin (Italienisch), Rätoromanisch, Prüfung von Android und Web.
- Ideales Team: 3–4 iOS-Entwickler, 1 ML-Ingenieur, 1 Game- und UX-Designer, 2 Illustratoren oder Animatoren, Sounddesign, 6–10 Fachdidaktikerinnen und Fachdidaktiker, Sprecherinnen und Sprecher, QA, Datenschutzberatung.

# Meine Frage an dich

Wie kann dieser Plan perfektioniert werden, wenn Kosten, Aufwand und Zeit keine Rolle spielen? Bitte beurteile ihn kritisch als Team aus erfahrener Primarlehrperson in der Schweiz, Fachdidaktiker, Lernforscherin, Senior-iOS-Architekt, ML-Ingenieurin für Handschrifterkennung und Game-Designer für Kinderspiele. Konkret:

1. Was fehlt, ist falsch oder ist für die Schweiz und den Lehrplan 21 ungenau?
2. Welche technischen Entscheidungen sind riskant, und was wäre besser (insbesondere die Handschrifterkennung bei 6- bis 8-Jährigen)?
3. Welche Erkenntnisse der Lernforschung sollten zusätzlich in die Lernlogik und die Tests einfliessen?
4. Wie organisiert man die Produktion von Tausenden hochwertigen Aufgaben pro Fach, ohne dass die Qualität leidet?
5. Wie bringt man Kinder dazu, gerne und regelmässig zu lernen, ohne manipulative Mechaniken?
6. Was würde die App von allen bestehenden Lern-Apps klar abheben?

Antworte mit einer priorisierten Liste konkreter Verbesserungen (Wirkung hoch/mittel/tief) und den grössten Risiken samt Gegenmassnahmen. Schliesse mit einer überarbeiteten Roadmap ab.
