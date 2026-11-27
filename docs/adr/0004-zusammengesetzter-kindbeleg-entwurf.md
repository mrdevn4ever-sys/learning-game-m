# ADR 0004: Zusammengesetzter Kindbeleg bei disjunktem App-Detour

Status: verbindlich als prospektive Produktentscheidung; ratifiziert am 2026-11-27, keine Implementierungsfreigabe
Datum: 2026-11-27
Geltung: ausschliesslich eine prospektive Praezisierung von Q-ANCHOR-INTERVENTION. Keine Freigabe des Manifestentwurfs, eines Kandidaten oder eines Releases.

## Anlass und exakter Entscheidungsumfang

ADR 0003 trennt Kindhandlung, aktuelle Wirksamkeit, Materialprovenienz und Hilfezeit. D1.3 verlangt eigenes Wiedererreichen; D1.4 erlaubt das Freilegen unveraenderter Kindprovenienz durch echtes App-Undo. Noch nicht entschieden ist die Kombination einer neuen Kind-Rueckkehr an einem Item mit spaeterem App-Undo an einem anderen Item, wenn erst danach wieder das ganze Ziellayout vorliegt.

Die offene Produktfrage wird hier eng entschieden, nicht durch eine nachtraegliche Auslegung alter Sollwerte. Beobachtete Akteure, Reihenfolgen und IDs sind keine Abstimmungsgegenstaende. Ebenso wenig sind Quellenwahrheit, Testergebnisse oder Rechte abstimmbar. Die tatsaechlichen Dateien haben Vorrang vor der folgenden Beschreibung.

Unveraenderte Grundlage: Manifestentwurf01, SHA-256 `1516d127a688cea5e5a707fbc562e0e70cd43fcd583752be25b1cc3871d95502`; Handoff `970299f1be40510c16eb2c707be39a947023e0eaf80f87f924ea057ea79324df`. Die v2-Inputs und ihre noch offenen Projektionen liegen unter `F:/ChnobelRuntime/specification/v2-manifest-draft-01/`.

- `V2-REV-T07-intervening-child-return`: Input-SHA-256 `1bca7d87e6cd3748c6d6706db46d14cb6c8c046b5471ce6b7726eff2aaa6ec42`.
- `V2-REV-N32-app-restores-after-new-child-return`: Input-SHA-256 `9f68cc6c03bdc47513750bb005ed691c70c4252c430d6508eece0ee0bd90a41f`.
- Beide bisherigen Erwartungsdateien: SHA-256 `a276cdee4da2cb4d2a9622e2577e30601270231d2104871e62a24d628c00c395`, weiterhin `SPECIFICATION_PENDING`.
- Autoritaetscommit fuer ADR 0003: `d84c597a68863929034cff50089e098120c7cb39`. Dessen D1-D6 bleiben unveraendert.

In beiden Inputs: eigener voller Kindweg bei seq 1; expliziter Zielhinweis danach und vor seq 5; Kind-Undo seq 5 erreicht nur 9/5/1; erst App-Undo seq 6 erreicht 10/5/0. Die direkte Antwort 15 stammt aus einer getrennten Eingabekette. Das ist eine Beschreibung synthetischer Vertragsdaten, keine beobachtete iPad-Ausfuehrung.

## Beratung und erhaltener Dissens

Drei frische Rollen haben die begrenzte Frage vollstaendig bearbeitet. Ihre Quelldigests, Abgaben und Ereignisreferenzen wurden separat abgeglichen; keine Rolle hat damit das Gesamtmanifest freigegeben.

