# Referenzprüfer v1 – offener Leitfall 8 + 7

Eigene Implementierung für P0-03/04/05. **Keine unabhängige Abnahme, keine
Freigabe und kein Nachweis für reale Kinder, Handschrifterkennung oder die
Darstellung auf einem iPad.** Der Prüfer liest nur lokale JSON-Daten. Er hat
keinen Netzwerkpfad, schreibt keine Profile und löscht keine Anhänge.

## Installation und tatsächlicher Testweg

Python ab 3.11; geprüft in der eigenen Python-3.14.7-Umgebung. Abhängigkeiten
sind Prüfwerkzeuge, nicht Bestandteil der Swift-App. `requirements.txt` pinnt
auch die RFC-3339-Prüfung: Ein `FormatChecker` ohne dieses Zusatzpaket würde
`date-time` sonst stillschweigend ungeprüft lassen. Fehlende UUID-/Zeitprüfung
führt deshalb zu `format_dependency_missing` statt zu einem positiven Bericht.

Vom Repository-Root, mit eigener Umgebung und Cache ausserhalb des Repositories:

```sh
uv venv --python python --cache-dir F:/ChnobelRuntime/referenz/uv-cache F:/ChnobelRuntime/referenz/venv
uv pip install --python F:/ChnobelRuntime/referenz/venv/Scripts/python.exe --cache-dir F:/ChnobelRuntime/referenz/uv-cache -r produkt/werkzeuge/referenz/requirements.txt
```

In Git Bash unter Windows (ein `F:`-Pfad darf nicht als PATH-Element verwendet
werden: der Doppelpunkt trennt dort Pfade):

```sh
export PATH='/f/ChnobelRuntime/referenz/venv/Scripts':"$PATH"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX=F:/ChnobelRuntime/referenz/pycache
export TMPDIR=F:/ChnobelRuntime/referenz/tmp
export TMP="$TMPDIR" TEMP="$TMPDIR"
python -m unittest discover -s produkt/werkzeuge/referenz/tests -v
python -m produkt.werkzeuge.referenz --check-open-corpus
python -m produkt.werkzeuge.referenz --trace produkt/vertraege/v1/spuren/korrigierte-fehllesung.json
```

Das `tmp`-Verzeichnis vorab anlegen. Auf anderen Plattformen dieselben Befehle
in einer eigenen venv mit dort gültigem externem Runtime-Pfad ausführen; der
Python-Code enthält keine Laufwerkspfade und verwendet keine Betriebssystem-API.
Die CLI schreibt nur nach stdout/stderr. Exit 0 bedeutet erfolgreich ausgewertet,
**nicht**, dass jede fachliche Aussage zulässig war. Exit 2 bedeutet ungültige
Eingabe oder eine gescheiterte offene Regression; dann gibt es keinen Teilbericht
mit positiven Aussagen auf stdout.

Der Export der eigenen offenen Spuren ist bewusst getrennt vom Prüfer:

```sh
python -m produkt.werkzeuge.referenz.offene_spuren --write
```

Er schreibt ausschliesslich `produkt/vertraege/v1/spuren/` und `ungueltig/`.
Die Sollentscheidungen stehen explizit im Exportprogramm und in den JSON-Dateien;
sie werden **nicht** aus der Referenzauswertung erzeugt. Das macht sie lesbar und
reproduzierbar, aber nicht unabhängig. Die ausgegebenen Katalogzählungen sind
Entwicklungskennzahlen, keine statistische Fehlerrate und keine Abdeckung realer Kinder.

## Python-API

```python
from produkt.werkzeuge.referenz import (
    ContractError, evaluate_trace, load_json, load_rules,
    validate_schema, validate_rules, validate_evidence,
)

fixture = load_json("produkt/vertraege/v1/spuren/korrigierte-fehllesung.json")
report = evaluate_trace(fixture["events"])
assert report["decisions"]["attempt.result.correct"] == "must_claim"
assert report["facts"]["answer.deviation"] == "falsch"
```

- `load_json(path)`: UTF-8; doppelte JSON-Schlüssel und nichtendliche Zahlen
  werden abgewiesen. Keine stillschweigende Normalisierung von Identitäten.
