# Chnobel: Wiederaufnahme und gesicherter Pausenstand

Stand: 2026-11-27. Neuer ausdruecklicher Auftrag "Chnobel weiter" nach Limitreset, ab `9b25d39918d870fcfb6acf33bc78ca6a2768e085`. Die fruehere Nutzerpause war bereits am 2026-11-26 aufgehoben worden; deren separater Statuscommit bleibt `d4a66d62c499d6f25c3eb1f8625972976c7c4fd2`.

## 1. Zuerst beachten

**Interaktive Fortsetzung erlaubt; Cron bleibt aus.** ZUSTAND und BETRIEB stehen auf IN_ARBEIT. Der Nutzerauftrag vom 2026-11-26 erlaubt die Fortsetzung ab `4e31d37c911a45a519ae728adebfbd45b328983c` und verlangt unveraenderte Gates sowie die Reihenfolge in Abschnitt 7. Die erste Live-Pruefung bestaetigte alle fuenf sauberen Worktrees und die erwarteten lokalen/Remote-SHAs. Keine lebenden Subagenten beim Start. Cron `26647d618052`: enabled false, state paused, next_run_at null. Bei erneuter Nutzerpause keine automatische Fortsetzung durch Sitzung, Limitreset, Cron oder Ruecklauf. Geschuetzte Instruktionsdateien ohne ausdrueckliche Dialogzustimmung nicht aendern; die frueher abgewiesene AGENTS.md-Aenderung ist nicht gelandet.

### Historischer erster Nachreview-Abgleich vom 2026-11-26

Beide alten Delegationsmanifeste und die Endmarker aller sechs Transkripte meldeten `interrupted`. Beim ersten Abgleich fehlten alle sechs unter Abschnitt 4 erwarteten Abschlussberichte. Daraus keine vollstaendigen Urteile oder Ratifikation. Die alten Teilbelege bleiben unveraendert und dienten nur als Ausgangsmaterial fuer frische fremde Kontexte. Maschinenlesbarer Abgleich: `F:/ChnobelRuntime/reviews/wiederaufnahme-20261126/abgleich.json`, SHA-256 `dcb023d365e998fbb78bbb10e2a22b5461a9b41eab0ff340db0e9df7efd9d131`. Reihenfolge: zuerst drei gezielte Nachreviews gegen die unten genannten exakten Reparatur-SHAs, danach die drei Ratifikationsvoten. Kein Neustart von `deleg_c8c713b8`, keine v2-Implementierung, kein CI-Neustart oder zweiter PR.

### Neuester Stand: Nachreviews und Ratifikation abgeschlossen

`deleg_5f23880a` ist abgeschlossen. Alle drei Berichte und die angegebenen Kandidaten-/Evidenzbindungen sind vom Elternkontext geprueft. Archive: `steuerung/gedaechtnis/pruefergebnisse/2026-11-26-nachreviews/`. Rohbelege: `F:/ChnobelRuntime/reviews/fortsetzung-20261126/{steuerung,referenz,ipad}/`. Steuerung PASS nur im lokalen Entwicklungsumfang. Referenz FAIL mit neuem hohen RT-16/NR-F01-01 (logisch unmoegliche Undofolge nach zwei Luecken); iPad statisch FAIL mit hohem RT-17/R1-IPAD-01-A (inverse neue App-Bewegung statt Undo belebt alten freien Kindanker). Native Ausfuehrung NOT RUN. Elternlauf: `F:/ChnobelRuntime/verification/2026-11-26-review-parent/evidence/verification.json`, SHA-256 `e557c2af8597cc5f4a09580d6d1fa605f37886e72df71f5e42f9612dbbc2f2f4`; 42 Steuerungsgegenproben bestanden, vier N20-Varianten gegen beide Python-Kandidaten reproduziert, elf iPad-Quellpruefungen mit einem FAIL. Nicht zu einer Gesamtsumme addieren.

