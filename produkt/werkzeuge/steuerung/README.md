# Lokaler Phase-0-Steuerungskern

Deterministische Python-/SQLite-Bibliothek fuer Betriebsproben. Keine Netzwerk-
oder Dienstprozesse, kein Git-Aufruf, kein Apple-Adapter, keine Secrets. Eine
lokale erfolgreiche Regression ist **weder eine Freigabe noch der Abschluss
von P0-02, P0-10 oder Phase 0**. Fremdes Review und die originalen Gates bleiben
notwendig. STATUS und die originale Auftragsliste werden nicht geschrieben.

## Voraussetzungen und lokale Tests

Python ab 3.11, SQLite ab 3.37 (STRICT-Tabellen), nur Standardbibliothek. Die
Speichergrenze dieser Installation ist Windows mit Laufwerk F:. Datenbanken,
Sicherungen und Testdateien liegen ausschliesslich unter
`F:/ChnobelRuntime/steuerung`; Bytecode liegt unter `F:/ChnobelRuntime/cache`.
Auf andere Volumes aufloesende Pfade werden abgelehnt. Die Verzeichnisse muessen
vom Betrieb angelegt/freigegeben sein; Tests erstellen isolierte Unterordner.

Aus dem Repository, unter Git Bash:

```bash
export TEMP='F:/ChnobelRuntime/steuerung'
export TMP="$TEMP"
export TMPDIR="$TEMP"
export PYTHONPYCACHEPREFIX='F:/ChnobelRuntime/cache'
python -m unittest discover -s produkt/werkzeuge/steuerung/tests -v
```

Alle Fixtures sind oeffentlich und synthetisch. Die Tests benutzen echte
SQLite-Dateien, mehrere Verbindungen, acht gleichzeitige Threads, vier
konkurrierende `spawn`-Prozesse fuer Auftragsclaims sowie zwei Prozesse fuer
eine lokale Wirkung. Subprozesse beenden sich mit `os._exit` vor/nach
Wirkungsabsicht, nach lokaler Wirkung und nach Bestaetigung. Ein weiterer
Prozess wird mitten in einer offenen Transaktion terminiert. SQLite-Rollback,
Auditspur, stale Worker, Wiederanlauf, parallele Sicherung und Restore werden
anschliessend ueber neue Instanzen gelesen und geprueft. Es gibt keine
sleep-basierte Erfolgserwartung; Barrieren/Ereignisse koordinieren die Proben.

## Dateien

- `contracts.py`: strikte JSON-, Digest-, ID-, Zeit- und Startgraphpruefung.
- `schema.py`, `core.py`: transaktionale Auftragsdaten, Leases, CAS, Audit.
- `journal.py`: vorab gespeicherte, exklusiv beanspruchte Wirkungsabsichten.
- `recovery.py`: SQLite-Onlinebackup, Inhaltspruefung, gesperrter Restore.
- `gates.py`: fail-closed Strukturpruefung eines vollstaendigen Schlussnachweises.
- `cli.py`, `__main__.py`: passive Uebernahme, Anzeige, Sicherung, Diagnose.
- `tests/`: synthetischer lokaler Wirkungsdienst und Regressionen.

## Zustands- und Schreibvertrag

Normalweg: `planned -> ready -> leased -> running -> verifying -> done`.
Zusaetzlich: `retry_wait`, `reconciling`, `blocked`, `superseded`.

| Ausgang | Zulaessige Folge / Bedingung |
|---|---|
| `planned` | `ready`, `blocked`, `superseded` |
| `ready` | `leased` nur ueber `claim`; sonst `blocked`, `superseded` |
| `leased` | `running`, `retry_wait`, `blocked` |
| `running` | `verifying`, `retry_wait`, `reconciling`, `blocked` |
| `verifying` | `done`, `retry_wait`, `blocked` |
| `retry_wait` | nach Frist `ready` oder `claim`; sonst `blocked`, `superseded` |
| `reconciling` | Lease ueber `claim`; nach Abgleich `running`/`verifying`; `blocked` |
| `blocked` | explizit `planned`, bei offener Wirkung `reconciling`, oder `superseded` |
| `done`, `superseded` | terminal; kein Rueckschreiben oder nachtraegliches Gruenfaerben |

