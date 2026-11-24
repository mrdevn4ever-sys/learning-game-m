"""Eigene offene Regressionen. Sollwerte sind von Hand gesetzt, nicht berechnet.

Dies ist KEIN verdeckter Pruefsatz und kein unabhaengiges Abnahmeurteil.
Erneuter Export: python -m produkt.werkzeuge.referenz.offene_spuren --write
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

CLAIMS = ("attempt.result.correct", "attempt.ten", "attempt.ten.guided",
          "attempt.alternative", "attempt.path.displayed")
C, N, U = "must_claim", "must_not_claim", "undecidable"


def uid(label: str) -> str:
    return str(uuid5(NAMESPACE_URL, "https://chnobel.local/offen/v1/" + label))


class Trace:
    def __init__(self, name: str):
        self.name = name
        self.events = []
        self.serial = 0
        self.left = [uid(f"{name}/a/{n}") for n in range(8)]
        self.right = [uid(f"{name}/b/{n}") for n in range(7)]
        self.input_id = self.recognition_id = self.answer_id = None
        self.add("attempt.opened", {
            "taskContract": "sum-8-7", "taskVersion": "1.0.0", "family": "addition-20",
            "representation": "counters", "target": "sum-8-7", "startingState": "board-8-7-v1",
            "profileId": uid(name + "/profile"),
            "initialMaterial": [{"itemId": item, "zone": zone, "origin": "task"}
                                for zone, items in [("left", self.left), ("right", self.right)]
                                for item in items]}, "system")

    def identifier(self, kind: str) -> str:
        self.serial += 1
        return uid(f"{self.name}/{kind}/{self.serial}")

    def add(self, kind: str, payload: dict, actor: str = "child") -> dict:
        event = {"schemaVersion": "1.0.0", "type": kind, "eventId": self.identifier("event"),
                 "streamId": uid(self.name + "/stream"), "seq": len(self.events),
                 "occurredAt": "2026-11-22T09:00:00Z", "actor": actor,
                 "candidate": {"build": "offener-referenzfall-v1", "content": "1.0.0", "rules": "1.0.0"},
                 "payload": payload}
        self.events.append(event)
        return event

    def capture(self, mode: str = "ziffernblock") -> None:
        self.input_id = self.identifier("input")
        self.add("input.captured", {"inputId": self.input_id, "mode": mode})

    def recognition(self, reading: str = "16") -> None:
        self.capture("handschrift_finger")
        self.recognition_id = self.identifier("recognition")
        self.add("recognition.proposed", {"recognitionId": self.recognition_id,
                 "inputId": self.input_id, "reading": reading, "confidence": 0.58,
                 "alternatives": ["15"] if reading != "15" else []}, "app")

    def answer(self, value: int = 15, origin: str = "direkt") -> None:
        if origin == "direkt":
            self.capture()
        self.answer_id = self.identifier("answer")
        p = {"answerId": self.answer_id, "inputId": self.input_id, "value": value, "origin": origin}
        if origin != "direkt":
            p["fromRecognitionId"] = self.recognition_id
        self.add("answer.committed", p, "app" if origin == "automatisch_uebernommen" else "child")

    def move(self, items: list[str] | None = None, source: str = "right", target: str = "left",
             actor: str = "child", via: str | None = None) -> str:
        move_id = self.identifier("move")
        self.add("material.moved", {"moveId": move_id, "items": self.right[:2] if items is None else items,
                 "fromZone": source, "toZone": target,
                 "via": via or ("app_demo" if actor == "app" else "ziehen")}, actor)
        return move_id

    def undo(self, move_id: str, actor: str = "child") -> None:
        self.add("action.undone", {"moveId": move_id}, actor)

    def support(self, target: str = "ten.step", effect: str = "hinweis") -> None:
        self.add("support.presented", {"supportId": self.identifier("support"), "kind": "aufmerksamkeit" if effect == "neutral" else "teilschritt",
                 "target": target, "effect": effect, "channel": "visuell"}, "app")

    def condition(self, kind: str = "gap", since: int | None = None) -> None:
        p = {"kind": kind, "detail": "Offene synthetische Gegenprobe"}
        if kind == "gap":
            p["sinceSeq"] = len(self.events) if since is None else since
        self.add("condition.observed", p, "system")

    def close(self, reason: str = "submitted") -> None:
        self.add("attempt.closed", {"reason": reason}, "system")


def build_traces() -> tuple[dict, dict]:
    traces, invalid = {}, {}

    def save(t: Trace, description: str, outcomes: tuple, close: bool = True) -> None:
        if close:
            t.close()
        assert len(outcomes) == len(CLAIMS)
        traces[t.name] = {"id": t.name, "description": description, "events": deepcopy(t.events),
                          "expected": dict(zip(CLAIMS, outcomes, strict=True))}

    t = Trace("antwort-15"); t.answer()
    save(t, "Direkte richtige Antwort ist kein beobachteter Rechenweg.", (C, N, N, N, N))
    t = Trace("antwort-14"); t.answer(14)
    save(t, "Direkte abweichende Eingabe, keine Fehlvorstellungsdiagnose.", (N, N, N, N, N))
    save(Trace("leere-abgabe"), "Abgabe ohne Antwort ist unbekannt, nicht falsch.", (U, N, N, N, N))
    t = Trace("lesart-16"); t.recognition()
    save(t, "Unbestaetigte Lesart erzeugt keinen fachlichen Fehler.", (U, N, N, N, N))
    t = Trace("korrigierte-fehllesung"); t.recognition(); t.answer(15, "korrigiert")
    save(t, "Lesart 16 wird mit explizitem Bezug zu 15 korrigiert.", (C, N, N, N, N))
    t = Trace("lesart-zwischenzustand"); t.recognition()
    save(t, "Zwischenzustand vor der Korrektur bleibt ohne Rechenfehler.", (U, N, N, N, N), False)
    t = Trace("frei-zehnerweg"); t.move()
    save(t, "Freier Zehnerweg belegt keine unbekannte Ergebniseingabe.", (U, C, N, N, C))
    t = Trace("frei-zehnerweg-ergebnis"); t.move(); t.answer()
    save(t, "Eigenstaendiger Zehnerschritt und korrektes Ergebnis sind getrennt.", (C, C, N, N, C))
    t = Trace("zehnerweg-falsches-ergebnis"); t.move(); t.answer(14)
    save(t, "Ein Zehnerweg darf keinen positiven Ergebnis-Fallback erzwingen.", (N, C, N, N, C))
    t = Trace("hinweis-vor-zug"); t.support(); t.move(); t.answer()
    save(t, "Hinweis vor der Handlung: angeleiteter, aber gueltiger Weg.", (C, N, C, N, C))
    t = Trace("hinweis-falsches-ergebnis"); t.support(); t.move(); t.answer(14)
    save(t, "Unfreie Strategie darf keinen falschen Ergebnis-Fallback freigeben.", (N, N, C, N, C))
    t = Trace("hinweis-ohne-ergebnis"); t.support(); t.move()
    save(t, "Unfreie Strategie darf keine fehlende Ergebniseingabe erfinden.", (U, N, C, N, C))
    t = Trace("hinweis-nach-zug"); t.move(); t.support(); t.answer()
    save(t, "Ein spaeterer Hinweis entwertet den bereits freien Schritt nicht.", (C, C, N, N, C))
    t = Trace("undo"); m = t.move(); t.undo(m); t.answer()
    save(t, "Undo entfernt den wirksamen Weg, nicht seine Historie.", (C, N, N, N, N))
    t = Trace("undo-hinweis-erneut"); m = t.move(); t.undo(m); t.support(); t.move(); t.answer()
    save(t, "Nach Undo gilt fuer den erneuten Zug die nun vorhandene Hilfe.", (C, N, C, N, C))
    t = Trace("app-demo"); t.move(actor="app"); t.answer()
    save(t, "App-Materialbewegung ist kein vom Kind dargestellter Weg.", (C, N, N, N, N))
    t = Trace("demo-wiederholung"); m = t.move(actor="app"); t.undo(m, "app"); t.move(); t.answer()
    save(t, "Eine Wiederholung nach Demo bleibt angeleitet, auch nach Undo.", (C, N, C, N, C))
    t = Trace("alternativ-7-7-1"); t.move(t.left[:1], "left", "spare"); t.answer()
    save(t, "Ein gueltiger anderer Weg: ein Plaettchen der Acht abtrennen.", (C, N, N, C, C))
    t = Trace("alternativ-zwei-zuege"); t.move(t.left[:1], "left", "right"); t.move(t.right[:1], "right", "spare"); t.answer()
    save(t, "Andere Bewegung und andere Plaettchen erreichen ebenfalls 7+7+1.", (C, N, N, C, C))
    t = Trace("luecke-vor-zug"); t.condition(); t.move(); t.answer()
    save(t, "Luecke verhindert Weg-/Hilfeschluss, spaetere 15 bleibt anerkannt.", (C, U, U, U, U))
    t = Trace("sequenzluecke"); t.move(); t.answer(); t.close()
    for e in t.events[1:]: e["seq"] += 1
    save(t, "Auch ohne gap-Meldung wird eine Sequenzluecke erkannt.", (C, U, U, U, U), False)
    t = Trace("luecke-nach-zug"); t.move(); t.condition(); t.answer()
    save(t, "Fehlende spaetere Bewegungen koennen den wirksamen Weg aendern.", (C, U, U, U, U))
    t = Trace("luecke-nach-antwort"); t.answer(); t.condition()
    save(t, "Eine fehlende Ruecknahme nach der Antwort ist nicht ausgeschlossen.", (U, U, U, U, U))
    t = Trace("abbruch"); t.close("aborted")
    save(t, "Abbruch ist ein belegtes Veto gegen eine Abgabeaussage.", (N, N, N, N, N), False)
    t = Trace("abbruch-mit-15"); t.answer(); t.close("aborted")
    save(t, "Die Eingabe bleibt Fakt; eine Abgabeaussage wird nicht behauptet.", (N, N, N, N, N), False)
    t = Trace("abschluss-fehlt"); t.answer()
    save(t, "Fehlender Abschluss ist unbekannt, nicht Abbruch.", (U, N, N, N, N), False)
    t = Trace("uhr-unsicher"); t.condition("clock_unreliable"); t.move(); t.answer()
    save(t, "Sequenz belegt den Weg; zeitlicher Transfer wird nicht behauptet.", (C, C, N, N, C))
    t = Trace("neutraler-hinweis"); t.support(effect="neutral"); t.move(); t.answer()
    save(t, "Explizit neutrale Darstellung ist kein verratender Zehnerhinweis.", (C, C, N, N, C))
    t = Trace("anderes-hilfeziel"); t.support(target="result"); t.move(); t.answer()
    save(t, "Nur die enge Aussage ohne Hinweis auf den Zehnerschritt ist erlaubt.", (C, C, N, N, C))
    t = Trace("antwort-zurueckgenommen"); t.answer(); t.add("response.retracted", {"answerId": t.answer_id})
    save(t, "Eine zurueckgenommene Antwort ist kein aktuelles Ergebnis.", (U, N, N, N, N))
    t = Trace("antwort-ersetzt"); t.answer(14); t.add("response.retracted", {"answerId": t.answer_id}); t.answer()
    save(t, "Explizite Ruecknahme und neue direkte Antwort.", (C, N, N, N, N))
    t = Trace("automatisch-16"); t.recognition(); t.answer(16, "automatisch_uebernommen")
    save(t, "Automatische Uebernahme einer Lesart ist kein fachlicher Fehler.", (U, N, N, N, N))
    t = Trace("automatisch-15"); t.recognition("15"); t.answer(15, "automatisch_uebernommen")
    save(t, "Auch eine automatisch richtige Lesart ist nicht bestaetigt.", (U, N, N, N, N))
    t = Trace("doppelte-zustellung"); t.move(); t.answer(); t.close(); t.events.append(deepcopy(t.events[1]))
    save(t, "Identisches Ereignis wirkt trotz doppelter Zustellung nur einmal.", (C, C, N, N, C), False)
    t = Trace("ungeordnete-zustellung"); t.move(); t.answer(); t.close(); t.events.reverse()
    save(t, "Zustellreihenfolge ist nicht die fachliche Sequenz.", (C, C, N, N, C), False)
    t = Trace("inhalt-zurueckgezogen"); t.move(); t.answer(); t.close(); t.add("content.withdrawn", {"content": "1.0.0", "reason": "Offene Gegenprobe"}, "system")
    save(t, "Inhaltsrueckzug sperrt daraus abgeleitete Aussagen.", (N, N, N, N, N), False)
    t = Trace("beobachtung-invalidiert"); t.move(); t.answer(); t.close(); t.add("observation.invalidated", {"eventIds": [t.events[1]["eventId"]], "reason": "Offene Gegenprobe"}, "system")
    save(t, "Invalidierte Beobachtung bleibt als Historie, nicht als gueltiger Nachweis.", (N, N, N, N, N), False)
    t = Trace("profil-loeschung"); t.move(); t.answer(); t.close(); t.add("profile.erasure_requested", {"profileId": t.events[0]["payload"]["profileId"]}, "system")
    save(t, "Loeschabsicht sperrt die Auswertung; physische Loeschung ist Adaptersache.", (N, N, N, N, N), False)
    t = Trace("unterbrechung"); t.condition("interruption"); t.move(); t.answer()
    save(t, "Unterbrochene Beobachtung belegt keine Abwesenheit von Hilfe.", (C, U, U, U, U))
    t = Trace("selbstbericht"); t.add("self_report.recorded", {"reportId": t.identifier("report"), "target": "ten.step", "value": True}); t.answer()
    save(t, "Selbstauskunft ist keine beobachtete Materialhandlung.", (C, N, N, N, N))
    t = Trace("importiertes-werk"); t.add("artifact.saved", {"artifactId": t.identifier("artifact"), "origin": "importiert", "digest": "0" * 64, "mediaType": "drawing"})
    save(t, "Importiertes Werk erzeugt keine eigene Ausfuehrungsleistung.", (U, N, N, N, N))
    t = Trace("weg-zwischenzustand"); t.move()
    save(t, "Ein wirksamer Weg ohne Abschluss bleibt fuer Abgabeaussagen offen.", (U, U, N, N, U), False)
    t = Trace("zwei-einzelzuege"); t.move(t.right[:1]); t.move(t.right[1:2]); t.answer()
    save(t, "Zwei wirksame Einzelzuege sind derselbe gueltige Zehnerweg.", (C, C, N, N, C))
    t = Trace("bestaetigte-lesart"); t.recognition("15"); t.answer(15, "bestaetigt")
    save(t, "Bestaetigte Lesart mit identischem Wert.", (C, N, N, N, N))

    t = Trace("ziffernblock-nach-rueckfrage"); t.recognition(); t.add("mode.changed", {"from": "handschrift_finger", "to": "ziffernblock"}); t.answer()
    save(t, "Direkte Alternative nach Lesart ohne verdeckte Vorbelegung.", (C, N, N, N, N))
    t = Trace("anhang-geloescht"); artifact = t.identifier("artifact"); t.add("artifact.saved", {"artifactId": artifact, "origin": "selbst_erstellt", "digest": "0" * 64, "mediaType": "drawing"}); t.answer(); t.close(); t.add("artifact.deleted", {"artifactId": artifact}, "system")
    save(t, "Anhangsloeschung aendert die erhaltene direkte Ergebniseingabe nicht.", (C, N, N, N, N), False)

    def bad(name: str, source: str, error: str, mutate) -> None:
        row = deepcopy(traces[source])
        row["id"] = name
        row["description"] = "Absichtlich ungueltige offene Gegenprobe: " + name
        row.pop("expected")
        row["expectedError"] = error
        mutate(row["events"])
        invalid[name] = row

    bad("kind-app-demo", "frei-zehnerweg", "schema", lambda es: es[1]["payload"].update(via="app_demo"))
    bad("doppelte-plaettchen", "frei-zehnerweg", "schema", lambda es: es[1]["payload"]["items"].append(es[1]["payload"]["items"][0]))
    bad("abschluss-ohne-grund", "antwort-15", "schema", lambda es: es[-1]["payload"].clear())
    bad("korrektur-ohne-bezug", "korrigierte-fehllesung", "schema", lambda es: es[3]["payload"].pop("fromRecognitionId"))
    bad("uuid-ungueltig", "antwort-15", "schema", lambda es: es[0].update(streamId="kein-uuid"))
    bad("lesart-fremder-bezug", "korrigierte-fehllesung", "dangling_reference", lambda es: es[3]["payload"].update(fromRecognitionId=uid("nicht-vorhanden")))
    bad("event-id-konflikt", "doppelte-zustellung", "event_id_conflict", lambda es: es[-1]["payload"].update(via="tastatur"))
    bad("seq-konflikt", "antwort-15", "sequence_conflict", lambda es: es[2].update(seq=1))
    bad("fremder-stream", "antwort-15", "foreign_stream", lambda es: es[2].update(streamId=uid("fremder-stream")))
    bad("fremdes-material", "frei-zehnerweg", "unknown_material", lambda es: es[1]["payload"].update(items=[uid("fremdes-material")]))
    bad("falsche-ausgangszone", "frei-zehnerweg", "wrong_source", lambda es: es[1]["payload"].update(fromZone="spare"))
    bad("korrektur-unveraendert", "korrigierte-fehllesung", "recognition_value_mismatch", lambda es: es[3]["payload"].update(value=16))
    return traces, invalid


def export(root: Path) -> tuple[int, int]:
    traces, invalid = build_traces()
    for directory, rows in [("spuren", traces), ("ungueltig", invalid)]:
        target = root / directory
        target.mkdir(parents=True, exist_ok=True)
        for name, row in sorted(rows.items()):
            (target / (name + ".json")).write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return len(traces), len(invalid)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", required=True)
    parser.parse_args()
    print(export(Path(__file__).resolve().parents[2] / "vertraege" / "v1"))