Ratifikation `deleg_b54b26ad` ist abgeschlossen: Architekt `sa-0-a0489192`, Didaktik `sa-1-6119ebf7`, Red-Team `sa-2-6572b58d` jeweils COMPLETE/JA zum gesamten eingefrorenen ADR-Hash aus Abschnitt 4. Drei unterschiedliche Rollen, unbedingte Stimmen, Bericht-/Stimm-/Fassungsdigests und Mehrheit vom Elternkontext am 2026-11-26 geprueft. Archiv `steuerung/gedaechtnis/entscheide/2026-11-26-adr0003-ratifikation/` enthaelt die urspruenglichen Rohbytes verlustfrei und einen Hashindex. ADR 0003 ist fuer prospektive Produktentscheidungen verbindlich; nur Status/Entscheidungsvermerk wurden aktualisiert, D1-D6 nicht geaendert. Befunde, Tests und Rechte sind nicht abstimmbar; RT-16/17 bleiben offen.

Das v2-Revisions-/Fallmanifest ist jetzt als unvollstaendiger Entwurf vorhanden: ganze Feldliste, ereignisadressierte Sollbelege und drei konkrete Fragen sind noch nicht abgeschlossen. Vor Freeze zuerst diese Sperren klaeren und eine vollstaendige neue Fassung erstellen, dann einfrieren/haschen und fremd pruefen. Vor dessen Freigabe weiterhin keine Implementierung/native Folgearbeiten/Integration. Die ADR-Ratifikation ersetzt diese Freigabe nicht.

Ratifikationscheckpoint `d84c597a68863929034cff50089e098120c7cb39` und anschliessender Auftragscheckpoint `91cb0c49da3f29c23c4322e51f0256a0c6dc5676` wurden gepusht und zurueckgelesen. `deleg_6bcb2994` / `sa-0-416e4182` ist nun beendet: **INCOMPLETE**, kein Freeze/keine eigene Freigabe. Unveraenderte Rohdaten nur `F:/ChnobelRuntime/specification/v2-manifest-draft-01/`. `manifest.json` SHA-256 `1516d127a688cea5e5a707fbc562e0e70cd43fcd583752be25b1cc3871d95502`; `handoff.json` SHA-256 `970299f1be40510c16eb2c707be39a947023e0eaf80f87f924ea057ea79324df`. Read-only Elternkontrolle vor den neuen Dokumentationswrites: 4'944 Dateihashes, 1'767 Fall-IDs, 3'534 Fallverweise bestaetigt, nicht fachlich ausgefuehrt. Beleg `F:/ChnobelRuntime/verification/v2-manifest-draft-01-parent/mechanical-readback.json`, SHA-256 `056cb24d4b956b4898c9c71d1c9b9f96d2d5c9073ba3c3b0a893709d69bc505a`. Historischer Pruefer bindet den damaligen sauberen Hauptbranch; sein enges Parent-Pfad-Allowlisting nicht zur scheinbaren Anpassung spaeterer Belege veraendern. Status-/Manifest-/Blocker-/Mengen-/Elternabgleich-/Beratungstexte sind verlustfrei unter `steuerung/gedaechtnis/pruefergebnisse/2026-11-26-manifest-entwurf01/` gesichert; die 4'946 gesamten Runtime-Dateien sind nicht vollstaendig in Git gesichert.

Offene Punkte exakt aus `open-issues.json`: Q-ANCHOR-INTERVENTION (Kindanker waehrend noch wirksamem App-Detour), Q-U07 (alte INCONCLUSIVE-Qualifikation ohne Ein-Slot-Annahme), Q-GUARD-TOTALISATION sowie M-REPORT-ORACLES, M-HELP-TEXT-BINDING, M-FIELD-NORMALFORM, M-SEMANTIC-CASE-CHECK. 20 explizit SPECIFICATION_PENDING markierte IDs sind keine fachlichen unbekannt-Faelle; globale Luecken betreffen mehr Faelle. Generische Profile haben noch keine vollstaendige Ereignisherleitung. Insbesondere ist beim U07-Appfall das unbekannt-Profil gegen belegte App-Demo und den support.general-Katalog zu klaeren, kein Produktlauf behauptet.

