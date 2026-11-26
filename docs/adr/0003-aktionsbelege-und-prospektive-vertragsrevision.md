# ADR 0003: Aktionsbelege und prospektive Vertragsrevision

Status: verbindlich als prospektive Produktentscheidung; ratifiziert am 2026-11-26, keine Produktfreigabe
Datum: 2026-11-24
Geltung: ausschliesslich neue, explizit versionierte Entwicklungskandidaten nach Ratifikation. Keine Implementierungs-, Integrations-, Abnahme- oder Releasefreigabe.

## Anlass und Quellenbindung

Die Originalreviews zur Referenz `b8cd111453b2c44d28a5fc21125c4f9dbc95877e` und zum iPad `d71acbe65a602f091840ed5fa7e6069a157843c2` bleiben FAIL. Die Reparaturen `107f524a0529e84fb5dad78af7a7204edb6f649e` und `c1ad063851f568eb3e376fdb7ca7802a59cb0d1b` sind neue, gesondert zu pruefende Kandidaten. Ihre eigenen gruenen Tests sind kein fremdes Urteil.

Normative Grundlagen: Masterprompt 1.4/1.5, 5.1–5.9, 6.2, 9, 11, 15.6, 18 und 21; ADR 0001/0002. Der vorherige Entscheidungsentwurf und die drei unveraenderten Voten werden verlustfrei unter `steuerung/gedaechtnis/entscheide/2026-11-24-reparatursemantik/` archiviert. Das Indexmanifest bindet ihre Originalbytes. Oeffentliche Fachgegenproben sind kein verdeckter Abnahmesatz.

## Stimmen zum vorherigen Entwurf, nicht zum vorliegenden Text

- Architekt: D1 JA, D2 JA, D3 JA, D4 JA, D5 AENDERUNG, D6 JA.
- Didaktik-Kritik Mathematik: D1 JA, D2 JA, D3 JA, D4 JA, D5 AENDERUNG, D6 JA.
- Red-Team: D1 AENDERUNG, D2 AENDERUNG, D3 JA, D4 AENDERUNG, D5 AENDERUNG, D6 JA.

D1/D2/D4 hatten eine zustimmende Mehrheit, D3/D6 einstimmige Zustimmung. D5 verlangt in allen Voten eine Konkretisierung. Dieser konsolidierte Text nimmt die gemeinsamen D5-Forderungen und die strengeren, nicht widersprechenden Red-Team-Praezisierungen auf. Die neue Zeitfensterdefinition und Versionsform werden ausdruecklich zur Ratifikation gestellt; keine neue Stimme wird erfunden. Die unabhaengigen Red-Team-Befunde bleiben auch bei Mehrheitsbeschluss erhalten. Quellenwahrheit, Rechte und Testergebnisse sind nicht Gegenstand einer Abstimmung.

## D1: Historischer Kindbeleg, aktuelle Wirksamkeit und Undo

1. Jede Wegbehauptung braucht einen konkreten Kind-Handlungsbeleg, gueltige Materialprovenienz, den zu dieser Handlung gehoerenden Hilfezeitpunkt und einen getrennten Beleg ihrer aktuellen Wirksamkeit. Gleiche Endmengen oder Endpositionen allein genuegen nicht. `history.ten.child` allein belegt keine historische Hilfefreiheit.
2. Kind legt frei 10/5, spaeterer Hinweis ohne neue Materialhandlung: der erhaltene Kindbeleg wird nicht rueckwirkend angeleitet.
3. Kind verlaesst seine Darstellung und erreicht sie nach Zielhilfe durch einen eigenen neuen Zug oder sein eigenes wirksames Undo erneut: neuer aktueller Kindanker nach Hilfe. Auch ein Plattchen an seiner Anfangsposition kann diese neue Handlung belegen. Der fruehere freie Beleg bleibt nur historisch und benoetigt eigenen zeitlichen Wortlaut/eigene Regel.
4. App-Detour mit App-Undo darf den urspruenglichen Kindanker nur dann wieder wirksam machen, wenn exakt die erhaltene Kind-Provenienz nachgewiesen ist: gleiche Materialidentitaeten und wirksame Kindbeitraege, keine dazwischenliegende Kind-Neuherstellung, keine relevante Luecke/Invalidierung, keine unbelegte Abhaengigkeit. Keine neue Kindhandlung wird erfunden.
5. Ein inverser neuer App-Zug ist kein Undo. App stellt nach ihren neuen Bewegungen dieselbe Menge her: daraus folgt kein aktueller Kind-Wegbeleg. Ein unabhaengig gueltiger Ergebnisbeleg bleibt nutzbar.
6. App-Demo, App-Undo, Kind wiederholt: die erhaltene Zielhilfe bleibt erinnert. Eine Bedienanforderung des Kindes ist nicht automatisch eine fachliche Kind-Materialhandlung. `action.undone.actor` muss zum urspruenglichen Bewegungsakteur passen; Fehlakteure bleiben Integritaetsfehler.
7. Historie, aktueller freier Weg und aktueller angeleiteter Weg werden getrennt geprueft. Bei gemischten oder lueckenhaften Abhaengigkeiten keine Wiederbelebung eines alten freien Ankers ohne Beleg. Eine reine Ergebniseingabe verankert Material nicht neu.