- Didaktik-Kritik Mathematik empfiehlt `REQUIRE_CHILD_COMPLETED_LAYOUT`: nach dem Hinweis zeigt die Kind-Rueckkehr nur einen Teilzustand. Die spaetere App-Ruecknahme soll daraus keinen neuen vollstaendigen angeleiteten Kindweg machen. Einzelbeitraege, frueherer freier Weg und richtige Antwort bleiben anerkennbar.
- Architektur und Red-Team empfehlen `COMPOSITE_CHILD_PROOF`, aber nur mit vollstaendiger itemgebundener Herkunftskette, disjunkten Eingriffen, echtem referenziertem App-Undo und ausdruecklich offengelegter App-Beteiligung.
- Alle drei verlangen `PROSPECTIVE_CLARIFICATION_REQUIRED`. Die beiden gleich benannten Empfehlungen sind keine Stimmen zu diesem neuen Ganztext. Die didaktische Gegenposition bleibt als begruendeter Dissens erhalten; sie ist weder unvollstaendig noch widerlegt.

Rohberichte und Entscheidungen: `F:/ChnobelRuntime/reviews/v2-manifest-questions-02/anchor/{didaktik,architekt,redteam}/`. Erste beiden Rollen verlustfrei in `steuerung/gedaechtnis/entscheide/2026-11-27-ankerberatung-teil01/`; Red-Team und neuer Elternabgleich in `steuerung/gedaechtnis/entscheide/2026-11-27-ankerberatung-teil02/`.

## A1: Eng begrenzte Zulassung, keine neue Kindhandlung

Fuer diese disjunkte Konstellation wird ein zusammengesetzter Darstellungsbeleg zugelassen, wenn alle folgenden Voraussetzungen belegt sind:

1. Zuvor wurde eine vollstaendige Kind-Zehnerdarstellung mit gueltigen Materialidentitaeten, Aufgabenherkunft und eigener Kindhandlung beobachtet.
2. Die App hat durch einen konkreten eigenen Materialzug einen Teil dieser Darstellung voruebergehend ueberlagert. Der urspruengliche Kindbeitrag wurde nicht selbst zurueckgenommen.
3. Waehrend dieses App-Detours hat das Kind an einem anderen, fuer die Darstellung relevanten Item einen eigenen Umweg gemacht und durch sein eigenes wirksames Undo tatsaechlich die fruehere Position wieder erreicht. Die beiden Eingriffe betreffen disjunkte Itemmengen. Die Rueckkehr an eine Anfangsposition ist eine neue Materialhandlung und wird nicht ausgeblendet.
4. Erst danach nimmt die App ausschliesslich ihren eigenen Detour durch korrekt referenziertes, akteurgetreues `action.undone` zurueck. Dadurch werden exakt die erhaltenen Kindbeitraege wieder wirksam; es entsteht kein neuer appseitiger Herstellungsbeitrag.
5. Fuer alle notwendigen Items sind Identitaet, Anfangsherkunft, Position, erhaltene Kindbeitraege und einschlaegige Move-/Undo-Abhaengigkeiten bis zur vollstaendigen Wiederwirksamkeit gueltig belegt. Es gibt keine relevante unbeobachtete oder invalidierte Abhaengigkeit, die durch das Einzelitem-Undo nur scheinbar repariert wuerde.

Der neue Kind-Handlungsanker ist die eigene Rueckkehrhandlung. Der erste vollstaendige Wirksamkeitsbeleg ist das spaetere App-Undo. Beide bleiben mit ihren wirklichen Event-IDs, Sequenzen und Akteuren getrennt. Die Apphandlung wird weder zur Kindhandlung noch zum umdatierten Kindanker. Bei T07/N32 sind das Kind seq 5 und App seq 6.

Das ist eine explizite Ausnahme fuer die neue Zusammensetzung nach der Zwischenhandlung, keine Wiederbelebung des unveraenderten alten Gesamtankers nach D1.4. Eine neue inverse Appbewegung, gleiche Endmengen, gleiche Endpositionen, eine blosse Bedienanforderung oder irgendein beliebiger Kind-Teilzug erfuellen diese Ausnahme nicht. Ueberlappende Itemeingriffe, andersartige Kind-Rueckkehrhandlungen und weitere Konstellationen werden hier nicht pauschal zugelassen; sie brauchen eine eigene begruendete Spezifikation. Das setzt anderweitig bereits gueltige Belege nicht ausser Kraft.

## A2: Hilfezeit, Historie und Aussagegrenze

