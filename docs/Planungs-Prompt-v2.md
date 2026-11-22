# Kontext und Idee

Ich entwickle «Chnobel», eine native Lern-App in Swift für die 1. bis 6. Primarklasse in der Deutschschweiz. Chnobel ist ein digitales Arbeitsheft, in dem Kinder ihren Denkweg zeigen. Sie schreiben Antworten von Hand wie im Heft (Finger oder Apple Pencil) und legen Material wie Plättchen, Münzen oder Zeiger. Alternativ arbeiten sie per Ziffernblock, Tastatur oder Antwortauswahl, umschaltbar in den Einstellungen. Eine Reise durch die Schweiz gibt den Kindern einen Grund, das Heft gerne zu öffnen. Der eigentliche Wert liegt in der Rückmeldung: Chnobel erkennt, was beim nächsten Schritt hilft, und weiss, wann es zu wenig weiss, um eine Leistung zu beurteilen.

Der erste Qualitätsmassstab ist dieser Ablauf: Eine Erstklässlerin soll 8 + 7 so legen, dass man das Ergebnis gut sieht. Sie schiebt zwei Plättchen zur Acht, legt fünf daneben und schreibt 15. Liest die App ihre Fünf als Sechs, kann das Kind die Eingabe berichtigen. Einige Tage später kommt 9 + 5 in einer anderen Darstellung. Erst wenn auch das gelingt, gilt die Strategie «zur Zehn ergänzen» als selbstständig angewendet (Bezug Lehrplan 21: MA.1.C.1, Stufen b und c).

Zeit und Kosten spielen keine Rolle. Es gilt aber eine harte Randbedingung.

# Grundsatz: keine externen Personen

Entwicklung, Inhalte, Prüfung und Tests erfolgen ausschliesslich durch mich und durch KI-Agenten. Ich bin die einzige menschliche Person im Projekt: Ich entwickle, teste auf meinen eigenen Geräten und gebe frei.

Ausgeschlossen sind:
- Kinder, Eltern, Lehrpersonen und Schulen
- Pädagogische Hochschulen, Fachdidaktikerinnen und Fachdidaktiker
- Sprecherinnen, Illustratoren, Musiker
- Juristen und Beta-Testerinnen
- jede Erhebung von Daten über Personen
- eigene Server
- öffentliche Verteilung

Ziel ist ein interner TestFlight-Build für meine eigenen Geräte. Was sich nur mit realen Personen belegen lässt, wird nicht behauptet, sondern als «unbestätigt» geführt. Die App gleicht diese Unsicherheit durch vorsichtige Voreinstellungen aus.

So werden externe Rollen ersetzt:
- **Fachredaktion und Lehrpersonen**: getrennte KI-Rollen. Ein Autor-Agent entwirft, ein Löser-Agent löst ohne Lösungsschlüssel, ein Didaktik-Kritiker prüft. Dazu kommen ein Sprachprüfer für Schweizer Standarddeutsch und ein Barrierefreiheitsprüfer. Deterministische Validatoren ergänzen die Agenten, die Freigabe mache ich.
- **Kindertests**: simulierte Lernende in drei Formen:
  - regelbasierte Schülermodelle mit einer Bibliothek typischer Fehlvorstellungen, etwa Zehnerübergang vergessen, Stellenwerte vertauscht oder beim Weiterzählen den Startwert mitgezählt (8 + 7 = 14)
  - Persona-Agenten, die die App über UI-Automation bedienen und dabei eingeschränkt sind: können nicht lesen, tippen ungenau, haben grosse Finger, sind langsam, brechen ab
  - Zufalls- und Stresstests