Jeder Auftrag speichert ID, Revision, Phase, Titel, originale Abhaengigkeiten,
SHA-256 der Startlistenbytes und der Auftragsdefinition, Lease-Inhaber/-Ablauf,
Fencing-Token, Versuchszahl, naechste Pruefzeit, Ergebnisdigests und blocked-Grund.
Abhaengigkeiten gelten nur mit `done` als erfuellt, nicht mit `blocked` oder
`superseded`. Die originalen P0-Abhaengigkeiten werden exakt uebernommen.
Unabhaengige Entwicklung setzt deren Zustaende nicht kuenstlich auf `done`.

- Pro Mutation: eigene Verbindung, `BEGIN IMMEDIATE`, erwartete Revision,
  Zustands-/Abhaengigkeitspruefung, Daten und Audit in derselben Transaktion.
  Neue Datenbanken verwenden WAL, alle Schreibverbindungen `synchronous=FULL`,
  Fremdschluessel und Speichertemporaerdateien. Kein gemeinsam benutzter
  Python-Verbindungszustand zwischen Threads.
- Leases enthalten Store-Epoche, Inhaber und Fencing-Token. Wirkungsleases
  binden zusaetzlich den Auftrags-Token. Bei **jeder** Neuvergabe steigt ein
  datenbankweiter Integer-High-Water-Mark. Die Epoche verhindert Token-ABA
  zwischen alter Instanz und Restore. Revisionen sind keine Berechtigungen.
- Alle Zeiten sind explizite nichtnegative UTC-Sekunden als Integer, keine
  Booleans/Floats. Identische Eingaben/Uhrzeiten fuehren zu identischen
  fachlichen Entscheidungen. Nur die Instanzepoche ist zufaellig. Die Uhr
  darf gegenueber der zuletzt bestaetigten Transaktion nicht zuruecklaufen.
  Der spaetere vertrauenswuerdige Steuerungsdienst muss die Uhr liefern.
- Eine Lease ist bei `now == lease_expires` bereits ungueltig. `renew` braucht
  die aktuelle Revision und eine noch gueltige Lease. Abgelaufene Leases
  werden zuerst mit `recover_expired` in `retry_wait` oder bei unsicherer
  Wirkung in `reconciling` ueberfuehrt. Eine positive Wiederanlaufpause bleibt
  ueber Neustarts gespeichert. Wiederholte Abgleiche haben begrenztes,
  exponentielles Backoff; es gibt keinen blinden Wiederholungsupload.
- `blocked` verlangt einen nichtleeren Grund, z.B. `extern blockiert`.
  Unblock/Abloesung sind explizit und auditiert. Offene Wirkungen sperren
  Verifikation/Abschluss/Abloesung; unsichere Wirkungen auch normales Retry.
- `done` verlangt eigene gespeicherte Ergebnisartefakte. Ein Ergebnisverweis
  allein ist keine fachliche oder unabhaengige Freigabe. Die Bibliothek ist
  nur fuer einen vertrauenswuerdigen Steuerungsdienst bestimmt; die CLI bietet
  bewusst keinen Abschluss- oder beliebigen Statusbefehl.
- Artefakte sind SHA-256-adressierte unveraenderliche Bytes in SQLite mit
  Auftragszuordnung und Rolle. Grenze: 16 MiB pro Artefakt. Diese lokale
  Betriebsprobe ist kein Speicher fuer grosse native Releasearchive.