Der zusammengesetzte Vollbeleg entsteht nicht schon beim Kind-Teilanker. Erst die vollstaendige gueltige Kette traegt ihn. Sein Hilfefenster ist an die tatsaechliche neue Kind-Rueckkehr gebunden, nicht an das spaetere App-Undo und nicht an den alten freien Anker. Ein davor belegter Zehnerhinweis erlaubt nur die angeleitete, nicht die aktuelle Ohne-Hinweis-Qualifikation. Undo loescht das Hilfeangebot nicht; eine mentale Wirkung wird nicht behauptet.

Ein historischer angeleiteter Vollbeleg aus dieser Zusammensetzung entsteht fruehestens mit der vollstaendigen damaligen Wirksamkeit. Er verweist ebenfalls auf Kindanker und App-Ruecknahme und wird nicht auf den frueheren Teilzustand zurueckdatiert. Bei T07/N32 entsteht er somit nicht bei seq 5 allein, sondern fruehestens bei seq 6. Der fruehere freie Vollbeleg bei seq 1 bleibt mit seinem eigenen damals belegten negativen Hilfefenster historisch erhalten.

Zugelassen ist ausschliesslich die enge Anerkennung einer wieder vollstaendig wirksamen Darstellung aus nachgewiesenen Kindbeitraegen mit offengelegter App-Ruecknahme. Nicht belegt sind eine nach dem Hinweis allein neu hergestellte ganze Darstellung, eine neue vollstaendige Kindhandlung bei seq 6, selbst gewaehlte Strategie, Verstehen oder Lernwirksamkeit. Eine neue vollstaendige Herstellungsleistung darf nicht bloss aus dem zusammengesetzten Darstellungsbeleg abgeleitet werden. Die didaktische Gegenposition zu dieser begrenzten Anerkennung bleibt nachvollziehbar.

## A3: Positive, verbotene und unbekannte Aussagen

Bei vollstaendig belegter A1-Kette und den jeweils unabhaengig gueltigen Voraussetzungen muss die enge zusammengesetzte Darstellungsrueckmeldung erreichbar sein. Pauschales Schweigen oder nur eine Ergebnisrueckmeldung ist kein Ersatz fuer diesen dann zulaessigen Beleg.

Fuer die zwei gebundenen T07/N32-Inputs lautet die prospektive fachliche Zuordnung am Abschluss:

- `attempt.ten.guided` und `attempt.path.displayed`: positiver zusammengesetzter Darstellungsbeleg, ausschliesslich mit dem engen Wortlaut aus A4 und je eigener gueltiger Regel.
- `attempt.ten`: kein aktueller Ohne-Hinweis-Claim; neuer Kindanker nach dem bekannten Zielhinweis.
- `history.ten.guided`: eigener historischer zusammengesetzter Beleg erst ab seq 6, nicht aus dem aktuellen Label kopiert.
- `history.ten.displayed` und `history.ten.without_hint`: frueherer Vollbeleg seq 1 und dessen eigenes Hilfefenster bleiben erhalten.
- `attempt.result.correct`: die unabhaengige direkte 15 bleibt nach ihrer eigenen Regel anerkennbar. Eine Antwort ersetzt keinen fehlenden Materialbeweis.

Diese Zuordnung ist kein vollstaendiges Reportoracle und keine generische Belegung aller Fakten/Gueltigkeitswaechter. Die allgemeinen Kontext-, Abgabe-, Integritaets- und claimbezogenen Gueltigkeitsvoraussetzungen aus ADR 0003 bleiben zwingend. Der Alternativwegclaim und Q-GUARD-TOTALISATION werden hier nicht neu entschieden.

Ein sicher fehlendes notwendiges Merkmal sperrt die abhaengige positive Kette. Ist eine notwendige Abhaengigkeit nur ungesichert, bleibt sie unbekannt statt bewiesen falsch. Andere gueltige Beweise und unabhaengige engere Aussagen werden getrennt beurteilt. Eine offene Spezifikationsfrage ist weiterhin `SPECIFICATION_PENDING`, kein fachliches unbekannt und kein bestandener Enthaltungsfall.