- `validate_schema(name, value)`: Draft 2020-12 plus aktivierte Formate;
  `name` ist `ereignis`, `beweisregel` oder `belegstatus`. Lokale Schemas,
  kein Remote-Resolver. Ein Schemaerfolg allein ist kein fachlicher Nachweis.
- `validate_rules(rules)`: Schemas, bekannte Fakten, disjunkte `all`/`none`,
  Gültigkeits-/Abgabewächter, eindeutige IDs und Claims, verschiedene Pflichtspuren,
  vollständige und azyklische Fallback-Verweise. Die offene Katalogprüfung löst
  zusätzlich die Spurenpfade auf und prüft deren tatsächliche Sollentscheidungen.
- `evaluate_trace(events, rules=None) -> dict`: reine Funktion; v1-Ereignisliste
  eines Streams oder ein gültiges Zwischenpräfix. Standardregeln aus `v1/regeln/`.
  Verändert Eingaben nicht. Ohne Zustand ausserhalb der Spur wiederherstellbar.
- `validate_evidence(evidence, expected_candidate=None, expected_digests=None,
  expected_count=None)`: Struktur, Zählerinvarianten und optional vom Aufrufer
  vorgegebene Bindungen. Keine Rückgabe bedeutet nur strukturell gültig.
  **Kein Authentisierungs-, ACL-, Signatur- oder Releaseverfahren.** Externe
  Erwartungswerte dürfen nicht aus demselben zu prüfenden Bericht kopiert werden.
- `ContractError.code`: stabile Fehlerkategorie (`schema`, `event_id_conflict`,
  `sequence_conflict`, `foreign_stream`, `dangling_reference`, `wrong_source`,
  `candidate_binding`, `digest_binding`, `count_mismatch` usw.). Ein Integritätsfehler
  unterbindet die gesamte fachliche Auswertung; er ist kein Fehler des Kindes.

Berichtsform (`schemaVersion: 1.0.0`):

| Feld | Bedeutung |
|---|---|
| `streamId`, `candidate` | unveränderte Bindung der Eingabespur |
| `facts` | alle Fakten aus dem Katalog mit `wahr`, `falsch`, `unbekannt` |
| `decisions` | für jede Regel `must_claim`, `must_not_claim` oder `undecidable` |
| `claims` | ausschliesslich zulässige Aussagen mit Claim-ID, Regel-ID/-Revision und Wortlaut |
| `integrity.uniqueEvents` | Anzahl eindeutiger Ereignisse |
| `integrity.deduplicated` | Anzahl ignorierter identischer Zustellungen |
| `integrity.gapStarts` | sortierte Startsequenzen bekannter Lücken/Unterbrechungen |
| `curriculumSourceStatus` | hier immer `offen` |

`decide`, `conjunction` und `negate` sind niederstufige Logikbausteine für bereits
validierte Regeln/Fakten, kein Ersatz für `evaluate_trace`.

## Faktenkatalog 1.0.0

Alle Aussagen verlangen `observation.valid` und `attempt.submitted` als wahr.
Es gilt die starke dreiwertige Konjunktion: ein belegtes Veto macht die Regel
falsch; sonst macht ein unbekanntes benötigtes Faktum sie unbekannt. `none`
verlangt ausdrücklich `falsch`, niemals bloss das Fehlen eines positiven Werts.

