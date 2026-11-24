# Technische Rollen: Entwurf und verifizierter Einrichtungsstand

Stand: 2026-11-24. Planungsnotiz, kein verbindlicher ADR, keine Produktfreigabe.

## Unabhaengiger Befund

Ein fremder Sicherheitskontext hat eine Least-Privilege-Architektur fuer das persoenliche GitHub-Konto beschrieben. Der unveraenderte Originalbericht liegt ausserhalb Git unter `F:/ChnobelRuntime/reviews/identitaeten.md`. Seine anonymen Repository-Messungen gelten fuer den dort genannten Zeitpunkt und Commit, nicht automatisch fuer spaetere Kandidaten.

Vorgeschlagene Grenzen:

- Produktworker ohne unmittelbares GitHub-Schreibcredential; oeffentlicher Abruf und lokal begrenzte Vorschlaege.
- Deterministischer Publikations-/Steuerungsdienst mit eigener privater GitHub App nur fuer das Produktrepository. Enger Inhalt-/PR-Schreibzugriff, Pruefstatus nur lesend; keine Administration, Workflows, Pruefdaten oder Apple-Rechte.
- Separater Pruefdaten-Leser nur fuer das private Pruefrepository, eigener Autorenschreibweg und eigener Urteilsaussteller nur fuer redigierte Statusmeldungen im Produktrepository. Der Kandidatenprozess erhaelt weder Token noch Sollwissen.
- Getrennter Release-Dienst nur mit geprueftem, unveraenderlichem Archiv und zugelassenem Chnobel-Auftrag. Kein Neubau, keine Testergruppen, Einladungen oder Store-Freigabe.
- Zwei getrennte main-Rulesets: Gates ohne Bypass und ausschliessliches PR-Mergerecht der Steuerung. Ein gemeinsamer Bypass darf nicht gleichzeitig Gates ausnehmen.
- Echte Prozess-/VM-, Credential- und Artefaktgrenzen; getrennte Worktrees oder Rollenbezeichnungen allein genuegen nicht.

Der Bericht definiert zwoelf positive/negative Zugriffstestpaare. **Alle bleiben NOT RUN.** Eine fehlgeschlagene Anmeldung oder ein unbekanntes Ziel ist keine bestandene negative Zugriffskontrolle. Pro Negativtest ist eine passende erfolgreiche Positivkontrolle erforderlich.

## Eigener Live-Abgleich und Teilkonfiguration

- Produktrepository: klassischer main-Schutz mit Admin-Einbezug vorhanden; `required_status_checks=null`; Ruleset-Liste leer. Kein behaupteter Pflichtstatus-/Mergeidentitaetsbeleg.
- Privates Pruefrepository: Actions weiterhin deaktiviert.
- Die Erstellung des Environments `independent-check` mit Reviewer-Schutz scheiterte mit HTTP 422: Der Tarif unterstuetzt die angefragte Reviewer-Regel nicht. Trotz Fehler wurde das leere Environment angelegt. Dieser Teilzustand wurde zurueckgelesen und nicht als erfolgreiche Schutzkonfiguration verbucht.
- Die danach separat eingerichtete Branch-Policy wurde gespeichert und zurueckgelesen: ausschliesslich Branch `main`, keine Tag-Policy. Environment-Secrets: leere Namensliste. `can_admins_bypass=true`; kein Reviewer-Schutz und keine Job-/Rollenisolation nachgewiesen.
- Keine Freigabeschwelle geaendert. Actions im privaten Repository bleiben aus; keine Credentials, verdeckten Pruefdaten oder Builds hinzugefuegt.
- Der Kontotarif bleibt unbekannt. Die tatsaechlich moegliche Basis-Environment-Konfiguration widerlegt eine pauschale Behauptung, schon jede private Environment sei in dieser konkreten Umgebung unmoeglich. Sie belegt keine Verfuegbarkeit erweiterter Schutzregeln.

## Offener Browser-Zugang

Der sichtbare Chrome ist bei einem anderen GitHub-Konto angemeldet als der fuer dieses Projekt verifizierte CLI-Owner `mrdevn4ever-sys`. Im Account-Switcher war kein bereits angemeldeter Projekt-Owner verfuegbar. Die vorbereitete private App-Registrierung wurde vor Absenden abgebrochen. Keine GitHub App, Installation, Client-Secrets oder privaten Schluessel angelegt.

Der fremde Browserkontoname bleibt nur im lokalen Portalbeleg. Kein Konto wird still ausgeloggt, kein Credential zwischen CLI und Browser uebertragen. Die App-Registrierung benoetigt den korrekten Owner-Kontext; unabhaengige Entwicklung und Reviews sind davon nicht blockiert.

## Apple-Grenze

Apple-Teamkeys haben keine native Beschraenkung auf Chnobel. Der Release-Dienst muss daher vor jedem Netzauftrag App-ID, Bundle-ID, Team, Archivdigest, Buildnummer und erlaubte Operation deterministisch binden. Ein solcher Broker darf nicht als native Einschraenkung des Apple-Schluessels bezeichnet werden. Seine Isolation und Negativtests sind weiterhin offen; der Entwurf ist keine Freigabe und rechtfertigt keine Secretuebertragung.

## Naechste Belege

1. Korrekte Owner-Oberflaeche fuer private App-Registrierungen; getrennte, minimal berechtigte Installationen und Credential-Kontexte.
2. Echter Pflichtstatuslauf der oeffentlichen Entwicklungs-CI; anschliessend Bindung an die beobachtete CI-Identitaet.
3. Gremium/ADR fuer die endgueltige Architektur, unabhaengige Implementierungspruefung und ausgefuehrte Zugriffstestpaare mit exakten Policies und Positivkontrollen.
4. Erst danach privilegierte Pruefung, Signing und Upload freischalten. RT-01/RT-02 bleiben offen.

## Oeffentliche Quellen

- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments
- https://docs.github.com/en/rest/deployments/environments#create-or-update-an-environment
- https://docs.github.com/en/apps/sharing-github-apps/registering-a-github-app-using-url-parameters
- https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app
- https://developer.apple.com/documentation/appstoreconnectapi/creating-api-keys-for-app-store-connect-api