## A4: Verbindlich gemeinsam zu versionierender enger Wortlaut

Die folgenden Varianten gehoeren zur vorgeschlagenen Produktentscheidung, nicht zu einem bereits geaenderten Katalog. Vor Ausgabe muessen sie in der neuen Manifestfassung mit eigener Regel-/Variantenbindung und den konkreten Belegen verbunden sein:

- Aktuell angeleitet: «Nach dem Hinweis auf den Zehnerschritt hast du ein Plaettchen zurueckgelegt. Erst nachdem die App ihren eigenen Umweg rueckgaengig gemacht hat, ist dein Zehnerweg wieder vollstaendig dargestellt.»
- Aktueller Weg ohne Hilfequalifikation: «Dein Rechenweg mit Material ist nach deiner Rueckkehrhandlung und der Ruecknahme des App-Umwegs wieder vollstaendig dargestellt.»
- Historisch angeleitet: «Du hast in diesem Versuch nach einem Hinweis auf den Zehnerschritt ein Plaettchen zurueckgelegt. Erst nach der Ruecknahme des App-Umwegs war dein Zehnerweg wieder vollstaendig dargestellt. Das ist eine historische Beobachtung.»

Die alten unqualifizierten aktuellen Katalogsaetze genuegen fuer diese zusammengesetzte Nachweisform nicht. Ihre Verwendung ohne Offenlegung der App-Ruecknahme ist durch diesen Vorschlag nicht erlaubt. Historische freie Aussagen behalten ihr eigenes zeitliches Hilfefenster; reine Ergebnisformulierungen bleiben davon unabhaengig. Ohne passende Wortlaut-/Regelbindung bleibt die Umsetzung gesperrt, nicht still auf eine breitere Formulierung zurueckfallen.

## A5: Unveraenderte Grenzen und obligatorische Gegenkontrollen

Die folgenden Kontrollen sind deklarative Anforderungen, keine ausgefuehrten Tests:

- Positiv: `V2-RT17-a1-child-undo-hint` muss weiterhin den unmittelbaren eigenen Wiederaufbau nach Hinweis anerkennen. D1.3 wird nicht auf die neue Ausnahme beschraenkt.
- Negativ: `V2-RT17-b1-app-inverse-hint` darf trotz gleicher Endlage keinen aktuellen Kindweg aus neuer inverser Appherstellung erhalten. D1.5 bleibt unveraendert.
- Unklar: `V2-REV-T05-app-undo-with-lost-provenance` darf durch ein Einzelitem-Undo nicht die gesamte verlorene Provenienz zurueckbekommen. Ein bekannter positiver Hinweis bleibt erhalten. Diese Kontrolle ratifiziert nicht das gesamte bisherige Faktenprofil, insbesondere nicht ein dort projiziertes unbekannt fuer bereits positiv beobachtete allgemeine Hilfe.
- Zusaetzlich braucht die kuenftige Manifestfassung direkte Nachbarn der positiven T07/N32-Kette: App-Undo durch neuen inversen Appzug ersetzt; relevante Luecke zwischen Kind-Rueckkehr und Wirksamkeitsbeleg. Neue IDs/Revisionen und ereignisadressierte Sollwerte sind vor Implementation festzulegen. Die bestehenden Quellen werden dafuer nicht veraendert, und die Nachbarn gelten nicht als schon materialisiert oder ausgefuehrt.
- Der reine App-Detour mit echtem App-Undo ohne eigene Zwischenhandlung bleibt nach D1.4 moeglich. Historisch gueltige freie Belege, korrekt bestaetigte/korrigierte Antworten und andere gueltige Wege werden nicht pauschal unterdrueckt.

## Folgen, Abstimmungsverfahren und verbleibende Sperren