Historische Nachfolge `deleg_07559a2f`: `sa-0-4c346f07` Architekt, `sa-1-653e4ead` Didaktik, `sa-2-e51db84c` Red-Team, `sa-3-897f522a` Feld-/Hilfetext-Spezifikation. Alle vier am Limit failed/error; gelten als NICHT DURCHGEFUEHRT, keine Teilberichte als Urteile annehmen. Alter Brief `F:/ChnobelRuntime/reviews/v2-manifest-questions-01/brief.md`, SHA-256 `a41b85b4f7b710ddf32e6111d27a4f2fe957c684a50c9ac5485bbe3c1c96ac69`, bleibt unveraendert. Am 2026-11-27 tatsaechlich vorhandene Teilbestaende: Architektur/Red-Team je report.md ohne decision.json; Didaktik ohne diese Dateien; 625 Dateien im technischen Ausschnitt `F:/ChnobelRuntime/specification/v2-field-supplement-01/`, aber keine README.md und kein handoff.json. Keine Vollstaendigkeit aus der Dateimenge ableiten. Inventar und Logdigests unter `F:/ChnobelRuntime/reviews/wiederaufnahme-20261127/abgleich.json`, SHA-256 `a2da62df68a726590c51849b956750611cf7b0b9c5e184cdb62832134984a565`; kompakter Repoabgleich `steuerung/gedaechtnis/pruefergebnisse/2026-11-27-wiederaufnahme/abgleich.json`. Die Altdateien bleiben unveraendert.

### Verbindliche Fortsetzung vom 2026-11-27

