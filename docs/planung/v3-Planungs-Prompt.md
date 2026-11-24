# Kontext und Idee

«Chnobel» ist eine native Lern-App in Swift für die 1. bis 6. Primarklasse in der Deutschschweiz. Chnobel ist ein digitales Arbeitsheft, in dem Kinder ihren Denkweg zeigen. Sie schreiben Antworten von Hand wie im Heft (Finger oder Apple Pencil) und legen Material wie Plättchen, Münzen oder Zeiger. Alternativ arbeiten sie per Ziffernblock, Tastatur oder Antwortauswahl, umschaltbar in den Einstellungen. Eine Reise durch die Schweiz gibt den Kindern einen Grund, das Heft gerne zu öffnen. Der eigentliche Wert liegt in der Rückmeldung: Chnobel erkennt, was beim nächsten Schritt hilft, und weiss, wann es zu wenig weiss, um eine Leistung zu beurteilen.

Der erste Qualitätsmassstab ist dieser Ablauf: Eine Erstklässlerin soll 8 + 7 so legen, dass man das Ergebnis gut sieht. Sie schiebt zwei Plättchen zur Acht, legt fünf daneben und schreibt 15. Liest die App ihre Fünf als Sechs, kann das Kind die Eingabe berichtigen. Einige Tage später kommt 9 + 5 in einer anderen Darstellung. Erst wenn auch das gelingt, gilt die Strategie «zur Zehn ergänzen» als selbstständig angewendet (Bezug Lehrplan 21: MA.1.C.1, Stufen b und c).

Zeit und Kosten spielen keine Rolle. Es gilt aber eine harte Randbedingung.

# Grundsatz: Die KI-Agenten erledigen alles

Eine Organisation aus KI-Agenten erledigt das gesamte Projekt autonom, von der Lehrplananalyse bis zum fertigen Build in TestFlight: Planung, Architektur, Code, Inhalte, Grafik, Audio, Tests, Prüfung, Freigabe und Upload. Kein Mensch arbeitet mit. Das gilt auch für mich als Auftraggeber: Ich prüfe nichts, gebe nichts frei und entscheide nichts.

Ausgeschlossen sind:
- Kinder, Eltern, Lehrpersonen und Schulen
- Hochschulen, Fachpersonen, Sprecher, Illustratoren, Juristen und Tester
- Datenerhebungen über Personen
- eigene Server
- öffentliche Verteilung

Was sich nur mit realen Personen belegen lässt, behauptet die App nicht, sondern führt es als «unbestätigt». Vorsichtige Voreinstellungen gleichen diese Lücke aus.

Einmalige technische Voraussetzungen, die vor dem Start bereitstehen müssen, weil Agenten sie nicht selbst anlegen können:
- ein Apple-Developer-Konto
- ein App-Store-Connect-API-Schlüssel als hinterlegtes Secret
- ein Git-Repository
- macOS-Build-Umgebungen mit Xcode (z.B. macOS-CI-Runner oder Xcode Cloud)

Danach greift kein Mensch mehr ein.

# Detaillierter Plan