## D2: Dreiwertiges, objekt- und zeitbezogenes Wissen

1. Ereignisidentitaet, aktuelle Antwortaktivitaet, Eingabemodus, Position jedes Plattchens und Undo-Abhaengigkeit werden getrennt gefuehrt. Unbekannt bedeutet weder sicher inaktiv noch sicher unveraendert. Eine bereits sicher zurueckgenommene Identitaet wird durch eine Luecke nicht wieder aktiv.
2. Antwort 15 oder 14, danach relevante Luecke, keine frische Antwort: aktuelle Richtigkeit und aktuelle Abweichung unbekannt. Die historische Eingabe bleibt erhalten. Keine fachliche Fehlbewertung aus einer Lesart oder automatisch uebernommenen Erkennung.
3. Nach Luecke kann eine neue gueltige direkte oder korrigierte Antwort wieder ihre enge Rueckmeldung tragen. Referenzierte Ruecknahme darf nicht allein wegen unbekannter alter Aktivitaet scheitern. Neue Eingabebeobachtung kann Moduswissen wiederherstellen. Ohne neue Luecke/Wechsel bleibt ein anschliessender bewiesener Moduswiderspruch ein Fehler.
4. Neu beobachteter Zug beweist die betroffenen Zielpositionen. Ein unmittelbar danach bewiesener Ausgangszonenwiderspruch bleibt `wrong_source`, auch nach frueheren Luecken. Unbekannte Positionen anderer Plattchen werden nicht still aus dem Anfang uebernommen.
5. Vollstaendig neu beobachtetes Material mit gueltigen Kindhandlungen kann den eigenen dargestellten Weg erneut belegen. Fruehere unbeobachtete Hilfe bleibt unbekannt; ein sicher beobachteter positiver Zielhinweis bleibt dagegen wahr. Teilweiser Neuaufbau belegt keinen vollstaendigen Weg.
6. Bekannte doppelte Ruecknahmen, fremde/verwaiste Referenzen, falsche Referenztypen/Akteure und frisch bewiesene Undo-Konflikte bleiben Integritaetsfehler. Unbekannte Abhaengigkeit ist kein bewiesener Konflikt. Keine erfundenen Zwischenereignisse.
7. **Prospektive Zeitfensterdefinition:** Eine explizite Lueckenmeldung an Sequenz m mit `sinceSeq = s` umfasst mangels engerem unabhaengigen Endbeleg das unsichere Fenster s bis einschliesslich m. Beobachtungen innerhalb dieses Fensters koennen ihre historische Existenz belegen, aber keine sichere aktuelle Fortgeltung am Fensterende. Die Meldung selbst kann keine neue Antwort/Position beweisen. Erst danach frische direkte Beobachtungen koennen betroffenes Wissen erneuern. Das Fenster muss schema- und semantikseitig geprueft sein; s darf nicht nach m liegen. Keine stillschweigende engere Endgrenze.
8. Eine echte Sequenzluecke macht das vorherige aktuelle Wissen vor Verarbeitung des naechsten gelieferten Ereignisses unbekannt. Dieses neue Ereignis kann seine eigenen direkt beobachteten Fakten wiederherstellen. Explizite und Sequenzluecken wirken fuer dasselbe unsichere Intervall gleich. Spaete Meldungen rechnen den ueberlappten Nachweis neu; historische Schritte vollstaendig davor bleiben erhalten. Zeitstempel allein ueberschreiben die Sequenz-/Fensterbindung nicht.
9. G4 ist explizit neuer Vertragsgrenzfall: Eingabe seq 1, Antwort 15 seq 2, Lueckenmeldung seq 3 mit sinceSeq 1, Abschluss seq 4 -> aktuelle Ergebnisentscheidung unbekannt. Eine erst nach seq 3 neu beobachtete gueltige Antwort muss wieder anerkennbar sein. O01 bleibt historisch eine offene Grenze, kein nachtraeglicher alter FAIL-Grund.