- Live-Staende zuerst abgeglichen und dem Nutzer gemeldet: fuenf saubere Worktrees, passende Remote-SHAs, main unveraendert, alle 4'944 Manifest-Handoff-Dateien hashgleich. Cron disabled/paused/next_run_at null, keine lebenden Kinder vor Dispatch. Kein neuer nativer oder fachlicher Test daraus behauptet.
- **Hoechstgrenze zwei gleichzeitige Subagenten.** Jede grosse Gremiumsberatung wird nach Frage zerlegt, die technische Spezifikation nach unabhaengigem Abschnitt. Keine Ueberschreibung alter Teilabgaben und keine Wiederverwendung abgebrochener Kontexte als Schlussurteil.
- Wiederaufnahmecheckpoint `093e86e7471e7c70d3a9676f417f6b46176693c9` gepusht/remote bestaetigt, main unveraendert. Frischer Batch `deleg_6aa0a185` vollstaendig zurueck: `sa-0-b9e9737e` Didaktik, `sa-1-f253a3a2` Architektur, nur Q-ANCHOR-INTERVENTION an T07/N32. Beide report.md/decision.json vollstaendig gelesen beziehungsweise maschinell nachgeprueft. Didaktik REQUIRE_CHILD_COMPLETED_LAYOUT gegen Architektur COMPOSITE_CHILD_PROOF; beide PROSPECTIVE_CLARIFICATION_REQUIRED. Elternabgleich bestaetigt je Rolle Pflichtdigests, alle verwendeten unveraenderlichen Quellen, Berichtbindung und Ereignisreferenzen; erlaubte STATUS-/WIEDERAUFNAHME-Aenderungen separat gegen den vorigen Checkpoint belegt. Keine Produkt-/native Ausfuehrung. Archiv mit Originalbytes `steuerung/gedaechtnis/entscheide/2026-11-27-ankerberatung-teil01/`; Rohbeleg `F:/ChnobelRuntime/verification/anchor-consultation-02/verification.json`, SHA-256 `fa35b7a6297e24d8dd35565d2c99ef0e1fba55dd37c27feca972b18a86da7c70`. Dissens erhalten, keine Mehrheit/Ratifikation ohne dritte Rolle.
- Nachfolgecheckpoint `95afeab4dd09593578d9abbfd98e39075313d44d` gepusht/remote bestaetigt und am 2026-11-27 nochmals als sauberer lokaler/Remote-Stand zurueckgelesen. `deleg_f0606d8f` nun abgeschlossen und verarbeitet: Red-Team COMPLETE zur Ankerfrage, Empfehlung COMPOSITE_CHILD_PROOF. Drei begrenzte Empfehlungen damit maschinell 2:1, kein Ganztextbeschluss; Didaktikdissens unveraendert. 35 unveraenderliche Red-Team-Quellen und 20 Ereignisreferenzen elterngeprueft, zwei erlaubte Kontextaenderungen separat gegen Gitobjekte. Archiv `steuerung/gedaechtnis/entscheide/2026-11-27-ankerberatung-teil02/`; neuer Elternbeleg `F:/ChnobelRuntime/verification/anchor-consultation-03/verification.json`, SHA-256 `3426367ea3dd75d067e9385ba435837de2c158855381026dc2982a062ae149a2`. Eine erneut zugestellte alte Batchmeldung ist keine neue Stimme.
- Ereignisautor aus demselben Batch: Prozess completed, Abgabe INCOMPLETE. Reiner elterlicher Dokument-Readback Exit 0: 209 historische Knoten = 201 RETAIN + 8 REPLACE; 5 ADD-Knoten fuer vier Zusatzfelder samt UUID-Element ergeben 214 eindeutige Knoten/Pointer. B-EVENT-DIGEST-TARGET fuer contentDigest/ruleDigest offen, keine Feldzielzuordnung aus Namen erraten. Hilfetextbindung nicht bearbeitet; keine semantische Fremdpruefung/Schemaausfuehrung. Gesamte neue Teilabgabe samt Brief und rohem Eltern-Readback verlustfrei unter `steuerung/gedaechtnis/pruefergebnisse/2026-11-27-ereignis-normalform-teil01/`; Rohwurzel `F:/ChnobelRuntime/specification/v2-field-supplement-02/event-normalform/`. Dies ist nicht das ganze urspruengliche Manifestbackup. Erster Elternhelferlauf scheiterte beim Vergleich unterschiedlich aufgebauter Quellmetadaten; Fehler erhalten, danach exakte Projektion und weiterhin alle Vorher-/Nachher-Checks. Keine Produktregel geaendert.
- Neuer Vorschlag `docs/adr/0004-zusammengesetzter-kindbeleg-entwurf.md` bleibt ENTWURF. Vollstaendiger Abstimmungsgegenstand `F:/ChnobelRuntime/reviews/adr0004-ratifikation-01/ballot.md`, SHA-256 `eaabc21a38b1bdc806f37444a6bdee00991004b462f9066d521cbb4b732d3b3c`; identische Repo-Bytes. Brief dort `brief.md`, SHA-256 `90528cb018b77674c2f2c65a3598f8864e036baeff1052f128449ce1d8bfa244`. Der neue Text legt nur einen engen zusammengesetzten Anker samt offengelegter App-Ruecknahme zur Abstimmung vor; die drei alten Empfehlungen sind keine Stimmen zu diesem Text.
- Aktiver neuer Batch `deleg_f43220be`: Didaktik `sa-0-9017494c` und Architektur `sa-1-7415e72f`, frische vollstaendige Ganztextvoten nur zu ADR 0004. Erwartete report.md/vote.json und optional sources.json unter derselben Runtimewurzel in didaktik/ bzw architekt/. Noch keine Voten verarbeitet. Red-Team-Ganztextvotum noch nicht beauftragt, erst nach freiem Platz in der Zwei-Agenten-Grenze. Danach bleibt die technische Digestzielklaerung als kleiner separater Quellen-/Spezifikationsauftrag moeglich. Kein Ganzmanifesturteil oder eigene Ratifikation durch Kinder. Eingefrorene Abstimmungsbytes/Brief und Dispatchuebergabe verlustfrei im Repo unter `steuerung/gedaechtnis/entscheide/2026-11-27-adr0004-entwurf01/`.
- Danach verbleiben Q-U07 und Q-GUARD-TOTALISATION je Rolle, B-EVENT-DIGEST-TARGET, die restlichen Feldvertraege/Hilfefelder sowie die anderen M-Punkte. Vollstaendige offene Folgeumfaenge und Dispatchbindung: `steuerung/gedaechtnis/arbeitsstand/v2-spezifikationsqueue-20261127-anker.json`. Ein COMPLETE nur fuer eine Frage oder einen Vertragsteil ist kein vollstaendiges Rollenurteil und kein Votum zum gesamten Manifest. Die offenen Umfaenge stehen im neuen Archivindex. Vor Freigabe muessen die erforderlichen Rollen vollstaendig gegen die exakte Fassung abgestimmt haben; die separate vollstaendige Manifestfassung mit Freeze/Fremdpruefung bleibt zusaetzlich erforderlich. Ein Normvorschlag wird erst nach gebundener Entscheidung verbindlich; kein vorgezogener Text-/Oracle-/Codewechsel.
- Bei erneut knappem Limit keine grosse neue Pruefung anfangen: STATUS/BLOCKER/WIEDERAUFNAHME aktualisieren, committen/pushen, SHAs live zuruecklesen und sauber anhalten. Laufende Kinder bei echter Unterbrechung sauber stoppen; unvollstaendige Ergebnisse niemals als Urteil ausgeben. Keine automatische Cron-Reaktivierung.
- Nach vollstaendigen Ruecklaeufen Faktenbelege von Produktvorschlaegen trennen, erforderliche Praezisierung separat verbindlich klaeren, erst dann neue vollstaendige Manifestfassung zusammenfuehren. Kein alter Entwurf/FAIL/Sollwert wird ueberschrieben. Keine Implementation, native Folgearbeit oder Integration vor dem Manifestgate.