Die Bibliotheks-API liefert JSON-faehige Snapshots. `Lease.from_record(snapshot)`
uebernimmt die Lease, waehrend jede nachfolgende Mutation die zuletzt
zurueckgelieferte Revision verwenden muss. Es gibt keinen generischen
SQL-/Patch-Endpunkt fuer Produktionszustand.

## Merge-/Upload-Wirkungsjournal

`prepare_effect` speichert die Operations-ID und einen unveraenderlichen
Request **vor** einer moeglichen Wirkung. Pflichtbindungen: Auftrag, Art,
Kandidatendigest, gespeichertes Archiv und exaktes Ziel. Uploadziel:
`app_id`, `version`, `build_number`. Mergeziel: `repository`, `branch`, `commit`.
SHA-256-Digests sind exakt 64 kleine Hexzeichen; Commitdigests 40 oder 64.
Es findet keine stillschweigende Normalisierung statt.

Dieselbe Operations-ID mit gleichem Request ist idempotent; mit anderem
Inhalt ein Konflikt. Ein zweiter Vorgang fuer dasselbe Ziel/dieselbe Buildnummer
wird auch bei neuer Operations-ID abgelehnt.

1. `prepared`: Absicht samt Archivbytes ist dauerhaft vorhanden.
2. `claim_effect`: exklusiver Claim mit eigener Revision, steigender Nummer,
   begrenzter Lease und Bindung an die noch gueltige Auftragslease; `checking`.
3. `observe_effect`: zuerst nach genau diesem Ziel suchen. `found` bestaetigt
   nur bei exakter Operations-, Request-, Kandidaten-, Archiv- und Zielbindung
   mit externer Vorgangs-ID. `unknown` bleibt mit Grund und Prueffrist ausstehend.
4. Nur ein eindeutiges `absent` **vor dem allerersten Versuch** erlaubt `armed`.
5. `begin_dispatch` speichert atomar `unknown`, `dispatch_count=1` und
   `uncertain=1`. Erst danach duerfte ein autorisierter Dienst die Wirkung
   ausloesen. Diese Methode selbst sendet nichts.
6. Ein Prozessabbruch laesst die Absicht stehen. Der Nachfolger darf nur
   abgleichen. Selbst `absent` nach begonnener Wirkung erlaubt **keine** zweite
   Ausfuehrung: externe Sichtbarkeit kann verzoegert sein. Ein Fund kann
   bestaetigt werden, sonst bleibt die Wirkung begruendet ausstehend.

Der lokale Testdienst schreibt tatsaechlich in eine zweite SQLite-Datenbank
und prueft Idempotenz/Fencing. Er ist ausschliesslich Testcode. Die Bibliothek
kann eine bereits an einen fremden Dienst gesendete Anfrage nicht zurueckrufen.
Ein echter Dienst muss Fencing, technische Rechte und Idempotenz am
Wirkungspunkt durchsetzen und Lesebeobachtungen authentisieren. Ein Datenbank-
Token oder ein beliebiger JSON-Bericht beweist diese externe Grenze nicht.
Es gibt absichtlich keinen Reset von `dispatch_count`, keinen Force-Upload
und keinen Weg, einen unsicheren Vorgang unter neuer ID heimlich zu wiederholen.

## Sichere CLI-Uebernahme der Originalauftraege

`preview` liest standardmaessig `steuerung/auftraege/phase-0.json` aus diesem
Worktree. Es schreibt weder SQLite noch die Quelldatei. Die Ausgabe enthaelt
den Digest **der exakten Dateibytes**, alle Originalauftraege und deren Anzahl.

```bash
python -m produkt.werkzeuge.steuerung preview
```

Erst nach Kontrolle dieses Digests erfolgt eine explizite, passive Uebernahme
in einen neuen, vom Betrieb gewaehlten F:-Laufzeitpfad:

```bash
python -m produkt.werkzeuge.steuerung import \
  --database F:/ChnobelRuntime/steuerung/betrieb/auftraege.sqlite \
  --expected-digest '<exakter Digest aus preview>' \
  --now '<verifizierte UTC-Sekunden>'
python -m produkt.werkzeuge.steuerung show \
  --database F:/ChnobelRuntime/steuerung/betrieb/auftraege.sqlite
python -m produkt.werkzeuge.steuerung check \
  --database F:/ChnobelRuntime/steuerung/betrieb/auftraege.sqlite
```

Platzhalter muessen bewusst ersetzt werden. `--source` erlaubt einen
abweichenden, expliziten Startlistenpfad. Akzeptiert werden nur das originale
Startformat `0.1.0` und passive `planned`/`ready`-Auftraege, ohne unbekannte,
zyklische oder doppelte Abhaengigkeiten. Ein geaenderter Graph wird nicht
nachtraeglich eingemischt. Ein identischer Wiederholungsimport laesst Revision,
Lease und Fortschritt unveraendert. Geaenderte Bytes brauchen einen separaten,
noch nicht implementierten versionierten Migrationsentscheid.

## Sicherung und Wiederherstellung

```bash
python -m produkt.werkzeuge.steuerung backup \
  --database F:/ChnobelRuntime/steuerung/betrieb/auftraege.sqlite \
  --destination F:/ChnobelRuntime/steuerung/sicherung/snapshot.sqlite
python -m produkt.werkzeuge.steuerung restore \
  --source F:/ChnobelRuntime/steuerung/sicherung/snapshot.sqlite \
  --destination F:/ChnobelRuntime/steuerung/wiederhergestellt/auftraege.sqlite \
  --expected-digest '<Sicherungsdigest>' \
  --fencing-floor '<externer aktueller High-Water-Mark>' \
  --now '<verifizierte UTC-Sekunden>'
```

- Onlinebackup ueber die SQLite-Backup-API, keine Kopie einer offenen DB ohne
  WAL. Die abgeschlossene Sicherung ist eine einzelne Datei im DELETE-Modus.
  Jobs, Originalbytes, Abhaengigkeiten, Artefaktbytes, Ergebnisse, offene und
  bestaetigte Wirkungen, High-Water-Mark und Audit sind in derselben Momentaufnahme.
- `integrity_check`, Fremdschluessel, Startgraph, Inhaltsdigests, Ergebnis- und
  Wirkungsbindungen sowie Auditrevisionen werden vor Veroeffentlichung geprueft.
  Ein File-SHA ersetzt diese internen Pruefungen nicht.
- Veroeffentlichung per atomarem Hardlink unter neuem Namen auf demselben
  lokalen Volume; vorhandene Ziele werden nie ersetzt. Fehler beim Hardlink
  bleiben Fehler. Keine Behauptung ueber Netzlaufwerke oder Stromausfalltests.
- Restore prueft den expliziten Dateidigest beim Kopieren, verlangt einen
  Fencing-Untergrenzwert mindestens so hoch wie die Sicherung, wechselt die
  Epoche, entzieht alte Leases und erhoeht Revisionen. **Jede** offene Wirkung
  wird unsicher, selbst wenn sie in der alten Momentaufnahme nur `prepared`
  war: die Quellinstanz koennte sie nach der Sicherung begonnen haben.
- Der Restore bleibt `recovery_locked=1`. Die CLI kann ihn anzeigen/pruefen,
  aber nicht aktivieren. `activate_local_recovery` dient ausschliesslich der
  synthetischen Bibliotheksprobe und beweist keine Rechte oder Quellstilllegung.
- Produktionsaktivierung ist offen: Die alte Quelle muss stillgelegt, der
  aktuelle globale Fencing-Stand unabhaengig beschafft und das externe
  Operationsinventar vollstaendig abgeglichen werden. Ein alter Snapshot kennt
  nachtraeglich neu angelegte Vorgangs-IDs nicht. Der RPO ist der Sicherungszeitpunkt,
  kein Versprechen verlustfreier Wiederaufnahme nach beliebigem Datenverlust.
  Ohne diese externen Nachweise bleibt echte Wirkung gesperrt.