## D3: Symmetrischer Zehnerweg und Mustergrenzen

- Beobachteter Kindweg von 8/7 nach 5/10 ist ebenso ein Zehnerweg wie 10/5, mit gleicher Pruefung von Identitaeten, Provenienz, Hilfe und Abgabe. Einzel- und Teilzuege sind zu beruecksichtigen. Der Wortlaut darf keine falsche Links-rechts-Zuordnung behaupten.
- Rein appseitige Darstellung, unveraendertes Anfangsmaterial oder eine wirkungslose Handlung beweisen keinen selbst dargestellten Kindweg. Mengenerhaltung allein reicht nicht.
- 7+7+1 bleibt ein eigener gueltiger Alternativweg. Ein vollstaendig beobachtetes anderes Layout darf den spezifischen Zehnerfakt falsch machen, beweist aber nicht «kein gueltiger Rechenweg». Eine unvollstaendige Musterliste ergibt fuer den breiten Wegclaim unbekannt statt ein pauschales fachliches Negativurteil.
- Positive Pflichtfaelle fuer 5/10 ohne Zielhilfe und nach Zielhilfe, App-Gegenfall und ungesicherte Provenienz werden vor Umsetzung festgelegt; nicht dauerhaft nur den Ergebnisclaim als Ersatz zaehlen.

## D4: Invalidierung folgt den tatsaechlichen Beweisabhaengigkeiten

1. Strukturelle Ereignis-/Referenzintegritaet wird vor fachlicher Invalidierung geprueft. Spaetere Invalidierung heilt weder eventId-/seq-Konflikt noch `wrong_source` oder Akteursfehler. Ein unabhaengiger Ergebniswert ueberdeckt keine ungueltige Spur.
2. Kontextgueltigkeit und Gueltigkeit jedes verwendeten Belegs sind getrennt. Abhaengigkeiten umfassen auch Anfang/Abgabe, aktuelle Antwort, Eingabe-/Lesartprovenienz, Materialherkunft, Handlungsanker und die Beobachtungsabdeckung negativer Voraussetzungen. Globale `observation.valid` wird nicht ersatzlos entfernt oder pauschal wahr gesetzt.
3. Invalidierter unbenutzter Selbstbericht oder alleiniger Materialbeleg sperrt keine unabhaengige direkte 15 mit gueltiger Eingabe und Abgabe. Abhaengige Wegclaims verlieren ihren Beleg. Invalidierte Antwort oder notwendige Eingabe/Lesart sperrt dagegen genau diese Antwortkette.
4. Invalidierung ist kein Undo der realen Welt: invalidierter Hinweis wird nicht zu bewiesener Hilfefreiheit; invalidierter Zug stellt nicht automatisch alte Positionen her. Ohne unabhaengige weitere Evidenz bleibt der betroffene Hilfestand unbekannt. Verbleibender nachgewiesener Zielhinweis bleibt wahr.
5. Invalidierung der aktuellen Antwort reaktiviert keine alte zurueckgenommene Antwort. Eine vollstaendig unabhaengige neue Antwort darf wieder eng beurteilt werden. Alternative Beweise sind nur mit eigener gepruefter Gueltigkeit nutzbar.
6. Notwendiger gemeinsamer Anfangs-/Abschlussbeleg sperrt alle von ihm abhaengigen Claims. Inhaltsrueckzug und passende Profilloeschabsicht bleiben harte Sperren des betroffenen Bereichs. Keine Behauptung physischer Loeschung allein aus der Absicht. Fremde/nicht vorhandene eventIds bleiben Fehler.

## D5: Zielhilfe, allgemeine Hilfe und Beobachtungsabdeckung

Drei getrennte Fragen: allgemeine App-Unterstuetzung, tatsaechlicher Hinweis auf den konkreten Zielschritt und vollstaendig beobachtetes/klassifiziertes relevantes Hilfefenster. Hilfe ist beobachtetes Angebot, kein Beweis ihrer mentalen Wirkung.