Nur Runtime-Spezifikationswrites; keine Produktwriter. Ruecklaeufe werden automatisch in dieselbe aktive Arbeit geliefert; nicht pollen oder doppelt starten. Vor echter Unterbrechung Kinder sauber stoppen und den entstandenen Teilstand sichern; ein asynchroner Ruecklauf-Handoff ist noch kein Sitzungsabbruch.

Bei jedem Wiederanlauf: `steuerung/STATUS.md`, den gesamten `MASTERPROMPT.md`, `AGENTS.md`, `docs/adr/`, diese Anleitung, `steuerung/BLOCKER.md`, `steuerung/auftraege/phase-0.json` und `docs/red-team-register.md` lesen. Skill `chnobel-autonomy` laden. Massgebend sind Dateien, unveraenderliche Gitobjekte und echte Toolausgaben, nicht eine rekonstruierte Erinnerung.

## 2. Wo liegt was?

- Repository: https://github.com/mrdevn4ever-sys/learning-game-m (oeffentlich).
- Orchestrator-/Dokumentationsworktree: `F:/Projects/Chnobel`, Branch `ci/entwicklungspruefung`. Der Pausencommit dieses Branchs enthaelt diese Anleitung; seinen aktuellen SHA mit `git rev-parse HEAD` beziehungsweise `git ls-remote` feststellen. Vorgaenger vor der Pausensicherung: `dff0534b0bcc8d3eff016ca95bd9b591b02d2dc7`.
- Steuerung: `F:/Projects/Chnobel-Steuerung`, `feat/steuerung`, `e4a8f442272b75cfa0e1f7fd46c2d793b1fbd2ca`.
- Referenz/Vertraege: `F:/Projects/Chnobel-Vertraege`, `feat/vertraege-referenz`, `107f524a0529e84fb5dad78af7a7204edb6f649e`.
- iPad/Packages: `F:/Projects/Chnobel-iPad`, `feat/ipad-kern`, `c1ad063851f568eb3e376fdb7ca7802a59cb0d1b`.
- Native Diagnose: `F:/Projects/Chnobel-Nativ`, `ci/native-phase0`, `5246dbeb8e495563d0c04edd17fb24a8cc61ccf9`.
- Runtime, Umgebungen, rohe Logs, Portalbelege und Reproduktionen: `F:/ChnobelRuntime/`, ausserhalb Git. Das ist lokale Evidenz, nicht komplett als Git-Backup gesichert.
- Python: `F:/ChnobelRuntime/venv/Scripts/python.exe`. `TEMP`, `TMP`, `TMPDIR`, Bytecode- und Paketcache explizit nach F:; uv-Cache `F:/ChnobelRuntime/cache/uv`.
- Privater Pruefbereich: `mrdevn4ever-sys/chnobel-pruefung`. Keine verdeckten Aufgaben oder Secrets in das Produktrepo kopieren. Privatsichtbarkeit ist noch keine technische Isolation.