## Fail-closed Nachweispruefung

`Policy` ist ein unveraenderlicher, separat zu vertrauender Regelplan. Er
verlangt Kandidaten-, Archiv- und Regeldigest, den erwarteten Belegaussteller
und **alle acht** Pflichtjobs aus Masterprompt Abschnitt 18 mit jeweils
vorab festgelegter positiver Integer-Fallzahl und erwarteter CI-Identitaet.
Es gibt keine leeren oder abgeschwaechten Standardwerte.

Das Format wird in `gates.py` und den oeffentlichen synthetischen Tests
vollstaendig gezeigt. Ein Bericht verlangt `schema_version=1`,
`kind=ci_attestation`, die exakten Bindungen, `status=passed`, `executed=true`
und genau einmal jeden Pflichtjob. Jeder Job braucht dieselben Digests, seine
erwartete Identitaet, `status=passed`, exakt das Boolean `true` und
`expected_cases = executed_cases = passed_cases = vorgegebene positive Zahl`.
Fehlend, skipped, null, null Faelle, falscher Kandidat, falsches Archiv,
falscher Aussteller, doppelte Jobs, Floats/Booleans als Fallzahlen und
unbekannte Felder scheitern. Lokale Simulationsberichte scheitern ebenfalls.

```bash
python -m produkt.werkzeuge.steuerung validate-report \
  --policy F:/ChnobelRuntime/steuerung/pruefung/regelplan.json \
  --report F:/ChnobelRuntime/steuerung/pruefung/bericht.json
```

`checks_valid=true` bezeichnet nur die Struktur-/Bindungspruefung.
**`release_authorized` bleibt immer `false`; `authentication=not_verified`.**
CLI-Exitcode 2 bedeutet ungueltig/Fehler, 3 bedeutet strukturell passend, aber
unauthentisiert und weiterhin gesperrt. Der Validator gibt nie Exitcode 0 als
Freigabesignal. Der Regelplan muss ausserhalb des Kandidaten vor dem Lauf
festgelegt und gegen Aenderung geschuetzt sein. Texte fuer Aussteller und
Digests sind ohne Signatur-/OIDC-/Artefaktpruefung keine authentisierten Belege.

Dieser Plan beschreibt den **vollstaendigen Schlussnachweis**, einschliesslich
`release-internal` und `reconcile`. Er ist nicht als zirkulaere Vorbedingung
fuer den allerersten Upload zu verwenden. Eine getrennte authentisierte
Vorab-Releaseentscheidung und die Integration in privilegierte Dienste sind
noch nicht implementiert.

## Weiterhin offene Grenzen

- Keine technisch durchgesetzte Rollen-/Credential-Trennung, keine verdeckte
  Abnahme, kein eigener Freigabeaussteller, kein echtes Merge-/Uploadrecht.
- SQLite-Dateirechte sind die Vertrauensgrenze. Ein Prozess mit beliebigem
  Dateischreibrecht kann auch SQL/Trigger austauschen; lokale CAS-Pruefungen
  sind keine Sandbox und Audittrigger keine kryptografische Manipulationssperre.
- Kein nativer Build, keine Signierung und kein Apple-Endzustand getestet.
  Der originale Startgraph und die separat dokumentierten Identitaets-/Gate-
  Blocker werden nicht durch diese Betriebsproben erledigt.
- Kleine lokale Artefakte, keine Verschluesselung, keine automatische
  Sicherungsaufbewahrung, keine Produktionsmigration, kein automatischer
  Recovery-Aktivierungsdienst und keine externe Exactly-once-Garantie.
- Ein Zeitgeber muss vertrauenswuerdig sein. Ruecklauf sperrt; ein beliebig
  vorwaerts springender untrusted Zeitwert ist keine sichere Lease-Uhr.
