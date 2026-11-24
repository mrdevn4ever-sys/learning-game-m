# ADR 0002: Entwicklungsgrenze und technische Identitaeten

Status: verbindlich
Datum: 2026-11-24
Geltung: neue Entwicklungskandidaten nach Startpaket `144c9b3f8a2b03907cca41ed30ac81fdc196d91d`.

## Entscheidung

1. Oeffentliche Entwicklungs-CI darf nur offene synthetische Regressionen ausfuehren, mit minimalen Leserechten und ohne Secrets, verdeckte Pruefdaten, Build-/Archiv-/IPA-Uploads. Sie ist kein Schlussabnahmebeleg. Privilegierte Jobs werden nicht als gruenes Echo oder uebersprungener Erfolg eingefuehrt.
2. Private Abnahme und Release bleiben gesperrt, bis verschiedene technische Identitaeten, negative Zugriffstests und Isolation des laufenden Kandidaten nachgewiesen sind. Private Sichtbarkeit allein reicht nicht. Die Einrichtung eines leeren privaten Bereichs ist kein Abnahmebetrieb.
3. Plattformneutraler Swift-6-Kern, SwiftUI/SwiftData-Adapter fuer iPadOS ab 18. Kein Drittanbieter-SDK in der App. Python-Referenzpruefer und Steuerung sind Build-/Pruefwerkzeuge ausserhalb der App.
4. Unverifizierte Handschrifterkennung bleibt deaktiviert. Der Ziffernblock ist eine direkte Entwicklungseingabe. Synthetische Lesarten existieren nur als offene Vertragstests, niemals als vorgetaeuschte CoreML-Leistung im Produkt. Die Handschrift-Abnahmeschwellen bleiben unveraendert.
5. Ergebnis, wirksamer dargestellter Weg, historische Handlung und Zeitpunkt/Herkunft der Hilfe bleiben getrennt. Unbekannte Fakten sperren nur abhaengige Aussagen. Ein Fallback-Claim wird immer durch seine eigene Regel geprueft.
6. Der Pflichtstatus wird nach Einfuehrung der Entwicklungsjobs an die GitHub-Actions-App gebunden. Der spaetere Freigabedienst muss zusaetzlich unveraenderliche Regeln, erwartete positive Fallzahlen, tatsaechliche Ausfuehrung, autorisierte Aussteller und Kandidaten-/Artefaktbindung pruefen. Ein lokaler Bericht ist kein authentisierter Freigabebeleg.

## Gremium

Drei getrennte Kontexte: Architekt JA; zustaendige Fachkritik JA zur engen fachlichen Architektur; Red-Team JA zur Sicherheitsgrenze und ausschliesslich zum passiven Bootstrap-Import. Red-Team-Befunde RT-01/02/03 bleiben im Register unabhaengig von Mehrheitsstimmen erhalten. Kontexttrennung ist keine Credential-Trennung.

## Begruendung und Reichweite

Dies konkretisiert die strengeren Grenzen aus Masterprompt 1, 6.1, 7, 18 und 19; es ueberschreibt keine Masterprompt-Anforderung. Die Einrichtungs-Secretliste wird als Namensvertrag, nicht als Erlaubnis zur Freigabe von Secrets an beliebige Produktworkflows ausgelegt. Einrichtung und Entwicklung sind erlaubt; die fehlende Rollen-/Apple-Infrastruktur blockiert privilegierte Wirkung.

## Quellen der Toolchain-Pruefung

Am 2026-11-24 gelesen: https://developer.apple.com/news/upcoming-requirements/ (seit 2026-04-28 Xcode 26+ und iOS/iPadOS-26-SDK; Deployment Target bleibt getrennt). Runner-Inventar: https://raw.githubusercontent.com/actions/runner-images/main/images/macos/macos-26-arm64-Readme.md (Xcode 26.6, iOS-SDK 26.5 und iPad-Simulatoren dokumentiert). Fuer die tatsaechliche Konfiguration wird die aktuelle stabile Toolchain erneut geprueft; Quelle allein ist kein ausgefuehrter Build. Vor jedem Release erneut pruefen.