Die drei Reparatur-SHAs wurden gepusht und exakt zurueckgelesen. Remote-main zuletzt `9bab69c078f2c7dbfbca3b548ce1c8ef24a9ab61`, unveraendert. Bei Wiederaufnahme alle Ref-/Sauberkeitspruefungen erneuern. Keine Force-Pushes, keine ueberschriebenen Worktrees; alte FAIL-Snapshots erhalten.

## 3. Wie weit ist die App?

**Phase 0, nicht testbereit und kein TestFlight-Build.** Bootstrap/Betriebsbasis sind integriert; die Produktentwicklung liegt auf getrennten Arbeitsbranches. Ein minimaler SwiftUI-/SwiftData-Entwicklungskern fuer 8 + 7, sieben Swift-Packagemodule, Python-Referenzpruefer und SQLite-Steuerung sind implementiert, aber nicht gemeinsam abgenommen. Handschrifterkennung ist bewusst deaktiviert statt vorgetaeuscht. Breiter Lehrplan-/Inhaltsumfang, vollstaendige Accessibility, echte Handschrift, unabhaengiger Bildschirmabgleich, Release und Phasen 1–7 sind nicht erledigt.

Historische Elternnachtests der Reparaturkandidaten vom 2026-11-24 (neuere fremde Urteile stehen oben):
- Steuerung: 83/83 Python-Tests; Restore behaelt Job-/Wirkungsfristen. Fremdes Nachreview offen.
- Referenz: 232/232 Python-Tests; F01-F03 repariert laut Worker, unabhaengiges Nachreview offen. F04-F06 sind bekannte noch offene Vertrags-/Fachkonflikte.
- iPad: 40/40 **statische** Python-Tests. Kein Swift-/Xcode-PASS fuer diesen Reparatur-SHA. Laut Worker 77 Package-, 13 SwiftData- und 11 UI-Testdefinitionen vorbereitet.

Nicht additiv als Gesamtfreigabe verwenden: unterschiedliche Quellcommits, unterschiedliche Verfahren. Keine Skips oder erwarteten Fehler in den Elternlaeufen. Bytegleichheit alter Tests/Vertraege und Quellbindung wurden separat geprueft.

Evidenz im Repo:
- `steuerung/gedaechtnis/pruefergebnisse/2026-11-24-code-reviews/`: drei unveraenderte Original-FAILs als verlustfreie JSON-Zeilencontainer mit Hashindex.
- `steuerung/gedaechtnis/pruefergebnisse/2026-11-24-repair1-parent/`: Elternlaeufe und Checkpointmanifest. Rohlogs bleiben unter `F:/ChnobelRuntime/verification/`.
- `docs/red-team-register.md`: RT-01 bis RT-17; Kandidatenbindungen und offene Befunde werden durch eine Produktentscheidung nicht geschlossen.
- `produkt/werkzeuge/referenz/REPARATUR-1.md` im Referenzworktree und `produkt/App/REPARATUR-1.md` im iPadworktree: Implementierungsumfang und Grenzen.

## 4. Reviews und Gremium: nicht nochmals bei null anfangen