| Fakt | Wahr | Falsch / unbekannt |
|---|---|---|
| `attempt.submitted` | Abschlussgrund `submitted` | `aborted`/`interrupted`: falsch; kein Abschluss: unbekannt |
| `observation.valid` | kein Rückzug, keine Invalidierung oder Profillöschabsicht | bei einem dieser Vorgänge falsch; kein Beleg physischer Löschung |
| `observation.complete` | abgeschlossene lückenlose Spur | offene Spur oder bekannte Lücke: unbekannt |
| `answer.value.15` | aktuelle direkte, bestätigte oder korrigierte Antwort 15 | anderer expliziter Wert: falsch; keine aktuelle Antwort, nur Lesart oder automatische Übernahme: unbekannt |
| `answer.deviation` | aktueller expliziter Wert ungleich 15 | explizite 15: falsch; Lesart/automatische Übernahme/fehlende Antwort: unbekannt. Keine Diagnose einer Fehlvorstellung |
| `board.ten.child` | wirksam 10 links, 5 rechts, keine Reserve; alle vom Anfang abweichenden Plättchen zuletzt vom Kind bewegt | anderer bekannter Zustand/übernommene App-Provenienz: falsch; Materiallücke: unbekannt |
| `board.ten.app` | wirksam 10/5 mit mindestens einem von der App verschobenen Plättchen | keine solche App-Provenienz: falsch; Materiallücke: unbekannt |
| `board.doubles.child` | wirksam 7 links, 7 rechts, 1 Reserve; Verschiebungen vom Kind | andere bekannte Lage: falsch; Materiallücke: unbekannt |
| `board.path.child` | Zehner- oder 7+7+1-Weg durch obige Regeln belegt | beide falsch: falsch; sonst unbekannt |
| `history.ten.child` | Kind hat im beobachteten Verlauf einmal wirksam 10/5 gelegt | Undo entfernt diesen historischen Fakt nicht; keine solche Handlung und lückenlos: falsch; sonst unbekannt |
| `support.ten.before` | wirksame Zehnerhandlung hat vorher einen zielbezogenen Hinweis/eine Demo | nur bei lückenlos beobachtetem Präfix ohne solche Hilfe falsch; ohne wirksame Zielhandlung unbekannt |
| `support.doubles.before` | entsprechend für die wirksame 7+7+1-Handlung | gleiche Grenze; derzeit keine Freiheitsbehauptung für diesen Weg |

Der Aktionsanker ist die Sequenz, an der die aktuelle Darstellung erstmals
vollständig erreicht wurde. Ein späterer Hinweis verändert diesen Anker nicht.
Verlässt ein Zug/Undo die Darstellung, wird er entfernt; erneutes Erreichen wird
neu verankert. Historische Handlung und aktuell wirksame Darstellung sind getrennt.
Ein Hinweis zwischen zwei Einzelzügen liegt vor dem vollendeten Zehnerschritt.

Bei einer Lücke kann eine nicht beobachtete Rücknahme oder Bewegung nicht
verneint werden: der Materialzustand bleibt konservativ unbekannt, ebenso die
bis dahin aktive Antwort. Eine **danach explizit abgegebene 15** kann trotzdem
anerkannt werden. Eine Lücke nach dieser Antwort macht deren Aktualität erneut
unbekannt. Ein vollständiger Neuaufbau des Materials nach Lücke ist in v1 noch
kein implementierter Nachweisweg; dafür wäre ein eigener Snapshot-Vertrag nötig.

## Ereignisvertrag für den Swift-Abgleich

Kanonisch: [`../../vertraege/v1/ereignis.schema.json`](../../vertraege/v1/ereignis.schema.json).
Alle Hüllen und Payloads sind geschlossen (`additionalProperties: false`).

### Hülle

- `schemaVersion` exakt `1.0.0`.
- `eventId`, `streamId` und alle fachlichen IDs: kanonische kleine UUIDs mit
  RFC-Variante und Version 1–8; keine Nil-UUID und keine fremden Zeichenfolgen.
- `seq`: nichtnegative ganze Zahl, erste Sequenz 0. Zustellungen werden nach
  `seq` sortiert. Gleiche `eventId` und identischer JSON-Inhalt werden einmal
  verarbeitet. Anderer Inhalt unter derselben ID, zwei IDs an derselben Sequenz,
  fremder Stream oder Kandidatenwechsel sind Integritätsfehler.
- `occurredAt`: RFC-3339 mit Zeitzone, kein Beweis für verlässlichen Zeitabstand.
  Optional `monotonic: {bootId, ns}`: innerhalb derselben Boot-ID nicht rückläufig.
  Die fachliche Ordnung stammt ausschliesslich aus `seq`.
- `actor`: `child`, `app` oder `system`, abhängig vom Ereignistyp.
- `candidate`: nichtleere `build`, `content`, `rules`; in einem Stream unverändert.
  Dieser Prüfer unterstützt ausschliesslich Regelpaket `rules: "1.0.0"`.

### Payload und Akteur