- **Handschrift von Kindern**: synthetische Handschrift aus einem eigenen Strichmodell, dazu meine eigenen, bewusst variierten Schreibproben. Öffentliche Datensätze wie EMNIST kommen nur für Vorversuche und nur mit passender Lizenz zum Einsatz.
- **Sprecher**: Systemstimmen (AVSpeechSynthesizer) oder vorab erzeugte Sprachdateien, mit einem Aussprache-Lexikon für Schweizer Begriffe und Ortsnamen. Optional nehme ich selbst Audio auf.
- **Illustration und Sound**: prozedurale Grafik (SwiftUI Canvas und Shapes, SF Symbols, eigene Vektorgrafiken) und synthetisch erzeugte Klänge, zusammengehalten durch ein einheitliches Design-System.
- **Recht und Datenschutz**: Datenschutz durch die Architektur. Es gibt keine Konten, keine Analytics und keinen Netzwerkzugriff im Kern, und keine Daten verlassen das Gerät. Lehrplantexte werden nicht übernommen, sondern nur Kompetenzcodes mit eigenen Formulierungen. Lieder sind gemeinfrei oder selbst erstellt.
- **Wirksamkeitsstudie**: eine interne Evidenzbilanz aus Simulationen und Abdeckungsmatrix. Das Produktversprechen lautet «lehrplanbezogen und forschungsinformiert», nicht «wirksam».

# Detaillierter Plan

## 1. Prioritäten
1. **Hoch**: Technische Erkennung und fachliche Bewertung trennen. Ein unleserliches Zeichen, ein App-Fehler, eine übersprungene Aufgabe und ein fachlicher Fehler werden unterschiedlich erfasst.
2. **Hoch**: Für jede Kompetenzstufe festlegen, woran man sie erkennt: Antwort, dargestellter Lösungsweg, Werkstück (Foto oder Aufnahme im Reisebuch) oder Selbsteinschätzung des Kindes.
3. **Hoch**: Ein erster vollständiger Lernweg, den ein simuliertes Kind ohne Lesekenntnisse und ohne Hilfe eines Erwachsenen bedienen kann, mit dem Finger auf einem gewöhnlichen iPad.
4. **Hoch**: Den kantonalen Lehrplan versionieren. Kanton, Schulsprache, Klassenstufe, Grundanspruch, Orientierungspunkt und die von Chnobel empfohlene Reihenfolge werden getrennt geführt.
5. **Hoch**: Verzögertes Behalten und Transfer prüfen. Ein bestandener Modultest ist nur ein erster Nachweis.
6. **Hoch**: Eine Redaktionspipeline mit KI-Agenten und harten automatischen Prüfungen.
7. **Hoch**: Ehrliche Kennzeichnung. Jede Aussage über Erkennung, Verständlichkeit oder Lernwirkung trägt den Status «automatisch geprüft», «simuliert» oder «unbestätigt».
8. **Mittel**: Praktische Aufträge ausserhalb des Bildschirms für NMG, Gestalten, Musik und Bewegung.
9. **Mittel**: Die Schweizreise für zwei Altersgruppen gestalten, ruhig und gesprochen für die 1.–3. Klasse, eigenständiger für die 4.–6. Klasse.
10. **Tief**: Ferienautomatik, Avatar-Zubehör und Zusatzanimationen zurückstellen.

## 2. Lehrplan 21 und Schweizer Schulrealität
- Zielgruppe ist die 1. bis 6. Klasse in der Deutschschweiz. Für den Einstieg gibt es Aufgaben auf Kindergartenniveau: Mengen bis fünf erkennen, Laute unterscheiden, gesprochene Anweisungen verstehen. Sie dienen der Unterstützung, ohne das Kind sichtbar zurückzustufen.
- Die kleinste Referenz ist die Kompetenzstufe. Pro Lernziel werden gespeichert:
  - die kantonale Fassung
  - Fach, Kompetenzbereich und Handlungs- oder Themenaspekt
  - Kompetenzcode und Stufe
  - Grundanspruch und Orientierungspunkt (am Ende der 4. Klasse, für Zyklus 1 gibt es keine)
  - davon getrennt die eigenen Lektionen und Klassenempfehlungen
- Luzern ist der erste Referenzkanton (Englisch ab der 3., Französisch ab der 5. Klasse). Das zweite Profil ist Bern, wo die Sprachfolge umgekehrt ist. Graubünden braucht später Profile nach Schulsprache und Region. Wechselt ein Kind den Kanton, bleibt sein Lernstand erhalten.
- Kantonsdaten (Sprachfolge, Schrift, Stundentafeln) recherchiere ich aus öffentlichen Quellen und dokumentiere sie mit Quelle und Datum. Die Romandie (PER) und das Tessin (Piano di studio) folgen erst spät.