Original-FAILs betreffen:
- Steuerung `3bf45a586478a1c38ba8563bef7d0e8ad22e06e6`: Restore verkuerzt gespeicherte Fristen. Kein Wiederholungsupload nachgewiesen.
- Referenz `b8cd111453b2c44d28a5fc21125c4f9dbc95877e`: falsches Wissen nach Luecken, uebersehene neue Zonenwidersprueche und falscher Kind-Hilfezeitanker bei App-Undo; zusaetzlich 5/10, Invalidierung und Hilfeklassifikation.
- iPad `d71acbe65a602f091840ed5fa7e6069a157843c2`: falsche aktuelle Hilfefreiheit, definitive alte Antwort trotz Luecke, zustandsfremde Hilfe, Undo-Akteur und Korrekturprovenienz.

Erster Reparatur-/Gremiumsauftrag `deleg_c8c713b8` ist zurueck und in diesem Stand behandelt. Nicht erneut die alten Reparaturauftraege starten. Die drei Ausgangsvoten sind unveraendert unter `steuerung/gedaechtnis/entscheide/2026-11-24-reparatursemantik/` archiviert: D1/D2/D4 zwei JA/eine AENDERUNG, D3/D6 drei JA, D5 drei AENDERUNG.

`docs/adr/0003-aktionsbelege-und-prospektive-vertragsrevision.md` ist seit 2026-11-26 **ratifiziert fuer prospektive Produktentscheidungen**. Die nachfolgende eingefrorene Fassung war der exakte Abstimmungsgegenstand; ihr historischer Entwurfsstatus bleibt in den archivierten Originalbytes erhalten. Keine inhaltliche Aenderung der D1-D6 durch die redaktionelle Statusaktualisierung. Eingefrorene Ratifikationsfassung:
`F:/ChnobelRuntime/reviews/adr0003-ratifikation-0f97e89acd7cb6a2ad937949db57f704596e36c617af5ac31a655ac407975472.md`.
Hash: `0f97e89acd7cb6a2ad937949db57f704596e36c617af5ac31a655ac407975472`.

Bei Pausenwunsch wurde Stop fuer folgende sechs Kontexte angefordert; Ruecklaeufe koennen teilweise oder spaet eintreffen. Nicht als fertige Urteile behandeln und nicht durch ihren Eingang fortfahren:
- `deleg_87155b84`: `sa-0-3746c9cd` Steuerungsnachreview, `sa-1-24127e2b` Referenznachreview, `sa-2-1fcbb769` iPadnachreview.
- `deleg_afd52147`: `sa-0-57b1d82a` Architekt, `sa-1-1d39cd2a` Didaktik, `sa-2-a010be5a` Red-Team zur ADR-Ratifikation.

Pfade der beim Pausenstand erwarteten Berichte; die drei neuen Nachreviews und drei neuen Ratifikationsvoten sind nun vollstaendig und elternverifiziert, alte abgebrochene Kontexte bleiben unveraendert:
`F:/ChnobelRuntime/reviews/steuerung-repair1-review.md`, `referenz-repair1-review.md`, `ipad-repair1-review.md`, `adr0003-ratifikation-architekt.md`, `adr0003-ratifikation-didaktik.md`, `adr0003-ratifikation-redteam.md`.

Vollstaendige Delegationstranskripte: `C:/Users/user/AppData/Local/hermes/cache/delegation/live/<delegations-id>/task-0.log` bis `task-2.log`. Aeltere Batches: `deleg_fe139734` Originalreviews; `deleg_c8c713b8` sechs Reparatur-/Votumruecklaeufe; `deleg_51255299` native Diagnose. Nur abgeschlossene/angehaltene Ruecklaeufe zur Rekonstruktion lesen, nicht laufende Kinder pollen.

## 5. Native Diagnose getrennt rekonstruieren

