# Reparaturversuch 1: F01–F03

Ausgangskandidat: `b8cd111453b2c44d28a5fc21125c4f9dbc95877e`.
Geltung: lokale Entwicklungsreparatur; **kein Integrationsurteil und keine
Selbstfreigabe**. Der Ausgangskandidat und das fremde Review bleiben unveraendert.

## Reparaturumfang

- **F01:** Antwort- und Bewegungsaktivitaet je ID sind wahr/falsch/unbekannt.
  Eine Luecke macht aktuelle Aktivitaet, Eingabemodus und Stackbasis unbekannt,
  nicht bewiesen inaktiv oder sicher unveraendert. Neue Beobachtungen gewinnen
  Wissen zurueck. Bekannte Ruecknahmen, eindeutige IDs, Akteursbindung,
  Eingabe-/Lesartreferenzen und frische Widersprueche bleiben strikt.
  Ein aeusseres Undo setzt seine bekannten abhaengigen Bewegungen inaktiv;
  eine passende Zone allein darf sie nicht reaktivieren.
- **F02:** Position und Undo-Stack werden pro Plattchen gefuehrt. Ein frisch
  beobachtetes Ziel wird sofort wieder zur verbindlichen Ausgangszone des
  naechsten Zuges. Eine unbekannte Gesamtbeobachtung hebt diese Pruefung nicht
  mehr auf. Bei wieder vollstaendigen Positionen und noetiger Provenienz kann
  auch der aktuelle Weg erneut belegt werden; unbeobachtete Hilfe bleibt offen.
  Damit wird die zuvor dokumentierte Grenze O01 fuer R09 enger, ohne einen
  Snapshot oder einen freien Weg zu erfinden.
- **F03:** Der aktuelle Hilfezeitanker stammt von einer Kind-Materialhandlung,
  einschliesslich eigenem Undo. App-Umweg/App-Undo datiert die erhaltene
  Kind-Handlung nicht um. Eigener Kind-Umweg/eigenes Undo nach Hilfe bleibt
  dagegen aktuell angeleitet. `history.ten.child` bleibt davon getrennt; eine
  historische freie Handlung wird im frueheren Praefix geprueft, nicht als
  aktuelle freie Darstellung ausgegeben.

Die Reparatur fuegt keine neuen Ausgabe-Fakten oder pauschalen Ausnahmewege
hinzu. Fehlende historische Referenzen bleiben Fehler. Provenienz wird aus
bekannten wirksamen Bewegungen gelesen, niemals aus der blossen Gleichheit
von End- und Anfangszonen rekonstruiert.

## Unveraenderte Historie und offene Vertragskonflikte

Schemas, Regeln, `v0`, der v1-Katalog und die drei vorhandenen Testdateien
bleiben bytegleich. Kein bestehendes Soll wird hier umdefiniert. F04–F06
brauchen den gesonderten Vertragsentscheid und eine nachfolgende Revision:

| Befund | Exakter offener Konflikt / Folgeumfang |
|---|---|
| F04 | `R01-spiegelweg-fuenf-zehn`: Review verlangt `attempt.path.displayed = must_claim`, die bisherige Erkennung nur von 10/5 und 7/7/1 liefert `must_not_claim`. Betroffen: `board()`, Faktenkatalog und `sum15.path.json` sowie die Zehnerregeln. Symmetrie und unbekannte, nicht erkannte Layouts muessen im künftigen Vertrag getrennt werden. |
| F05 | `R07-selektive-invalidierung-selbstbericht` und `R08-selektive-invalidierung-material`: Review verlangt Erhalt von `attempt.result.correct`; bisheriges globales `observation.valid = falsch` liefert `must_not_claim`. Der Katalogfall `beobachtung-invalidiert` und sein Export in `offene_spuren.py` erwarten ausdruecklich **alle fuenf** Entscheidungen `must_not_claim`. Betroffen sind Abhaengigkeitsrechnung, Gueltigkeitsfakten, Regelwaechter und die Katalogsummen. Keine stille Aenderung dieses Solls. |
| F06 | `R03-nur-doppelweg-demo-vor-zehnerweg`: Review erwartet keinen belegten Zehnerhinweis. Bisher wird jede App-Bewegung als Ziel `all` gespeichert, was `support.ten.before = wahr` und den spezifischen Guided-Wortlaut aus `sum15.guided.json` erzeugt. Allgemeine Unterstuetzung und belegte Zielhilfe brauchen getrennte Regeln. `demo-wiederholung`, `test_undo_demo_and_replay_same_items_is_still_guided` und `test_undo_does_not_remove_received_help` duerfen dabei nicht Hilfe nach Undo vergessen. |

Die genaue Versionsform und die neuen Erwartungsgruppen sind hier nicht
vorweggenommen. Eine neue Revision muss alte Vertragsfassungen und die alten
Fehler weiterhin reproduzierbar halten. Auch nach F01–F03 bleibt daher das
Review insgesamt offen/gescheitert, nicht freigegeben.

## Ausfuehrbare Regressionen

`tests/test_repair_f01_f03.py` ergaenzt die unveraenderten 165 Bestandstests
um 67 offene Tests: beide Akteure, positive/negative/unbekannte Antworten,
Moduswiedergewinnung, alte und neue Undo-Abhaengigkeiten, lokale Zonenkenntnis,
App- und Kind-Detours auf urspruenglichen sowie anderen Plattchen, Zehner- und
Doppelweg, Luecken, Antwortabstufung und idempotenten Replay.

```sh
export PYTHONDONTWRITEBYTECODE=1
export PYTHONIOENCODING=utf-8
F:/ChnobelRuntime/venv/Scripts/python.exe -B -m unittest discover -s produkt/werkzeuge/referenz/tests -v
F:/ChnobelRuntime/venv/Scripts/python.exe -B -m produkt.werkzeuge.referenz --check-open-corpus
```

Tatsaechlich ausgefuehrt: **232 Tests, OK**; davon der historische Bestand
auch separat **165 Tests, OK**. Der unveraenderte Katalog bleibt bei 46 gueltigen
und 12 ungueltigen Spuren mit 230 Entscheidungen. In den 38 eingefrorenen
Reviewgegenproben stimmen 34 Erwartungen; die vier verbleibenden Abweichungen
sind genau R01, R03, R07 und R08 aus der Tabelle. Das ist kein Gesamt-PASS.

Neue Logs, Kopien der Reviewskripte, unveraenderte Eingabekopien,
Vorher-/Nachherberichte und Bytebindungen liegen ausserhalb Git unter
`F:/ChnobelRuntime/reparaturen/referenz-1/`. Der rote Lauf der neuen Tests vor
Codeaenderung und die zusaetzliche rote Undo-Inferenzgegenprobe bleiben erhalten.
Ein spaeterer unabhaengiger Kontext muss den neuen Commit erneut pruefen.