| Typ | Akteur | Pflichtinhalt / zusätzliche Semantik |
|---|---|---|
| `attempt.opened` | system | `taskContract`, `taskVersion`, `family`, `representation`, `target`, `startingState`, `profileId`, `initialMaterial` |
| `attempt.closed` | system | `reason`: submitted/aborted/interrupted. Kein impliziter Erfolg |
| `input.captured` | child | neue `inputId`, `mode`: handschrift_finger/handschrift_stift/ziffernblock/tastatur/auswahl |
| `recognition.proposed` | app | neue `recognitionId`, frühere `inputId`, numerische `reading` als Zeichenfolge, confidence, alternatives; nur Handschrifteingaben |
| `answer.committed` | child, automatisch app | neue `answerId`, `inputId`, ganzzahliger value, origin; nicht-direkt zusätzlich `fromRecognitionId` |
| `response.retracted` | child | aktuell aktive `answerId`; keine unbekannte oder bereits zurückgenommene Antwort |
| `material.moved` | child oder app | neue `moveId`, eindeutige `items`, fromZone, toZone, via; Zone muss stimmen, Bewegung muss wirksam sein |
| `action.undone` | ursprünglicher Akteur | frühere aktive `moveId`; keine spätere Bewegung derselben Plättchen darf davon abhängen |
| `support.presented` | app | neue supportId, kind, target, effect, channel; Demo, Teilschritt und Lösungsweg können nicht neutral sein |
| `mode.changed` | child | from/to; tatsächlicher aktueller Ausgangsmodus und anderer Zielmodus |
| `artifact.saved` | child | neue artifactId, origin selbst_erstellt/importiert, digest, mediaType; keine implizite Leistungsbewertung |
| `self_report.recorded` | child | neue reportId, target, boolescher value; keine Beobachtung der Ausführung |
| `condition.observed` | system | kind und detail; gap zusätzlich sinceSeq > 0 und nicht in der Zukunft |
| `content.withdrawn` | system | content der Kandidatenfassung, reason |
| `observation.invalidated` | system | frühere eventIds desselben Streams, reason |
| `artifact.deleted` | system | bekannte artifactId; kein Effekt auf unabhängig erhaltene direkte Zahlenantwort |
| `profile.erasure_requested` | system | profileId muss dem Anfang entsprechen; blockiert Aussagen, ersetzt keine echte Löschroutine |

Nach Abschluss sind nur die vier Lifecycle-Ereignisse in den letzten vier Zeilen
zulässig. Das bedeutet **nicht**, dass Anhänge oder Profile physisch gelöscht
wurden. Der Swift-Adapter muss die tatsächliche Löschwirkung separat nachweisen.

### Leitfall und Provenienz

Die unterstützte Aufgabenfassung ist explizit:

```json
{
  "taskContract": "sum-8-7",
  "taskVersion": "1.0.0",
  "family": "addition-20",
  "representation": "counters",
  "target": "sum-8-7",
  "startingState": "board-8-7-v1"
}
```

`initialMaterial` enthält genau 15 unterschiedliche Einträge
`{itemId: UUID, zone: "left" | "right", origin: "task"}`: acht links, sieben
rechts, keine Reserve. IDs können vom Adapter vergeben werden; der Prüfer kennt
keine speziellen ID-Werte. Zonen für Bewegungen sind `left`, `right`, `spare`.
Die Herkunft aus dem Aufgabenmaterial und die letzte wirksame Bewegung werden
für jedes Plättchen getrennt ausgewertet. Ein unbekanntes/neues Plättchen darf
nicht in den Versuch eingeschmuggelt werden.

`via: app_demo` ist ausschliesslich für `actor: app` zulässig; App-Bewegungen
müssen diesen Bedienweg verwenden. Jede App-Bewegung zählt selbst als vorherige
Hilfe für nachfolgende Materialwege, auch wenn kein separates `support.presented`
vorliegt. Undo setzt Material zurück, **nicht** die erhaltene Hilfe.

Bei `support.presented` sind die Ziele `ten.step`, `doubles.step`, `result`,
`navigation`; Effekte `neutral`, `hinweis`, `vorgabe`. Nur die eng betroffene
Hilfefreiheit wird bewertet. «Ohne vorherigen Hinweis auf den Zehnerschritt» ist
keine Behauptung völliger Selbstständigkeit. Eine neutrale Kennzeichnung ist
Eingabe des Protokolls, kein unabhängiger Beleg des Bildschirminhalts.

### Lesarten und Antworten