- Keine Hilfe bei vollstaendig beobachtetem Fenster: Zielhilfe falsch; enger Ohne-Zielhinweis-Claim muss erreichbar sein.
- Ausschliesslich nachgewiesene 7+7+1-Demo, App-Undo, danach eigener 10/5- oder 5/10-Weg: allgemeine Hilfe wahr, vorherige Zehnerhilfe falsch. `attempt.ten = must_claim`, `attempt.ten.guided = must_not_claim`; gueltiger Weg und direktes Ergebnis bleiben anerkannt. Niemals «voellig selbststaendig» oder «Strategie selbst gewaehlt» daraus machen.
- Demo/Zielwirkung oder ein relevanter Kanal unbestimmt: spezifische Zehnerhilfe unbekannt, beide spezifischen Hilfeclaims unentscheidbar. Gueltiger eigener Weg und Ergebnis bleiben nutzbar. Ein sicher beobachteter positiver Zielhinweis wird durch weitere Unbekanntheit nicht aufgehoben.
- Tatsaechlicher Zehnerschritt/-hinweis vor Kindhandlung, auch mit anschliessendem Undo: Zielhilfe wahr, spezifischer Guided-Claim positiv, Ohne-Hinweis-Claim gesperrt.
- Zielhilfe erst nach weiter wirksamer eigener Handlung: D1 gilt. Vor einem neuen Kindanker bleibt der erhaltene Hinweis gespeichert.

«Vollstaendig beobachtet» betrifft alle relevanten Zwischenzustaende und Kanaele: Material, Hervorhebung, Einrasten, Farbe/Form, Audio, VoiceOver. Das Etikett «Doppelweg» oder eine lueckenlose seq-Folge ist kein Selbstausschluss eines Zehnersignals. Zulaessige Hilfeziele und Klassifikationsregeln sind vor dem Lauf versioniert. Verdecktes Zehnersignal in einer als neutral etikettierten Demo muss beim unabhaengigen Bildschirm-/Audio-/Zugangsabgleich scheitern. Synthetische Adapterbelege sind kein UI-Nachweis.

Zustandsfremde UI-Hilfe aus IPAD-03 bleibt eigenstaendig zu pruefen: 8/7, 9/6, 10/5, 7/7/1 und Undo, sichtbarer Text gegen protokollierten Text. Korrekte Metadaten allein heilen keinen falschen Auftrag.

## D6: Prospektive Revision und unveraenderte alte Urteile

1. Vorgesehene neue gemeinsame Vertragslinie: `produkt/vertraege/v2/`, Schema-/Faktenkatalogfassung `2.0.0`, explizit neue Regel- und Kandidatenbindung. Die konkrete vollstaendige Feld- und Fallliste wird vor Implementierung als eigenes Revisionsmanifest eingefroren und fremd geprueft. Die vorliegende Entscheidung ersetzt dieses Manifest nicht.
2. `v0`, `v1`, alte offene Sollfaelle, Reviewberichte und Kandidatenbytes bleiben unveraendert reproduzierbar. Alte Daten werden nicht still als v2 interpretiert. Keine automatische Migration oder Wiederberechnung unter anderer Revision ohne expliziten, geprueften Weg. Keine alten Tests entfernen, ueberspringen oder umetikettieren.
3. Pflichtkonfliktregister vor neuer Umsetzung:
   - `beobachtung-invalidiert` / `OpenTraceTests.test_spur_beobachtung_invalidiert`: nur Materialereignis `6537640f-c982-5d73-81f2-2cd534cb687f` invalidiert; unabhaengige direkte Antwort `34557498-a1e7-5249-b3dd-408be7928e9e`. Altes Ergebnis-Soll `must_not_claim` bleibt in v1; neues v2-Soll `must_claim`, abhaengige Wegbelege bleiben gesperrt.
   - `observation.valid`, `missing_validity_guard`, Regeln `sum15.result`, `sum15.ten`, `sum15.guided`, `sum15.alternative`, `sum15.path`: globalen Waechter durch dokumentierte Kontext-/Claimbeweis-Gueltigkeit ersetzen, nicht entfallen lassen.
   - `board.ten.child`, `board.path.child`, `history.ten.child`, `support.ten.before`, `support.doubles.before`: D1-/D3-/D5-Semantik und Wortlaut gemeinsam versionieren.
   - `unrelatedAppMovementIsNotInventedAsATenHint`: alter unklassifizierter Fall bleibt unknown; neu vollstaendig klassifizierter exklusiver Doppelwegfall muss engen freien Claim pruefen. Keine stille Umdeutung desselben alten Inputs unter alter Version.
   - `appDemoIsNotAnOwnPathAndRepetitionIsNotIndependent`: App-Ruecknahme akteurgetreu, Kind-Fehlakteur weiterhin negativ. Hilfeerinnerung bleibt.
   - `R01`, `R02`, `R03`, `R07`, `R08`, `R09`, `X10` sowie G4 und Invalidierung eines Hilfebelegs bleiben ausdrueckliche Gegenproben, keine Sollwerte aus Implementierungsausgaben ableiten.
