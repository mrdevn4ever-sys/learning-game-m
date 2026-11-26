# Chnobel: Wiederaufnahme und gesicherter Pausenstand

Stand: 2026-11-26. Die Nutzerpause vom 2026-11-24 wurde durch den ausdruecklichen Auftrag "Chnobel weiter" aufgehoben. Separater Statuscommit: `d4a66d62c499d6f25c3eb1f8625972976c7c4fd2`, gepusht und live zurueckgelesen.

## 1. Zuerst beachten

**Interaktive Fortsetzung erlaubt; Cron bleibt aus.** ZUSTAND und BETRIEB stehen auf IN_ARBEIT. Der Nutzerauftrag vom 2026-11-26 erlaubt die Fortsetzung ab `4e31d37c911a45a519ae728adebfbd45b328983c` und verlangt unveraenderte Gates sowie die Reihenfolge in Abschnitt 7. Die erste Live-Pruefung bestaetigte alle fuenf sauberen Worktrees und die erwarteten lokalen/Remote-SHAs. Keine lebenden Subagenten beim Start. Cron `26647d618052`: enabled false, state paused, next_run_at null. Bei erneuter Nutzerpause keine automatische Fortsetzung durch Sitzung, Limitreset, Cron oder Ruecklauf. Geschuetzte Instruktionsdateien ohne ausdrueckliche Dialogzustimmung nicht aendern; die frueher abgewiesene AGENTS.md-Aenderung ist nicht gelandet.

### Nachreview-Abgleich vom 2026-11-26

Beide alten Delegationsmanifeste und die Endmarker aller sechs Transkripte melden `interrupted`. Alle sechs unter Abschnitt 4 erwarteten Abschlussberichte fehlen. Keine vollstaendigen Urteile, keine Ratifikation. Die alten Teilbelege bleiben unveraendert und sind nur Ausgangsmaterial fuer frische fremde Kontexte. Maschinenlesbarer Abgleich: `F:/ChnobelRuntime/reviews/wiederaufnahme-20261126/abgleich.json`, SHA-256 `dcb023d365e998fbb78bbb10e2a22b5461a9b41eab0ff340db0e9df7efd9d131`. Zuerst drei gezielte Nachreviews gegen die unten genannten exakten Reparatur-SHAs, danach die drei Ratifikationsvoten. Kein Neustart von `deleg_c8c713b8`, keine v2-Implementierung, kein CI-Neustart oder zweiter PR.

Aktive Nachreview-Delegation `deleg_5f23880a`: `sa-0-40bc0516` Steuerung, `sa-1-1cee643e` Referenz, `sa-2-01e3e3c4` iPad. Nur Runtime-Reviewwrites; keine Produktwriter. Die erwarteten Abschlussberichte behalten die Pfade in Abschnitt 4, neue Evidenz liegt unter `F:/ChnobelRuntime/reviews/fortsetzung-20261126/{steuerung,referenz,ipad}/`. Ruecklaeufe werden automatisch in dieselbe aktive Arbeit geliefert; nicht pollen oder doppelt starten. Vor echter Unterbrechung Kinder sauber stoppen und den entstandenen Teilstand sichern; ein asynchroner Ruecklauf-Handoff ist noch kein Sitzungsabbruch.

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

Verifizierte Elternnachtests der Reparaturkandidaten:
- Steuerung: 83/83 Python-Tests; Restore behaelt Job-/Wirkungsfristen. Fremdes Nachreview offen.
- Referenz: 232/232 Python-Tests; F01-F03 repariert laut Worker, unabhaengiges Nachreview offen. F04-F06 sind bekannte noch offene Vertrags-/Fachkonflikte.
- iPad: 40/40 **statische** Python-Tests. Kein Swift-/Xcode-PASS fuer diesen Reparatur-SHA. Laut Worker 77 Package-, 13 SwiftData- und 11 UI-Testdefinitionen vorbereitet.

Nicht additiv als Gesamtfreigabe verwenden: unterschiedliche Quellcommits, unterschiedliche Verfahren. Keine Skips oder erwarteten Fehler in den Elternlaeufen. Bytegleichheit alter Tests/Vertraege und Quellbindung wurden separat geprueft.

Evidenz im Repo:
- `steuerung/gedaechtnis/pruefergebnisse/2026-11-24-code-reviews/`: drei unveraenderte Original-FAILs als verlustfreie JSON-Zeilencontainer mit Hashindex.
- `steuerung/gedaechtnis/pruefergebnisse/2026-11-24-repair1-parent/`: Elternlaeufe und Checkpointmanifest. Rohlogs bleiben unter `F:/ChnobelRuntime/verification/`.
- `docs/red-team-register.md`: RT-01 bis RT-15, nicht durch eigene Tests geschlossen.
- `produkt/werkzeuge/referenz/REPARATUR-1.md` im Referenzworktree und `produkt/App/REPARATUR-1.md` im iPadworktree: Implementierungsumfang und Grenzen.

## 4. Reviews und Gremium: nicht nochmals bei null anfangen

Original-FAILs betreffen:
- Steuerung `3bf45a586478a1c38ba8563bef7d0e8ad22e06e6`: Restore verkuerzt gespeicherte Fristen. Kein Wiederholungsupload nachgewiesen.
- Referenz `b8cd111453b2c44d28a5fc21125c4f9dbc95877e`: falsches Wissen nach Luecken, uebersehene neue Zonenwidersprueche und falscher Kind-Hilfezeitanker bei App-Undo; zusaetzlich 5/10, Invalidierung und Hilfeklassifikation.
- iPad `d71acbe65a602f091840ed5fa7e6069a157843c2`: falsche aktuelle Hilfefreiheit, definitive alte Antwort trotz Luecke, zustandsfremde Hilfe, Undo-Akteur und Korrekturprovenienz.

Erster Reparatur-/Gremiumsauftrag `deleg_c8c713b8` ist zurueck und in diesem Stand behandelt. Nicht erneut die alten Reparaturauftraege starten. Die drei Ausgangsvoten sind unveraendert unter `steuerung/gedaechtnis/entscheide/2026-11-24-reparatursemantik/` archiviert: D1/D2/D4 zwei JA/eine AENDERUNG, D3/D6 drei JA, D5 drei AENDERUNG.

`docs/adr/0003-aktionsbelege-und-prospektive-vertragsrevision.md` ist der konsolidierte **Entwurf**, noch nicht verbindlich. Eingefrorene Ratifikationsfassung:
`F:/ChnobelRuntime/reviews/adr0003-ratifikation-0f97e89acd7cb6a2ad937949db57f704596e36c617af5ac31a655ac407975472.md`.
Hash: `0f97e89acd7cb6a2ad937949db57f704596e36c617af5ac31a655ac407975472`.

Bei Pausenwunsch wurde Stop fuer folgende sechs Kontexte angefordert; Ruecklaeufe koennen teilweise oder spaet eintreffen. Nicht als fertige Urteile behandeln und nicht durch ihren Eingang fortfahren:
- `deleg_87155b84`: `sa-0-3746c9cd` Steuerungsnachreview, `sa-1-24127e2b` Referenznachreview, `sa-2-1fcbb769` iPadnachreview.
- `deleg_afd52147`: `sa-0-57b1d82a` Architekt, `sa-1-1d39cd2a` Didaktik, `sa-2-a010be5a` Red-Team zur ADR-Ratifikation.

Erwartete neue Berichte, deren Vollstaendigkeit erst nach Wiederaufnahme zu pruefen ist:
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