- `direkt`: Kind, ohne `fromRecognitionId`, Eingabe per Ziffernblock/Tastatur/Auswahl.
- `bestaetigt`: Kind, frühere Lesart derselben Eingabe, gleicher Zahlenwert.
- `korrigiert`: Kind, frühere Lesart derselben Eingabe, anderer Zahlenwert.
- `automatisch_uebernommen`: App, gleicher Wert wie die frühere Lesart; bleibt
  fachlich unbekannt, bis eine neue explizite Antwort vorliegt.
- Vor einer neuen Antwort muss die aktive zurückgenommen werden. Eine reine
  `recognition.proposed` ist niemals eine aktive fachliche Antwort.

Damit erzeugt die Folge Lesart 16 → Korrektur 15 auch in **jedem Zwischenpräfix**
keinen fachlichen Fehler. Die bestätigte 15 wird unabhängig von einem fehlenden,
angeleiteten oder unbekannten Materialweg anerkannt. Ein Materialweg allein
behauptet keine richtige Ergebniseingabe. Fallback-IDs werden nie direkt als
Claims ausgegeben: jede engere Aussage muss ihre eigene Regel bestehen.

## Regel- und Beleggrenzen

Fünf zentrale Aussagen: richtiges Ergebnis, freier Zehnerschritt, angeleiteter
Zehnerschritt, anderer gültiger 7+7+1-Weg, passend dargestellter Materialweg.
Jede hat explizite `must_claim`-, `must_not_claim`- und `undecidable`-Spuren.
Offene Spuren dürfen Teilwege und falsche Eingaben enthalten; sie sind nicht
mit absichtlich vertragswidrigen Spuren unter `ungueltig/` zu verwechseln.

Belegstatus v1 verbietet `passed` mit `none`, leeren Kandidaten, fehlendem Lauf,
fehlenden Digests, null Fällen, übersprungenen oder gescheiterten Fällen.
Nichtoffene Ergebnisse brauchen beide Achsen vollständig und SHA-256-Bindungen
für Artefakt, Prüfsatz, Regeln und Bericht. Die Referenz prüft Summen sowie
optionale fremd vorgegebene Kandidaten-/Digest-/Nennerbindungen. Sie überprüft
weder den wirklichen Inhalt eines Artefakts noch die Berechtigung des Ausstellers.
Die im Unit-Test konstruierte positive Struktur ist **kein ausgestellter Beleg**.

Alle LU-/BE-Kompetenzzuordnungen sind ausdrücklich **offene Vorschläge** aus dem
Projektauftrag, keine geprüften kantonalen LP-Referenzen. Es gibt keine
«Fassung zu bestimmen» mit Prüfetikett. v1 akzeptiert hier ausschliesslich
`quellenstatus: offen` und `bezug: teil`. Eine echte Quellenprüfung ist ein
weiterer, getrennt zu belegender Arbeitsschritt.

## Noch nicht belegt / bewusst ausserhalb des Werkzeugs

- Übereinstimmung von Swift-Implementierung, UI, Audio, Einrasten und Protokoll.
  Ein absichtlich verschwiegener, spurlos neu nummerierter Bildschirmhinweis
  ist ohne unabhängigen Bildschirmabgleich nicht aus JSON erkennbar.
- Authentisierte technische Rollen, verdeckte Prüfung, Releasefreigabe,
  Kandidatenarchiv, Signing oder Apple-Status. RT-01/02 bleiben dadurch offen.
- Echte Handschrifterkennung, Geräteverhalten, reale Kinder, Lernwirkung,
  Motivation, Fairness oder langfristiger Transfer.
- Physische Datenspeicherung/-löschung und fachliche Aussagen über weitere
  Aufgaben, Fächer oder allgemeine Kompetenzbeherrschung.

Der offene Katalog und die Negativtests konkretisieren RT-03 sowie die fachlichen
Zusatzbefunde. Historische Befunde werden damit nicht rückwirkend geschlossen.
Der spätere Swift-Abgleich soll dieselben JSON-Spuren konsumieren und `facts`,
`decisions`, Claim-IDs, Dedupe-Zähler sowie Fehlerkategorien vergleichen; ein
reiner Vergleich nur positiver Ergebniszahlen reicht nicht.