## 1. Die Agenten-Organisation
Rollen, jeweils mit eigenem Kontext, eigenen Rechten und eigenem Auftrag:
- **Orchestrator**: Er zerlegt die Roadmap in Aufgaben, vergibt sie, verfolgt den Fortschritt und eskaliert Konflikte an das Entscheidungsgremium. Er schreibt keinen Produktcode.
- **Architekt**: Er verantwortet Modulgrenzen, Schnittstellen und Architekturentscheidungen (ADRs). Er hat ein Vetorecht bei Verletzungen der Architektur.
- **iOS-Entwickler** (mehrere, parallel in getrennten Branches): Sie setzen Feature-Module, InputKit, TaskEngine, LearningEngine und so weiter um.
- **ML-Ingenieur**: Er entwickelt Handschriftgenerator, Modelle, Evaluierung und Core-ML-Export.
- **Lehrplan-Analyst**: Er erstellt die Kompetenzmatrix aus öffentlichen Quellen und dokumentiert Kantonsprofile mit Quelle und Datum.
- **Inhaltsautoren** (pro Fach): Sie schreiben Lernziele, Aufgabenfamilien, Hilfen und Generatoren.
- **Unabhängige Löser**: Sie lösen Aufgaben ohne Lösungsschlüssel und mit anderem Modell oder Kontext.
- **Didaktik-Kritiker** (pro Fach): Sie prüfen fachliche Richtigkeit, Lehrplanbezug und Fehlvorstellungen.
- **Sprachprüfer**: Er prüft Schweizer Standarddeutsch (kein ß, Apostroph bei Tausendern, Schweizer Begriffe), Französisch und Englisch.
- **Design-Agent**: Er verantwortet Design-System, prozedurale Grafik (SwiftUI Canvas und Shapes, SF Symbols, eigene Vektorgrafiken), Animationen und die Referenzpfade für die Handschrift.
- **Audio-Agent**: Er erzeugt Sprachausgaben mit Systemstimmen oder vorab berechneten Sprachdateien, pflegt das Aussprache-Lexikon für Schweizer Begriffe und erstellt synthetische Klänge.
- **Barrierefreiheits-Agent**: Er führt Audits zu VoiceOver, Schaltersteuerung, Dynamic Type, Kontrast und Zielgrössen durch.
- **Test-Agenten**: Sie schreiben und betreiben Unit-, UI-, Snapshot- und Inhaltstests sowie Mutationstests.
- **Persona-Agenten**: Sie bedienen die App als simulierte Kinder über UI-Automation.
- **Datenschutz- und Compliance-Agent**: Er prüft gegen Schweizer DSG, DSGVO, die App Review Guidelines (Kids Category) und das Rechteverzeichnis aller Inhalte.
- **Red-Team-Auditor**: Er sucht aktiv nach Fehlern, Schönfärberei und Behauptungen ohne Beleg. Er ist an keinem Produktartefakt beteiligt.
- **Release-Agent**: Er übernimmt Versionierung, Signierung, Archivierung und den Upload nach TestFlight über die App Store Connect API.

Spielregeln:
- **Vier-Augen-Prinzip zwischen Agenten**: Kein Artefakt wird von dem Agenten freigegeben, der es erstellt hat. Kritische Prüfungen laufen mit einem anderen Modell oder einer anderen Konfiguration, damit nicht alle dieselben blinden Flecken haben.
- **Deterministische Prüfungen haben Vorrang**: Wo ein Validator, Test oder Audit etwas prüfen kann, entscheidet nicht das Urteil eines Agenten.
- **Entscheidungsgremium**: Architekt, zuständiger Fach-Kritiker und Red-Team entscheiden per Mehrheit. Jede Entscheidung kommt mit Begründung und Alternativen in ein Entscheidungslog (ADR). Bei Patt gilt die vorsichtigere, besser umkehrbare Option.
- **Niemals auf Menschen warten**: Fehlt eine Information, wählt das Gremium einen vorsichtigen Standard, dokumentiert ihn und führt ihn als offenen Punkt.
- **Projektgedächtnis im Repository**: Roadmap, ADRs, Abdeckungsmatrix, Register bekannter Schwächen, Register offener Nachweise und Qualitätsberichte liegen versioniert im Repository. Jeder Agent liest sie, bevor er arbeitet.
- **Arbeitsfluss**: Aufgabe → Branch → Umsetzung → automatische Gates in der CI → Review durch einen fremden Agenten → Merge. Rote Gates blockieren den Merge immer.
- **Schutz gegen Selbsttäuschung**: Agenten dürfen Tests, Schwellenwerte oder Prüfregeln nicht abschwächen, um ein Gate grün zu machen. Jede Änderung an Gates braucht das Gremium und einen Eintrag im Log.

## 2. Prioritäten
1. **Hoch**: Technische Erkennung und fachliche Bewertung trennen. Unleserliches Zeichen, App-Fehler, übersprungene Aufgabe und fachlicher Fehler werden unterschiedlich erfasst.
2. **Hoch**: Für jede Kompetenzstufe festlegen, woran man sie erkennt: Antwort, dargestellter Lösungsweg, Werkstück (Foto oder Aufnahme im Reisebuch) oder Selbsteinschätzung des Kindes.
3. **Hoch**: Ein erster vollständiger Lernweg, den ein simuliertes Kind ohne Lesekenntnisse und ohne Hilfe eines Erwachsenen bedienen kann, mit dem Finger auf einem gewöhnlichen iPad.
4. **Hoch**: Den kantonalen Lehrplan versionieren. Kanton, Schulsprache, Klassenstufe, Grundanspruch, Orientierungspunkt und die empfohlene Reihenfolge werden getrennt geführt.
5. **Hoch**: Verzögertes Behalten und Transfer prüfen.
6. **Hoch**: Eine robuste Agenten-Organisation mit harten automatischen Gates.
7. **Hoch**: Ehrliche Kennzeichnung. Jede Aussage trägt den Status «automatisch geprüft», «simuliert» oder «unbestätigt».
8. **Mittel**: Praktische Aufträge ausserhalb des Bildschirms für NMG, Gestalten, Musik und Bewegung.
9. **Mittel**: Die Schweizreise für zwei Altersgruppen gestalten, gesprochen und ruhig für die 1.–3. Klasse, eigenständiger für die 4.–6. Klasse.
10. **Tief**: Ferienautomatik, Avatar-Zubehör und Zusatzanimationen.