Die Fächer:
- **Mathematik**: drei Kompetenzbereiche: Zahl und Variable, Form und Raum sowie Grössen, Funktionen, Daten und Zufall. Jeder ist verbunden mit den Handlungsaspekten Operieren und Benennen, Erforschen und Argumentieren, Mathematisieren und Darstellen. Kinder rechnen, schätzen, stellen dar, vergleichen Wege und begründen. Bei Geld sind «3 Fr. 50 Rp.» und «Fr. 3.50» gleichwertig, das Lernziel entscheidet, ob die Schreibweise zählt. Tausender schreibt man mit Apostroph (1'000).
- **Deutsch**:
  - Schriftspracherwerb: Laute hören, Laute Buchstaben zuordnen, Laute verbinden, kurze Texte verstehen
  - eigene Texte planen, schreiben und überarbeiten
  - Rechtschreibung ohne ß
  - Mundart und Schweizer Standarddeutsch in bewusst getrennten Situationen
  - Literatur: erzählen, deuten, vergleichen
- **Fremdsprachen**: Wortschatz in Handlungen eingebettet. Ein Kind hört zum Beispiel eine französische Einladung und erklärt einer Figur, wann und wo das Treffen ist. Dazu kommen Dialoge, Schreiben und kulturelle Bezüge.
- **NMG**: integriert unterrichtet. Eine Einheit zum Schulweg verbindet Karte, Beobachtung, Verkehr und Gemeinde. Kinder stellen Fragen, sammeln Beobachtungen und überarbeiten ihre erste Erklärung. Kantone und Hauptorte sind nur ein kleiner Teil.
- **Medien und Informatik**: Anwendungskompetenzen über die Fächer hinweg, zum Beispiel eine Weganleitung auf Mehrdeutigkeit prüfen, zwei Darstellungen derselben Nachricht vergleichen oder eigene Daten darstellen. Blockprogrammierung ist eine Option unter mehreren.
- **Musik, Bildnerisches Gestalten, Textiles und Technisches Gestalten, Bewegung und Sport**: praktische Aufträge. Kinder erfinden einen Rhythmus, bauen eine Papierbrücke oder erproben eine Bewegungsfolge. Die App gibt Auftrag und Kriterien, das Kind dokumentiert mit Foto oder Aufnahme und schätzt sich selbst ein. Wissensquiz erfassen nur das Wissen, nicht die Kompetenz.
- **Überfachlich**: Selbstständigkeit, Lernstrategien und Bildung für Nachhaltige Entwicklung, jeweils an konkrete Aufgaben gebunden.

Pro Kompetenz zeigt die App getrennt an: «Aufgabe verfügbar», «selbstständig digital gezeigt», «praktischer Auftrag dokumentiert» und «noch keine ausreichende Beobachtung».

## 3. Handschrift und Eingabe
In Version 1 bewertet die App automatisch nur Ziffern, einfache Operatoren und kurze Zahlenfolgen. Freies Schreiben und Zeichnen sind trotzdem überall möglich.

Die Eingabearten:
- **Ziffern**: PencilKit erfasst die Striche, ein lokales Modell wertet Form und zeitlichen Verlauf aus. Kinder schreiben frei, auf Linien oder in Kästchen. Das Original bleibt sichtbar, und das Kind kann die gelesene Zahl bestätigen, ändern oder zum Ziffernblock wechseln.
- **Buchstaben**: Mehrere lesbare Formen sind gültig. Richtung und Reihenfolge der Striche werden nur ausgewertet, wo die Schreibbewegung selbst geübt wird. Es gibt eine Führung für Linkshänder.
- **Wörter und Diktate**: Vision dient zum Vergleich. Bei Rechtschreibaufgaben sind Sprach- und Tastaturkorrektur ausgeschaltet. Eine Rückfrage zur Erkennung darf die richtige Schreibweise nicht verraten.
- **Freie Sätze, Zeichnungen, Konstruktionen**: Die Originalarbeit bleibt erhalten. Geometrie wird anhand von Eigenschaften und Toleranzen bewertet. Offene Arbeiten haben den Status «nicht automatisch beurteilt».
- **Sprache**: Vorlesen, eigene Aufnahme anhören und freiwilliges Nachsprechen sind getrennte Funktionen. Lokale Spracherkennung wird pro Gerät geprüft und erzwungen. Ein Fehler der Transkription löst nie eine Aussage über Aussprache oder Lesefähigkeit aus.

Das Handschrift-Labor arbeitet ohne Kinder:
1. **Synthetischer Generator**: Ich zeichne Referenzpfade für Ziffern und Buchstaben selbst, in Schweizer Formen wie der «1» mit Aufstrich, der «7» mit Querstrich und Basisschrift-ähnlichen Buchstaben, ohne Schriften zu kopieren. Ein parametrisches Modell erzeugt daraus kindliche Varianten:
   - Zittern, schwankende Grösse und Neigung
   - Pausen mitten im Zeichen, abgesetzte und nachträgliche Striche
   - Überzeichnen, Radieren, eng aneinander geschriebene Ziffern
   - Ungenauigkeit beim Schreiben mit dem Finger und Kontakt mit dem Handballen
   - spiegelverkehrte Ziffern, die als echter Lernfehler gelten und nicht als Erkennungsfehler
2. **Eigene Proben**: Ich schreibe mit Finger und Pencil, mit beiden Händen, bewusst langsam, schief und unordentlich.
3. **Getrennte Testmengen**: Stilfamilien und Generator-Startwerte des Abschlusstests kommen im Training nie vor und stehen für «unbekannte Schreiber». Dazu kommen gezielt schwierige Fälle (1/7, 4/9, 5/6, 0/6).
4. **Modellvergleich**: Ein Bildklassifikator, ein Modell für Strichfolgen und eine Kombination aus beiden werden auf denselben Daten verglichen.
5. **Erkennung ohne Kenntnis der Lösung**: RecognitionKit kennt nur den erwarteten Zeichentyp, nie die richtige Antwort. Das wird über die Abhängigkeiten zwischen den Modulen technisch erzwungen. So verschwinden echte Lernfehler nicht im Lernstandsbericht.
6. **Kennzahlen**: richtige Antworten, die wegen der Erkennung falsch erscheinen, falsche Antworten, die technisch zu richtigen werden, Rückfragen pro zehn Antworten und abgeschlossene Aufgaben. Ziele auf den synthetischen Testmengen: weniger als 0,5 % technisch verursachte Fehlbewertungen bei mindestens 90 % automatischer Bewertbarkeit. Weil Daten von echten Kindern fehlen, ist die Schwelle für Rückfragen bewusst vorsichtig gewählt. Bei Unsicherheit fragt die App lieber nach, als falsch zu werten.
7. **Latenz**: Die Tinte folgt dem Finger sofort. Gemessen wird die Zeit vom Abschluss der Eingabe bis zur sichtbaren Rückmeldung, auch auf dem ältesten Gerät, das ich besitze.

Die Genauigkeit bei echten Kindern bleibt «unbestätigt». Deshalb ist der Ziffernblock immer erreichbar, und Erwachsene können die Handschriftbewertung pro Profil abschalten.

## 4. Lernlogik, Hilfen und Tests
- **Einstieg**: Das Kind wählt eine Tätigkeit, hört die Anweisung und löst ein paar Aufgaben mit Erfolgserlebnis. Daraus ergibt sich ein vorläufiger Startpunkt, den Erwachsene ändern können.
- **Stufen des Lernstands** pro Kompetenz: mit Hilfe gezeigt, selbstständig gezeigt, nach einer Pause erneut gezeigt, in einer neuen Situation angewendet. Gespeichert werden auch Aufgabenfamilie, genutzte Hilfe, Eingabeart und Unsicherheit. Eine Vorlesehilfe gilt in Mathematik als Zugang zum Inhalt, beim Prüfen des Entzifferns dagegen als Hilfe, die das Ergebnis relativiert.
- **Neues lernen**: Vormachen mit hörbaren Gedanken, dann eine teilweise vorbereitete Aufgabe, dann eine eigene.
- **Festigen**: aktives Abrufen in wachsenden Abständen. Für Faktenwissen tritt FSRS gegen eine einfache Wiederholungsregel an, verglichen in der Simulation.
- **Mischen**: erst ähnliche Beispiele, später gemischte Aufgaben, bei denen das Kind die passende Strategie selbst wählen muss.
- **Fehler**: Eine einzelne falsche Antwort ist nur eine Vermutung. Eine passende Anschlussaufgabe klärt, ob das Problem beim Stellenwert, bei der Anweisung oder bei der Eingabe liegt.
- **Hilfen**: erst Aufmerksamkeit lenken, dann einen Teilschritt zeigen, dann den Lösungsweg. Danach folgt eine neue, verwandte Aufgabe für einen eigenen Versuch.
- **Anpassung**: rund 80 % Erfolg als Startwert für Übungsrunden, mit eigenen Regeln für Einführung, Erkundung, Automatisierung und Test. BKT oder IRT werden nur übernommen, wenn sie in der Simulation mit neuen synthetischen Lernenden das Behalten besser vorhersagen.
- **Kein Gesamt-Fitness-Wert**: Ein breiter Transfer von Gedächtnisspielen auf schulische Leistungen ist wissenschaftlich schwach belegt.
- **Tests auf vier Ebenen**:
  - Lektionscheck: kurz und unbenotet. Er entscheidet zwischen «nächster Schritt» und «noch ein Beispiel».
  - Modultest: neue Aufgaben aus mehreren Familien, Lösungen mit und ohne Hilfe getrennt ausgewiesen. Nach einigen Tagen folgt eine Wiederaufnahme.
  - Kapiteltest: mehrere Kompetenzen und Darstellungen, mindestens eine Aufgabe zum Begründen oder Anwenden.
  - Semester- oder Jahresbilanz: Prüfplan pro Fach. Praktische Dokumentationen ergänzen die digitalen Aufgaben.
- **Keine Schulnoten**: Statt einer Note gibt es Aussagen wie «Vergleicht gleichnamige Brüche sicher, braucht bei unterschiedlichen Nennern noch eine Zeichnung».

## 5. Inhaltsproduktion mit KI-Agenten
Der Umfang der Gesamtvision bleibt bei über 400 Modulen und über 15'000 kuratierten Aufgaben, ergänzt durch Generatoren. Freigegeben wird ein Lernziel, wenn es genügend unterschiedliche Aufgabenfamilien, Hilfen, Transferaufgaben und verlässliche Bewertung hat. Die reine Anzahl entscheidet nicht.

Die Pipeline:
1. **Lernziel**: Der Autor-Agent beschreibt Tätigkeit, Vorwissen und beobachtbaren Nachweis und gibt den Kompetenzcode an. Der Kritiker-Agent prüft die Passung zum Lehrplan anhand der öffentlich zugänglichen Kompetenzbeschreibungen.
2. **Aufgabenfamilie**: Auftrag, Audiotext, Darstellungen, alle gültigen Lösungen, zulässige Varianten, typische Fehlvorstellungen, Hilfen, Barrierefreiheit und Rechtevermerk. Gespeichert wird als versioniertes JSON nach festem Schema.
3. **Unabhängiges Lösen**: Ein Löser-Agent ohne Lösungsschlüssel und mit anderem Kontext findet alle Wege. Abweichungen zum Schlüssel gehen zurück an den Autor. Weitere Agenten prüfen Mehrdeutigkeit, Leselast, Schweizer Sprachgebrauch und alternative richtige Wege.
4. **Generatoren**: Jede Aufgabe ist über Version und Startwert reproduzierbar. Pro Generator laufen über eine Million Startwerte gegen Invarianten: lösbar, Lösung korrekt, keine doppelten Optionen, keine versteckten Hinweise, Einheiten stimmen, Grenzen des Zahlenraums eingehalten.
5. **Simulierte Erprobung**:
   - Schülermodelle mit Fehlvorstellungen müssen die vorgesehenen Fehler auch tatsächlich erzeugen, und die Diagnose muss sie erkennen.
   - Persona-Agenten bedienen die Aufgabe über die Oberfläche.
   - Automatische Audits prüfen Barrierefreiheit (performAccessibilityAudit), Zielgrössen (mindestens 60 pt im Modus für Zyklus 1) und den Audioanteil (jede Aufgabe für Zyklus 1 ist ohne Lesen lösbar).
6. **Freigabe**: Ich gebe stichprobenweise und bei allen auffälligen Aufgaben frei. Jede Familie hat Version und Änderungsverlauf. Fehlerhafte Aufgaben lassen sich zurückziehen, betroffene Wertungen werden nachträglich korrigiert.

Beispiel für die Redaktion: Bei «Addition mit Zehnerübergang bis 20» muss der Übergang tatsächlich stattfinden. Verdoppeln oder Zerlegen sind gültige Wege. Soll ausdrücklich «zur Zehn ergänzen» gezeigt werden, verlangt die Aufgabe diesen Weg über das Material. Aus der Zahl 15 allein lässt sich die Strategie nicht ableiten.

Die Kennzeichnung «fachlich geprüft» heisst hier: von unabhängigen Agenten und von mir geprüft. Ein Gutachten von Fachpersonen ist es nicht, und die App sagt das auch so.

## 6. Motivation, Inklusion und Abgrenzung
- **Schweizreise mit echten Tätigkeiten**: In Luzern eine Schifffahrt nach einem selbst erstellten Fahrplan planen, im Jura Spuren vergleichen, im Tessin eine Begrüssung hören. Jüngere Kinder legen Münzen für ein Billett, ältere vergleichen Verbindungen und begründen ihre Wahl.
- **Schneller Einstieg**: Bildprofil, dann «Weiterlernen», «Etwas entdecken» oder «Wiederholen». Anweisungen lassen sich erneut anhören. Während der Aufgabe tritt die Karte in den Hintergrund.
- **Runden mit Ende**: Nach 5 bis 10 Minuten zeigt die App eine konkrete Entdeckung des Kindes. Pausen kosten nichts. Es gibt keine Serien mit Verlustangst, keine Werbung, keine Lootboxen und keine In-App-Käufe.
- **Belohnung für Eigenständigkeit und Neugier**: Ein persönliches Reisebuch mit eigenen Werken. Auch Kinder, die mehr Hilfe brauchen, entdecken die ganze Schweiz.
- **Barrierefreiheit in jedem Aufgabentyp**:
  - Antippen statt Ziehen, Form oder Muster zusätzlich zur Farbe, eine visuelle Alternative zu Audio
  - VoiceOver, Schaltersteuerung, Hardware-Tastatur, grössere Schrift und Abstände, reduzierte Bewegung, Bedienung für Linkshänder
  - Bei Alternativen hält die App fest, welche Kompetenz weiterhin beurteilbar ist.
- **Förderung**: Bildwortschatz und gesprochene Aufträge für Kinder mit Deutsch als Zweitsprache. Strukturierte Mengenbilder bei Schwierigkeiten mit Zahlen. Schrift, Grösse und Abstand sind wählbar, ohne Wirksamkeitsversprechen einer speziellen Schrift.
- **Abgrenzung**: Bestehende Apps (ANTON, Mindsteps, Kaligo) analysiere ich nur über öffentliche Informationen. Die Positionierung von Chnobel ist die Verbindung aus freiem Lösungsweg, kindgerechter Handschrift, nachvollziehbarem Lehrplanbezug, praktischen Aufträgen, vollständig offline nutzbarem Kern und ehrlicher Kennzeichnung der Nachweise.

## 7. Technik und Datenschutz
- SwiftUI, Swift 6, Observation und SwiftData. iPadOS ist die Referenzplattform, das iPhone bekommt grosse Eingabeflächen, der Mac Tastatur und Maus. Mindestens iOS/iPadOS 18, flüssig auf meinem ältesten Gerät.
- Swift Packages: CoreDomain, CurriculumKit, TaskEngine, InputKit, RecognitionKit, LearningEngine, MotivationKit, VoiceKit, ContentPacks und Feature-Module pro Fach.
- Drei Schnittstellen sind besonders streng definiert:
  - RecognitionKit liefert mögliche Lesarten mit Unsicherheit.
  - TaskEngine bewertet eine bestätigte Eingabe gemäss Lernziel.
  - LearningEngine entscheidet, was diese Beobachtung für den Lernpfad bedeutet.
- Inhalte, Bewertung und Lernstandsberechnung tragen je eigene Versionen. Tests umfassen Swift Testing, UI-, Snapshot- und Inhaltstests, Updates mit alten Datenbeständen, unterbrochene Migrationen, Profilwechsel und die Wiederherstellung nach einem Absturz.
- **Simulationsumgebung als eigenes Paket** («LearnerSim»): synthetische Lernende, Persona-Agenten und der Handschriftgenerator. Läuft in der CI und erzeugt Berichte.
- **Daten**:
  - mehrere lokale Bildprofile ohne Konto
  - ein Bereich für Erwachsene mit eigener Sicherung, Berichten, Zeitlimiten, Export und Löschung
  - keine Netzwerkzugriffe, keine Drittanbieter-SDKs, Privacy Manifest «keine Daten erhoben»
  - Rohhandschrift und Stimme verlassen nie das Gerät
  - Datenschutz-Folgenabschätzung und Prüfung gegen die App-Store-Regeln der Kids Category mache ich selbst anhand öffentlicher Regelwerke
- **Später**: Der optionale iCloud-Sync für die Geräte einer Person und ein Lehrpersonenbereich (lokal, ClassKit) sind als Funktionen vorbereitet. Sie gelten als «nicht mit realen Schulen erprobt».

## 8. Risiken und Gegenmassnahmen
- **Synthetische Handschrift bildet echte Kinder schlecht ab.**
  - Gegenmassnahme: vorsichtige Rückfrageschwellen, Ziffernblock immer erreichbar, Handschriftbewertung abschaltbar, Status «unbestätigt».
- **Die KI-Agenten teilen dieselben blinden Flecken.**
  - Gegenmassnahme: Verschiedene Modelle oder Kontexte für Autor und Prüfer, deterministische Validatoren, eine Fehlerbibliothek aus der Literatur, meine eigene Stichprobe und ein Register bekannter Schwächen.
- **Die Simulation bestätigt nur ihre eigenen Annahmen.**
  - Gegenmassnahme: Schülermodelle stammen aus dokumentierten Fehlvorstellungen der Fachliteratur, nicht aus dem App-Code. Die Simulationen laufen gegen absichtlich eingebaute Fehler (Mutationstests) und werden als «simuliert» berichtet.
- **Bedienhürden für Sechsjährige bleiben unentdeckt.**
  - Gegenmassnahme: harte Regeln. Keine Pflicht zu lesen, grosse Zielflächen, höchstens eine Hauptaktion pro Bildschirm, Audio überall, Rückgängig überall. Persona-Agenten mit starken Einschränkungen.
- **Die App überschätzt die Beherrschung.**
  - Gegenmassnahme: unbekannte Aufgabenfamilien, verzögerte Wiederaufnahme, Transferaufgaben.
- **Die Inhaltsmenge wächst schneller als die Qualität.**
  - Gegenmassnahme: Abdeckung pro Kompetenzstufe und Handlungsaspekt messen und Lücken vor neuen Varianten schliessen.
- **Sprach- oder Bedienhürden erscheinen als Fachschwäche.**
  - Gegenmassnahme: Leselast, Eingabeart und fachliche Hilfe getrennt erfassen.
- **Rechtliche Risiken bei Inhalten.**
  - Gegenmassnahme: nur eigene oder gemeinfreie Inhalte, Rechteverzeichnis, keine Lehrplantexte im Wortlaut.

## 9. Roadmap (Ziel: interner TestFlight-Build)
- **Phase 0: Fundament**
  - Inhalt: Luzerner Kompetenzmatrix für Zyklus 1 und 2 (Codes und eigene Lernziele), Inhaltsschema, Agenten-Pipeline, Design-System für beide Altersgruppen, Rechteverzeichnis, Architektur, erste Version von LearnerSim.
  - Kriterium: Für jede Pilotaufgabe sind Lernziel, zulässige Eingaben, Nachweis und Rückmeldung festgelegt.
- **Phase 1: erster vollständiger Lernweg**
  - Inhalt: «Zahlen bis 20» mit Material, Finger, Pencil, Ziffernblock, Vorlesen, Hilfen, Lernstand und Erwachsenenansicht. Dazu ein kleines Modul zur Zuordnung von Lauten und Buchstaben.
  - Kriterium: läuft offline. Automatische Tests, Tests auf meinen Geräten und offene Nachweise sind getrennt ausgewiesen.
- **Phase 2: Handschrift-Labor**
  - Inhalt: synthetischer Generator, Modellvergleich, Kennzahlen, Latenzmessung, Persona-Tests.
  - Kriterium: Die Zielwerte auf den synthetischen Testmengen sind erreicht, und die Rückfrage-Logik ist abgestimmt.
- **Phase 3: Mathematik und Deutsch, 1.–2. Klasse**
  - Inhalt: alle priorisierten Kompetenzstufen, Generatorprüfungen, barrierefreie Varianten, Berichte, verzögerte Lernkontrollen.
  - Kriterium: Abdeckungsmatrix vollständig. Die Simulation zeigt, dass Fehlvorstellungen erkannt und gezielt gefördert werden.
- **Phase 4: 3.–4. Klasse und Profil Bern**
  - Inhalt: NMG, erste Fremdsprache, Medien und Informatik, erste praktische Lernwege.
  - Kriterium: Beide Kantonsprofile laufen im selben Kern korrekt.
- **Phase 5: vollständige Primarstufe**
  - Inhalt: bis zur 6. Klasse, zweite Fremdsprache, Projekte, praktische Aufträge, vorbereiteter Lehrpersonenbereich.
  - Kriterium: Pro Fach ist nachvollziehbar, was angeboten, automatisch beurteilt, praktisch dokumentiert und noch nicht abgedeckt ist.
- **Phase 6: interne Evidenzbilanz**
  - Inhalt: Simulationsbericht, Abdeckungsmatrix, Register offener Nachweise, Liste aller Aussagen mit ihrem Belegstatus.
  - Kriterium: Kein Text in der App behauptet mehr, als belegt ist.
- **Phase 7: weitere Regionen**
  - Inhalt: PER und Tessin mit eigenen Agenten-Pipelines pro Sprache.
  - Kriterium: gleicher Standard wie die Deutschschweizer Fassung, auch für die automatische Prüfung.

## 10. Was ohne reale Personen nicht belegbar ist
- die Genauigkeit der Handschrifterkennung bei echten Kindern
- die Verständlichkeit für Sechsjährige
- Motivation und freiwillige Rückkehr
- die Lernwirksamkeit
- Fairness über verschiedene Gruppen von Kindern
- die Feinheiten des Schweizer Sprachgebrauchs aus Sicht von Lehrpersonen

Diese Punkte führe ich als offene Nachweise. Die App kompensiert sie durch vorsichtige Voreinstellungen und durch Steuerung durch Erwachsene.

# Meine Frage an dich

Wie lässt sich dieser Plan perfektionieren, wenn Kosten, Aufwand und Zeit keine Rolle spielen, die Randbedingung «keine externen Personen» aber strikt gilt? Beurteile ihn kritisch aus der Sicht einer erfahrenen Schweizer Primarlehrperson, einer Lernforscherin, eines Senior-iOS-Architekten, einer ML-Ingenieurin für Handschrift und eines Game-Designers für Kinder. Konkret:

1. Wie realistisch kann synthetische Handschrift sechs- bis achtjährige Kinder nachbilden? Welche Generatoren, Störmodelle und Testverfahren kommen echten Daten am nächsten?
2. Wie macht man eine Redaktion aus KI-Agenten robust gegen gemeinsame Fehler? Welche Rollen, Prüfregeln und unabhängigen Kontrollen fehlen?
3. Wie simuliert man Lernende und Bedienung durch Kinder so, dass die Simulation nicht nur die eigenen Annahmen bestätigt? Welche Fehlvorstellungen aus der Fachliteratur gehören zwingend in die Bibliothek?
4. Welche Lehrplan-, Schweiz- und Fachfehler stecken noch im Plan?
5. Welche Gestaltungsregeln ersetzen am besten fehlende Tests mit Kindern (Bedienung, Verständlichkeit, Motivation ohne Manipulation)?
6. Welche Aussagen darf die App unter diesen Bedingungen machen und welche nicht, und wie zeigt man das Eltern verständlich?

Antworte mit einer priorisierten Liste konkreter Verbesserungen (Wirkung hoch/mittel/tief), den grössten Risiken samt Gegenmassnahmen und einer überarbeiteten Roadmap. Schlage keine Massnahmen vor, die externe Personen erfordern.