- Draft-PR https://github.com/mrdevn4ever-sys/learning-game-m/pull/3, offen und Draft, Basis main, Head `5246dbeb8e495563d0c04edd17fb24a8cc61ccf9`.
- Run https://github.com/mrdevn4ever-sys/learning-game-m/actions/runs/45494829002: `completed/failure` am selben Head, bei Pausensicherung zurueckgelesen.
- Der Auftrag `deleg_51255299` ist kein laufender Produktwriter mehr; detaillierter Ruecklauf im aktuellen Uebergabeschritt noch nicht ausgewertet. Aus failure allein weder konkrete Swiftfehler noch Testfallzahlen erfinden. Exakte Jobs/Logs spaeter lesen.
- Diagnose-Snapshot basiert auf den gesperrten Originalproduktbaeumen. Eine separate Review-Sperre darf native Diagnose nicht als Produktfreigabe tarnen. Nicht mit den neueren Reparaturbranches vermischen.
- Nicht blind erneut dispatchen oder einen zweiten PR anlegen. Erst vorhandenen Run, Quellen und Auftrag abgleichen. Keine oeffentlichen Binaer-/Archiv-/IPA-Artefakte.

## 6. Einrichtung und echte Blocker

Bundle-ID `ch.chnobel.app` und App Store Connect Chnobel `6838908211`, SKU `CHNOBEL-IPADOS-001`, Deutsch/iOS/iPadOS, eingeschraenkter Zugriff sind angelegt. Letzter Portalbeleg: keine Builds, null Tester. Keine Gruppen/Einladungen. Mitgliedschaft/Vertraege und Signing bleiben offen.

Produktrepo oeffentlich, Actions aktiv; main verlangt PR, auch Admins, keine Force-Pushes/Loeschung. Pflichtstatuschecks fehlen noch. Produktrepo-Secrets/Environments zuletzt leer. Privates Pruefrepo: Actions aus. `independent-check` mit main-Branchpolicy, aber kein nachgewiesener Reviewer-/Bypassschutz. HTTP 422 beweist keinen Kontoplan. Zwoelf Rollen-/Sandbox-Testpaare NOT RUN.

Sichtbarer GitHub-Browser war nicht unter dem Repository-Owner angemeldet; Appregistrierung vor Absenden abgebrochen. Keine CLI-Credentials in Browser uebertragen. Keine Secret-Werte lesen/ausgeben, keine Vertragsanahmen oder Zahlungen. Namensliste und genaue Behebung unter `steuerung/BLOCKER.md`; bereits einmal kommuniziert, nicht wiederholt als neuer Fragebogen senden.

## 7. Konkrete Reihenfolge nach Fortsetzungsauftrag

1. Pause im STATUS bewusst aufheben, Live-Worktrees/Remote-SHAs und vorhandene Reviews/CI-Ergebnisse abgleichen. Keinen vorhandenen Stand ueberschreiben.
2. Unterbrochene Nachreviews und ADR-Ratifikation mit vorhandenen Belegen gezielt vervollstaendigen; nur neue exakte Kandidaten beurteilen. Alte FAILs bleiben unveraendert. Nach zwei Reparaturen gleicher Ursache andere Hypothese/unabhaengige Reproduktion verlangen.
3. Falls ADR 0003 ratifiziert: explizites v2-Revisions-/Fallmanifest **vor Implementierung** einfrieren und fremd pruefen. Alte v0/v1-Daten und Sollwerte erhalten; keine Tests passend zum Output umdefinieren.
4. Native Diagnosefehler am exakten SHA auswerten/reproduzieren; reparierte Kandidaten gesondert nativ pruefen und Python-/Swift-Fakten, Claims, Wortlaut, Fehlerkategorien und Dedupe gemeinsam abgleichen.
5. Erst danach regulare Integrationsgates und fremdes Review/PR-Merge. Originalauftragsdatei nicht manuell fuer erledigt erklaeren. Separat technische Identitaeten/Apple-Voraussetzungen herstellen; kein Upload ohne gueltige finale Gates.

Der Chnobel-Cron `26647d618052` ist pausiert (`enabled: false`, `next_run_at: null`). Andere Projekte wurden nicht angehalten. Nicht automatisch nach Limitreset reaktivieren. Fuer interaktive Fortsetzung bleibt Cron aus, damit keine doppelten Schreiber entstehen.