## 3. Lehrplan 21 und Schweizer Schulrealität
- Zielgruppe ist die 1. bis 6. Klasse in der Deutschschweiz. Für den Einstieg gibt es Aufgaben auf Kindergartenniveau, ohne das Kind sichtbar zurückzustufen.
- Die kleinste Referenz ist die Kompetenzstufe. Pro Lernziel werden gespeichert:
  - die kantonale Fassung
  - Fach, Kompetenzbereich und Handlungs- oder Themenaspekt
  - Kompetenzcode und Stufe
  - Grundanspruch und Orientierungspunkt (am Ende der 4. Klasse, für Zyklus 1 gibt es keine)
  - davon getrennt die eigenen Lektionen und Klassenempfehlungen
- Lehrplantexte werden nicht im Wortlaut übernommen, sondern nur Codes und eigene Formulierungen.
- Luzern ist der Referenzkanton (Englisch ab der 3., Französisch ab der 5. Klasse). Das zweite Profil ist Bern, wo die Sprachfolge umgekehrt ist. Graubünden folgt später mit Profilen nach Schulsprache und Region. Bei einem Kantonswechsel bleibt der Lernstand erhalten. Die Romandie (PER) und das Tessin (Piano di studio) kommen erst spät.

Die Fächer:
- **Mathematik**: drei Kompetenzbereiche: Zahl und Variable, Form und Raum sowie Grössen, Funktionen, Daten und Zufall. Dazu die Handlungsaspekte Operieren und Benennen, Erforschen und Argumentieren, Mathematisieren und Darstellen. Bei Geld sind «3 Fr. 50 Rp.» und «Fr. 3.50» gleichwertig, das Lernziel entscheidet, ob die Schreibweise zählt. Tausender schreibt man mit Apostroph (1'000).
- **Deutsch**:
  - Schriftspracherwerb: Laute hören, Laute Buchstaben zuordnen, Laute verbinden, kurze Texte verstehen
  - eigene Texte planen, schreiben und überarbeiten
  - Rechtschreibung ohne ß
  - Mundart und Schweizer Standarddeutsch in getrennten Situationen
  - Literatur: erzählen, deuten, vergleichen
- **Fremdsprachen**: Wortschatz in Handlungen eingebettet, mit Sprachmittlung (zum Beispiel eine französische Einladung einer deutschsprachigen Figur erklären), Dialogen, Schreiben und kulturellen Bezügen.
- **NMG**: integriert unterrichtet, zum Beispiel eine Einheit zum Schulweg mit Karte, Beobachtung, Verkehr und Gemeinde. Kinder stellen Fragen und überarbeiten ihre ersten Erklärungen.
- **Medien und Informatik**: Anwendungskompetenzen über die Fächer hinweg. Blockprogrammierung ist eine Option unter mehreren.
- **Musik, Bildnerisches Gestalten, Textiles und Technisches Gestalten, Bewegung und Sport**: praktische Aufträge mit Kriterien, dokumentiert durch Foto oder Aufnahme und eine Selbsteinschätzung des Kindes.
- **Überfachlich**: Selbstständigkeit, Lernstrategien und Bildung für Nachhaltige Entwicklung, jeweils an konkrete Aufgaben gebunden.

Pro Kompetenz zeigt die App getrennt an: «Aufgabe verfügbar», «selbstständig digital gezeigt», «praktischer Auftrag dokumentiert» und «noch keine ausreichende Beobachtung».

## 4. Handschrift und Eingabe
In Version 1 bewertet die App automatisch nur Ziffern, einfache Operatoren und kurze Zahlenfolgen. Freies Schreiben und Zeichnen sind trotzdem überall möglich.

Die Eingabearten:
- **Ziffern**: PencilKit erfasst die Striche, ein lokales Modell wertet Form und zeitlichen Verlauf aus. Kinder schreiben frei, auf Linien oder in Kästchen. Das Original bleibt sichtbar, und das Kind kann die gelesene Zahl bestätigen, ändern oder zum Ziffernblock wechseln.
- **Buchstaben**: Mehrere lesbare Formen sind gültig. Richtung und Reihenfolge der Striche werden nur dort ausgewertet, wo die Bewegung geübt wird. Es gibt eine Führung für Linkshänder.
- **Wörter und Diktate**: Vision dient zum Vergleich. Sprach- und Tastaturkorrektur sind bei Rechtschreibaufgaben aus. Eine Rückfrage darf die richtige Schreibweise nicht verraten.
- **Offene Arbeiten**: Das Original bleibt erhalten, Geometrie wird über Eigenschaften und Toleranzen bewertet. Andere offene Arbeiten haben den Status «nicht automatisch beurteilt».
- **Sprache**: Vorlesen, eigene Aufnahme anhören und Nachsprechen sind getrennt. Die Erkennung läuft nur lokal, und Transkriptionsfehler führen nie zu Aussagen über Aussprache oder Lesefähigkeit.

Das Handschrift-Labor arbeitet vollständig durch Agenten:
1. **Referenzpfade**: Der Design-Agent erstellt Pfade in Schweizer Formen, etwa die «1» mit Aufstrich, die «7» mit Querstrich und Basisschrift-ähnliche Buchstaben, ohne fremde Schriften zu kopieren.
2. **Mehrere unabhängige Generatoren**: Mindestens drei Generatorfamilien, von verschiedenen Agenten mit unterschiedlichen Ansätzen gebaut: parametrische Störung, physikalisches Bewegungsmodell und ein gelerntes Strichfolgen-Modell. Sie erzeugen kindliche Varianten:
   - Zittern, schwankende Grösse und Neigung
   - Pausen, abgesetzte und nachträgliche Striche
   - Überzeichnen, Radieren, eng geschriebene Ziffern
   - Ungenauigkeit beim Schreiben mit dem Finger und Kontakt mit dem Handballen
   - spiegelverkehrte Ziffern als echter Lernfehler
3. **Öffentliche Datensätze**: EMNIST und ähnliche Datensätze nur mit passender Lizenz und nur ergänzend.
4. **Getrennte Testmengen**: Generatorfamilien und Startwerte des Abschlusstests kommen im Training nie vor und stehen für «unbekannte Schreiber». Dazu kommen gezielt schwierige Fälle (1/7, 4/9, 5/6, 0/6).
5. **Modellvergleich**: Bildklassifikator, Strichfolgen-Modell und Kombination aus beiden auf denselben Daten.
6. **Erkennung ohne Kenntnis der Lösung**: RecognitionKit kennt nur den erwarteten Zeichentyp. Das ist über die Abhängigkeiten zwischen den Modulen technisch erzwungen.
7. **Kennzahlen**: richtige Antworten, die wegen der Erkennung falsch erscheinen, falsche Antworten, die technisch zu richtigen werden, Rückfragen pro zehn Antworten, abgeschlossene Aufgaben. Ziel: weniger als 0,5 % technisch verursachte Fehlbewertungen bei mindestens 90 % automatischer Bewertbarkeit, auf jeder zurückgehaltenen Generatorfamilie einzeln. Die Schwelle für Rückfragen ist bewusst vorsichtig gewählt.
8. **Ende-zu-Ende-Tests**: Persona-Agenten spielen synthetische Strichfolgen als Touch- und Pencil-Eingaben in die echte App ein (XCUITest), auf allen unterstützten Simulatoren. Optional laufen die Tests zusätzlich auf echten iPads in einer Cloud-Gerätefarm.
9. **Latenz**: gemessen mit Instruments und Performance-Tests vom Abschluss der Eingabe bis zur Rückmeldung, auf dem ältesten unterstützten Gerätemodell.

Die Genauigkeit bei echten Kindern bleibt «unbestätigt». Deshalb ist der Ziffernblock immer erreichbar, und die Handschriftbewertung lässt sich im Bereich für Erwachsene pro Profil abschalten.

## 5. Lernlogik, Hilfen und Tests
- **Einstieg**: kurz, mit Erfolgserlebnis. Daraus ergibt sich ein vorläufiger Startpunkt, den Erwachsene ändern können.
- **Stufen des Lernstands** pro Kompetenz: mit Hilfe gezeigt, selbstständig gezeigt, nach einer Pause erneut gezeigt, in einer neuen Situation angewendet. Gespeichert werden auch Aufgabenfamilie, Hilfe, Eingabeart und Unsicherheit. Ob eine Vorlesehilfe das Ergebnis relativiert, hängt vom Lernziel ab.
- **Neues lernen**: Vormachen mit hörbaren Gedanken, dann eine teilweise vorbereitete Aufgabe, dann eine eigene.
- **Festigen**: aktives Abrufen in wachsenden Abständen. Für Faktenwissen tritt FSRS gegen eine einfache Wiederholungsregel an, verglichen in der Simulation.
- **Mischen**: erst ähnliche Beispiele, dann gemischte Aufgaben mit eigener Strategiewahl.
- **Fehler**: Eine einzelne falsche Antwort ist eine Vermutung. Eine Anschlussaufgabe klärt, ob das Problem beim Stellenwert, bei der Anweisung oder bei der Eingabe liegt.
- **Hilfen**: erst Aufmerksamkeit lenken, dann einen Teilschritt zeigen, dann den Lösungsweg. Danach folgt eine neue, verwandte Aufgabe.
- **Anpassung**: rund 80 % Erfolg als Startwert, mit eigenen Regeln für Einführung, Erkundung, Automatisierung und Test. BKT oder IRT nur, wenn sie in der Simulation das Behalten neuer synthetischer Lernender besser vorhersagen.
- **Kein Gesamt-Fitness-Wert**, weil der Transfer von Gedächtnisspielen auf schulische Leistungen wissenschaftlich schwach belegt ist.
- **Tests auf vier Ebenen**:
  - Lektionscheck: kurz, unbenotet, entscheidet über den nächsten Schritt
  - Modultest: neue Aufgabenfamilien, Lösungen mit und ohne Hilfe getrennt, mit verzögerter Wiederaufnahme
  - Kapiteltest: mehrere Kompetenzen, mindestens eine Aufgabe zum Begründen oder Anwenden
  - Jahresbilanz: Prüfplan pro Fach, ergänzt durch praktische Dokumentationen
- **Keine Schulnoten**, sondern konkrete Aussagen zum Lernstand.

## 6. Inhaltsproduktion
Der Umfang der Gesamtvision liegt bei über 400 Modulen und über 15'000 kuratierten Aufgaben, ergänzt durch Generatoren. Ein Lernziel gilt als fertig, wenn es genügend unterschiedliche Aufgabenfamilien, Hilfen, Transferaufgaben und eine verlässliche Bewertung hat.

Die Pipeline:
1. **Lernziel**: Der Autor-Agent beschreibt Tätigkeit, Vorwissen und beobachtbaren Nachweis und gibt den Kompetenzcode an. Der Kritiker prüft die Passung zum Lehrplan anhand der öffentlichen Kompetenzbeschreibungen.
2. **Aufgabenfamilie**: Auftrag, Audiotext, Darstellungen, alle gültigen Lösungen, zulässige Varianten, Fehlvorstellungen, Hilfen, Barrierefreiheit und Rechtevermerk, gespeichert als versioniertes JSON nach festem Schema.
3. **Unabhängiges Lösen**: Der Löser-Agent arbeitet ohne Schlüssel und mit anderem Modell. Abweichungen gehen zurück an den Autor. Sprach-, Leselast- und Mehrdeutigkeitsprüfung folgen.
4. **Generatoren**: reproduzierbar über Version und Startwert. Pro Generator laufen über eine Million Startwerte gegen Invarianten: lösbar, Lösung korrekt, keine doppelten Optionen, keine versteckten Hinweise, Einheiten stimmen, Grenzen des Zahlenraums eingehalten.
5. **Simulierte Erprobung**:
   - Schülermodelle mit Fehlvorstellungen aus der Fachliteratur müssen die vorgesehenen Fehler erzeugen, und die Diagnose muss sie erkennen.
   - Persona-Agenten bedienen die Aufgabe über die Oberfläche: können nicht lesen, tippen ungenau, haben grosse Finger, sind langsam, brechen ab.
   - Automatische Audits prüfen Barrierefreiheit (performAccessibilityAudit), Zielgrössen (mindestens 60 pt im Modus für Zyklus 1) und ob jede Aufgabe für Zyklus 1 ohne Lesen lösbar ist.
6. **Freigabe**: durch das Gate-System und einen fremden Prüfagenten, nie durch den Autor selbst. Das Red-Team zieht Stichproben. Jede Familie hat Version und Änderungsverlauf, fehlerhafte Aufgaben lassen sich zurückziehen, betroffene Wertungen werden korrigiert.

Die Kennzeichnung «fachlich geprüft» heisst: von unabhängigen KI-Agenten und automatischen Prüfungen geprüft. Ein Gutachten von Fachpersonen ist es nicht, und die App sagt das auch so.

## 7. Motivation, Inklusion und Abgrenzung
- **Schweizreise mit echten Tätigkeiten**: In Luzern eine Schifffahrt nach einem selbst erstellten Fahrplan planen, im Jura Spuren vergleichen, im Tessin eine Begrüssung hören. Die Aufgaben wachsen mit dem Alter der Kinder.
- **Schneller Einstieg** mit Bildprofil und «Weiterlernen», «Etwas entdecken» oder «Wiederholen». Anweisungen lassen sich jederzeit erneut anhören.
- **Runden mit Ende**: nach 5 bis 10 Minuten. Pausen kosten nichts. Keine Serien mit Verlustangst, keine Werbung, keine Lootboxen, keine In-App-Käufe.
- **Reisebuch**: Es würdigt Eigenständigkeit und Neugier. Auch Kinder, die mehr Hilfe brauchen, entdecken die ganze Schweiz.
- **Barrierefreiheit in jedem Aufgabentyp**:
  - Antippen statt Ziehen, Form oder Muster zusätzlich zur Farbe, eine visuelle Alternative zu Audio
  - VoiceOver, Schaltersteuerung, Hardware-Tastatur, grössere Schrift, reduzierte Bewegung, Bedienung für Linkshänder
- **Förderung**: Bildwortschatz für Kinder mit Deutsch als Zweitsprache, strukturierte Mengenbilder bei Schwierigkeiten mit Zahlen, wählbare Schrift und Abstände ohne Wirksamkeitsversprechen.
- **Abgrenzung**: Bestehende Apps (ANTON, Mindsteps, Kaligo) werden nur über öffentliche Informationen analysiert. Chnobel positioniert sich mit freiem Lösungsweg, kindgerechter Handschrift, nachvollziehbarem Lehrplanbezug, praktischen Aufträgen, einem vollständig offline nutzbaren Kern und ehrlicher Kennzeichnung der Nachweise.

## 8. Technik und Datenschutz
- SwiftUI, Swift 6, Observation und SwiftData. iPadOS ist die Referenzplattform, dazu iPhone und Mac. Mindestens iOS/iPadOS 18.
- Swift Packages: CoreDomain, CurriculumKit, TaskEngine, InputKit, RecognitionKit, LearningEngine, MotivationKit, VoiceKit, ContentPacks, Feature-Module pro Fach und LearnerSim (Simulationsumgebung mit synthetischen Lernenden, Persona-Agenten und Handschriftgeneratoren).
- Drei Schnittstellen sind besonders streng definiert:
  - RecognitionKit liefert Lesarten mit Unsicherheit.
  - TaskEngine bewertet die bestätigte Eingabe gemäss Lernziel.
  - LearningEngine entscheidet über den Lernpfad.
- Inhalte, Bewertung und Lernstandsberechnung tragen je eigene Versionen.
- CI auf macOS-Runnern:
  - Build, Swift Testing, UI-, Snapshot- und Inhaltstests, Mutationstests
  - Barrierefreiheits-Audits, Performance- und Latenztests
  - Migrationen mit alten Datenbeständen, unterbrochene Updates, Profilwechsel, Wiederherstellung nach Absturz
  - Simulationsläufe von LearnerSim
- **Daten**:
  - lokale Bildprofile ohne Konto, ein gesicherter Bereich für Erwachsene mit Berichten, Zeitlimiten, Export und Löschung
  - keine Netzwerkzugriffe, keine Drittanbieter-SDKs, Privacy Manifest «keine Daten erhoben»
  - Rohhandschrift und Stimme verlassen nie das Gerät
- Der Compliance-Agent erstellt eine Datenschutz-Folgenabschätzung und eine Prüfung gegen die Kids Category anhand öffentlicher Regelwerke.
- iCloud-Sync und ein lokaler Lehrpersonenbereich (ClassKit) sind vorbereitet, gelten aber als «nicht mit realen Schulen erprobt».

## 9. Definition von «fertig und perfekt»
Weil kein Mensch abnimmt, ist «perfekt» als messbare Abnahme definiert. Der Release-Agent lädt erst hoch, wenn alle Punkte erfüllt sind:
- alle CI-Gates grün, ohne dass Schwellen nachträglich gesenkt wurden
- keine offenen Befunde der Schwere «kritisch» oder «hoch» im Register des Red-Teams
- Abdeckungsmatrix für die Profile Luzern und Bern vollständig: jede Kompetenzstufe der 1.–6. Klasse mit Nachweisform, mindestens drei Aufgabenfamilien, einer Transferaufgabe und einer verzögerten Wiederaufnahme oder ausdrücklich als praktischer Auftrag gekennzeichnet
- Handschrift-Kennzahlen auf allen zurückgehaltenen Generatorfamilien erreicht
- Barrierefreiheits-Audit fehlerfrei auf allen Bildschirmen und für alle Aufgabentypen
- alle Persona-Agenten schliessen jeden Lernweg ohne Sackgasse ab
- jeder Text in der App mit Belegstatus versehen, keine Behauptung über dem Beleg
- Rechteverzeichnis vollständig, Datenschutz- und Kids-Category-Prüfung ohne offene Punkte
- Build signiert, über die App Store Connect API zu TestFlight hochgeladen und von Apple verarbeitet. Eine abgelehnte Prüfung durch Apple führt zu einem neuen Arbeitszyklus der Agenten.

## 10. Risiken und Gegenmassnahmen
- **Die Agenten driften ab oder vergessen frühere Entscheidungen.**
  - Gegenmassnahme: Projektgedächtnis im Repository, ADRs als Pflichtlektüre, Architektur-Tests in der CI.
- **Die Agenten teilen dieselben blinden Flecken.**
  - Gegenmassnahme: verschiedene Modelle für Autor und Prüfer, deterministische Validatoren, ein unabhängiges Red-Team.
- **Agenten machen Gates «passend».**
  - Gegenmassnahme: geschützte Gate-Dateien, Änderung nur über das Gremium, Mutationstests prüfen, ob Tests echte Fehler finden.
- **Die Simulation bestätigt nur ihre eigenen Annahmen.**
  - Gegenmassnahme: Schülermodelle aus der Fachliteratur statt aus dem App-Code, getrennte Agenten für Simulation und Produkt.
- **Synthetische Handschrift bildet echte Kinder schlecht ab.**
  - Gegenmassnahme: mehrere unabhängige Generatoren, vorsichtige Rückfragen, Ziffernblock immer erreichbar, Status «unbestätigt».
- **Bedienhürden für Sechsjährige bleiben unentdeckt.**
  - Gegenmassnahme: harte Gestaltungsregeln. Keine Pflicht zu lesen, grosse Zielflächen, eine Hauptaktion pro Bildschirm, Audio und Rückgängig überall, stark eingeschränkte Persona-Agenten.
- **Die App überschätzt die Beherrschung.**
  - Gegenmassnahme: unbekannte Aufgabenfamilien, verzögerte Wiederaufnahme, Transferaufgaben.
- **Die Inhaltsmenge wächst schneller als die Qualität.**
  - Gegenmassnahme: Abdeckung pro Kompetenzstufe messen, Lücken vor neuen Varianten schliessen.
- **Der Arbeitsfluss bleibt stecken (Endlosschleifen, widersprüchliche Reviews).**
  - Gegenmassnahme: Der Orchestrator erkennt Stillstand, eskaliert ans Gremium, und es gilt die vorsichtigere Option.
- **Rechtliche Risiken bei Inhalten.**
  - Gegenmassnahme: nur eigene oder gemeinfreie Inhalte, Rechteverzeichnis, keine Lehrplantexte im Wortlaut.

## 11. Roadmap (jede Phase endet mit automatisch geprüften Kriterien)
- **Phase 0: Agenten-Organisation und Fundament**
  - Inhalt: Rollen, Spielregeln, CI-Gates, Projektgedächtnis, Luzerner Kompetenzmatrix, Inhaltsschema, Design-System, Architektur, LearnerSim v1.
  - Kriterium: Eine Beispielaufgabe durchläuft die komplette Pipeline bis zu einem internen Build.
- **Phase 1: erster vollständiger Lernweg**
  - Inhalt: «Zahlen bis 20» mit Material, Handschrift, Ziffernblock, Vorlesen, Hilfen, Lernstand und Erwachsenenansicht. Dazu ein kleines Modul zur Zuordnung von Lauten und Buchstaben.
  - Kriterium: läuft offline, alle Gates grün, Persona-Agenten ohne Sackgasse. Erster TestFlight-Upload als technischer Durchstich.
- **Phase 2: Handschrift-Labor**
  - Inhalt: drei Generatorfamilien, Modellvergleich, Kennzahlen, Latenz, Ende-zu-Ende-Tests mit eingespielten Strichen.
  - Kriterium: Zielwerte auf allen zurückgehaltenen Familien erreicht.
- **Phase 3: Mathematik und Deutsch, 1.–2. Klasse**
  - Inhalt: alle Kompetenzstufen beider Fächer.
  - Kriterium: Abdeckungsmatrix vollständig, die Simulation zeigt, dass Fehlvorstellungen erkannt und gefördert werden.
- **Phase 4: 3.–4. Klasse und Profil Bern**
  - Inhalt: NMG, erste Fremdsprache, Medien und Informatik, praktische Lernwege.
  - Kriterium: Beide Kantonsprofile laufen im selben Kern korrekt.
- **Phase 5: vollständige Primarstufe**
  - Inhalt: bis zur 6. Klasse, zweite Fremdsprache, alle Fachbereiche, vorbereiteter Lehrpersonenbereich.
  - Kriterium: Abdeckungsmatrix 1.–6. Klasse vollständig.
- **Phase 6: Härtung und Evidenzbilanz**
  - Inhalt: Red-Team-Durchgänge bis keine kritischen und hohen Befunde mehr offen sind, Simulationsbericht, Register offener Nachweise.
  - Kriterium: Alle Punkte der Definition von «fertig und perfekt» sind erfüllt.
- **Phase 7: finaler TestFlight-Build**
  - Inhalt: Release-Agent signiert, lädt hoch und dokumentiert Version, Änderungen und Belegstatus.
  - Kriterium: Build ist in TestFlight verarbeitet und verfügbar.
- **Danach (optional)**: PER und Tessin mit eigenen Agenten-Pipelines pro Sprache, im gleichen Verfahren.

## 12. Was ohne reale Personen nicht belegbar ist
- die Genauigkeit der Handschrifterkennung bei echten Kindern
- die Verständlichkeit für Sechsjährige
- Motivation und freiwillige Rückkehr
- die Lernwirksamkeit
- Fairness über verschiedene Gruppen von Kindern
- das Verhalten auf echter Hardware, sofern keine Cloud-Gerätefarm genutzt wird
- die Feinheiten des Schweizer Sprachgebrauchs aus menschlicher Sicht

Diese Punkte führen die Agenten als offene Nachweise. Die App kompensiert sie durch vorsichtige Voreinstellungen und durch Steuerung durch Erwachsene.

# Meine Frage an dich

Wie lässt sich dieser Plan perfektionieren, wenn Kosten, Aufwand und Zeit keine Rolle spielen, aber zwei Bedingungen strikt gelten: Ausschliesslich KI-Agenten arbeiten, und kein Mensch ist beteiligt, auch ich nicht. Beurteile den Plan kritisch aus der Sicht einer erfahrenen Schweizer Primarlehrperson, einer Lernforscherin, eines Senior-iOS-Architekten, einer ML-Ingenieurin für Handschrift, eines Game-Designers für Kinder und eines Experten für autonome Multi-Agenten-Systeme. Konkret:

1. Wie muss die Agenten-Organisation aufgebaut sein, damit sie über Monate ohne Menschen stabil, konsistent und ehrlich arbeitet? Welche Rollen, Regeln, Gedächtnisstrukturen und Schutzmechanismen gegen Abdriften, Endlosschleifen und Selbsttäuschung fehlen?
2. Ist die Definition von «fertig und perfekt» vollständig und messbar? Was fehlt, damit ein autonomes System sie nicht formal erfüllt, aber inhaltlich verfehlt?
3. Wie realistisch kann synthetische Handschrift sechs- bis achtjährige Kinder nachbilden, und welche Generatoren und Testverfahren kommen echten Daten am nächsten?
4. Wie simuliert man Lernende und Bedienung durch Kinder so, dass die Simulation nicht nur die eigenen Annahmen bestätigt? Welche Fehlvorstellungen aus der Fachliteratur gehören zwingend in die Bibliothek?
5. Welche Lehrplan-, Schweiz- und Fachfehler stecken noch im Plan?
6. Welche technischen Schritte bis zum TestFlight-Upload können ohne Menschen scheitern (Signierung, App Review, Infrastruktur), und wie fangen die Agenten das ab?

Antworte mit einer priorisierten Liste konkreter Verbesserungen (Wirkung hoch/mittel/tief), den grössten Risiken samt Gegenmassnahmen und einer überarbeiteten Roadmap. Schlage keine Massnahmen vor, die Menschen erfordern. Ausgenommen sind nur die einmaligen technischen Voraussetzungen. Zeige dort, wie man sie auf ein Minimum reduziert.