4. Das alte Inventar umfasst laut Originalmanifest 46 gueltige und 12 ungueltige Spuren, fuenf Regeln und 230 Entscheidungen. Die neue Revision bildet jede alte Fall-ID revisionsgebunden ab, protokolliert jede fachlich begruendete Erwartungsdifferenz und fuegt Faelle hinzu. Vorher festgelegte Gesamt-/Teilzahlen und Fallidentitaeten werden aus dem Manifest validiert, nicht nach gruener Ausgabe angepasst. Alte Fallzahlen sind kein neuer Laufnachweis.
5. Pro geaenderter Erwartung: alte ID/Revision und Wert, neuer Wert, betroffene Fakten/Claims/Regeln, normative Begruendung, Gueltigkeitsbeginn und Gegenfall gegen Ueberanerkennung. Bei fehlender Zuordnung oder Widerspruch bleibt die Revision gesperrt.
6. Vorher-/Nachher-Matrix: alter Kandidat/alter Vertrag unveraendert; neuer exakter Kandidat/neuer Vertrag; alle offengelegten Defektspuren gegen den neuen Vertrag. Nicht beschlossene Erwartungsdifferenzen scheitern. Beide Fehlerarten separat pruefen, alle Positiv-/Verbots-/Unklarfaelle behalten. Ein engerer Ersatzsatz ist kein PASS fuer einen ausgelassenen berechtigten spezifischen Claim.
7. Replay-/JSON-Restore, identische Redelivery, geaenderte Zustellordnung, Hilfe-/Undo-/Lifecyclevarianten pruefen. Integritaetsveto, Korrekturprovenienz, Abgabe, Rueckzug, Loeschabsicht, positive Fallzahlen und Kandidaten-/Digestbindung bleiben zwingend.
8. Swift und Python werden an gemeinsam eingefrorenen Eingaben/Fassungen auf Fakten, Claim-IDs, Entscheidungen, Wortlaut, Fehlerkategorien und Dedupe verglichen. Native Swift-/iPad-Ausfuehrung und unabhaengiger Bildschirmabgleich sind eigene Gates. Keine Python-Nachbildung als nativer PASS.

## Folgen und verbleibende Sperren

- Erst Ratifikation dieses Texts und anschliessende fremde Pruefung des expliziten Revisionsmanifests erlauben die neue Umsetzung. Ein Beschluss macht keinen Test gruen und schliesst keinen Befund.
- Drei Reparaturbranches werden separat nachgeprueft. Die Original-FAILs und RT-01 bis RT-15 bleiben erhalten; neue Bewertungen binden neue Kandidaten.
- Technische Identitaetstrennung, authentisierte Freigabe, Offline-/Speicher-/Accessibility-/Hardware-Nachweise, Handschrifterkennung und Apple-Endzustand werden nicht durch dieses ADR ersetzt.
- Ratifikation am 2026-11-26 nach vollstaendigem Ruecklauf `deleg_b54b26ad`: Architekt JA, Didaktik-Kritiker Mathematik JA, Red-Team JA. Der Orchestrator hat drei verschiedene Rollen, COMPLETE, unbedingte Ganztextvoten und den exakten Hash geprueft. Abstimmungsgegenstand war ausschliesslich SHA-256 `0f97e89acd7cb6a2ad937949db57f704596e36c617af5ac31a655ac407975472`. Diese Fassung samt Originalvoten/-berichten bleibt bytegetreu unter `steuerung/gedaechtnis/entscheide/2026-11-26-adr0003-ratifikation/` erhalten; `index.json` bindet Inhalt und Container. Hier wurden nur Status und dieser Entscheidungsvermerk aktualisiert, D1-D6 bleiben wortgleich. RT-16/17 und alle nicht behobenen Befunde bleiben offen. Vor Implementierung ist weiterhin das separate eingefrorene und fremd gepruefte v2-Manifest erforderlich.