Dieser Ganztext wird gesondert den drei Rollen Architektur, Didaktik-Kritik Mathematik und Red-Team zur vollstaendigen Abstimmung vorgelegt. Nur vollstaendige, unbedingte Ganztextvoten zum selben exakten Bytehash zaehlen; Empfehlungen zu frueheren Texten werden nicht umetikettiert. Hoechstens zwei Kontexte laufen gleichzeitig. Ein Nein und seine Begruendung bleiben erhalten. Ein vollstaendiges Nein verhindert nicht allein eine sonst zulaessige Produktmehrheit; eine bedingte Zustimmung ist dagegen kein unbedingtes Ja. Produktmehrheit ersetzt keinen offenen Faktennachweis und darf keinen nachgewiesenen Normwiderspruch oder Produktfehler wegstimmen.

Bis zur Auswertung aller drei vollstaendigen Voten bleibt dieser Text ENTWURF. Bei Ablehnung oder geforderter Textaenderung keine verdeckte Anpassung unter demselben Hash. Eine neue Fassung verlangt neue Bindung und die erforderlichen neuen Voten. Im Fall einer Ratifikation wird nur Status/Entscheidungsvermerk ergaenzt; der abgestimmte Normtext und die Rohvoten bleiben verlustfrei erhalten.

Auch eine Ratifikation erlaubt noch keine Implementierung. Q-U07, Q-GUARD-TOTALISATION, alle M-Punkte einschliesslich vollstaendiger Feldnormalform, Hilfe-/Wortlautbindung und fallweiser Oracles sowie das separate vollstaendige Manifest-Freeze-/Fremdpruefungsgate bleiben offen. Das neue `B-EVENT-DIGEST-TARGET` wird hier nicht geloest. Erst eine neue vollstaendige Fassung kann die prospektive Zuordnung ausdruecklich aufnehmen. Alte v0/v1-Daten, Entwurf01, Sollwerte, FAILs und RT-16/RT-17 bleiben unveraendert; kein Kandidat wird durch diesen Beschluss gruen.

**Entscheidungsvermerk: Am 2026-11-27 als prospektive Produktentscheidung ratifiziert.** Drei vollstaendige, unbedingte Ganztext-JA zum selben unveraenderten Bytehash: Didaktik-Kritik Mathematik und Architektur aus `deleg_f43220be`, unabhaengiges Red-Team aus `deleg_84b7058f`. Keine verlangte Textaenderung oder zusaetzliche Bedingung. Der Orchestrator hat Rollen, Scope, Berichte, Stimmen und Quellenbindungen geprueft und drei JA maschinell gezaehlt. Abstimmungsgegenstand ausschliesslich SHA-256 `eaabc21a38b1bdc806f37444a6bdee00991004b462f9066d521cbb4b732d3b3c`. Originalfassung, alle Rohvoten/-berichte/-quellen und Elternbelege verlustfrei unter `steuerung/gedaechtnis/entscheide/2026-11-27-adr0004-ratifikation/`; der Index bindet Originalbytes und Container. Elternabschluss `F:/ChnobelRuntime/verification/adr0004-part02/verification.json`, SHA-256 `0a160af5d96fb9095c4f8750cfd1180966ade0e921d240ded309f500394311b6`, bestanden ausschliesslich fuer Ruecklauf-/Quellenbindung. Nur diese Statuszeile und dieser Entscheidungsvermerk wurden gegenueber dem Abstimmungsgegenstand geaendert; der gesamte sonstige Text einschliesslich A1-A5 bleibt wort- und bytegleich. Historische Formulierungen zum Entwurfs-/Abstimmungsverfahren werden nicht verdeckt umgeschrieben. Der fruehere didaktische Dissens bleibt erhalten. B-SPEC-T05-SUPPORT beziehungsweise RT-A4-01 bleibt ein offener Spezifikationskonflikt; A5 genehmigt das widerspruechliche Faktenprofil nicht. Q-U07, Q-GUARD-TOTALISATION, alle M-Punkte, B-EVENT-DIGEST-TARGET, RT-16/17 und das separate vollstaendige Manifest-Freeze-/Fremdpruefungsgate bleiben offen. Keine Manifest-, Kandidaten-, Implementierungs-, Integrations-, Abnahme- oder Releasefreigabe und kein Produkt-/Nativergebnis.
