"""Prüft alle Warm-Up-Datendateien unter _data/warmup/<gebiet>/<lernbereich>/<NN>-<sammlung>.yml.

Geprüft wird u. a.:
- check_id vorhanden und in _data/checks.json enthalten; Ordner und Dateiname passen zum Check
  (Lernbereich, zweistellige Nummer, Sammlung)
- keine Felder, die aus checks.json abgeleitet werden (titel, kompetenz, nummer, training_url, ...)
- bekannte Phasen, Bild- und Schritttypen
- auswahl: korrekt ist ein Index innerhalb der Optionen
- eingabe: jedes Feld hat eine numerische loesung
- zuordnen/markieren: Pflichtfelder vorhanden, markieren nur mit Matrix-Bild und gültigen Zeilen
- zeige: verweist nur auf vorhandene Punkt-/Eintrags-ids, Matrixzeilen/-spalten, Baumfelder 1–10
  bzw. Bereiche [a, b] und Werte mit 0 ≤ a ≤ b ≤ n (Histogramm, Zahlenstrahl)
- Modulseite lernbereiche/<gebiet>/<lernbereich>/warmup.md existiert
- kein "</script" in Texten (die Daten werden in <script type="application/json"> eingebettet)

Aufruf: python _data/warmup/validate_warmup.py
Exit-Code 0 = alles in Ordnung, 1 = Probleme gefunden.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKS_PATH = REPO_ROOT / "_data" / "checks.json"
WARMUP_ROOT = REPO_ROOT / "_data" / "warmup"
LERNBEREICHE_ROOT = REPO_ROOT / "lernbereiche"

TOP_LEVEL_KEYS = {"check_id", "abschluss", "karten"}
DERIVED_KEYS = {"titel", "kompetenz", "nummer", "training_url", "lernbereich_name"}
PHASES = {"orientierung", "vormachen", "mitmachen"}
STEP_TYPES = {"text", "aufdecken", "auswahl", "eingabe", "zuordnen", "markieren"}
VISUAL_TYPES = {"graph", "baum", "matrix", "liste", "histogramm", "zahlenstrahl"}
MATRIX_AREAS = {"A", "Ay"}
TREE_SLOTS = range(1, 11)


def is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_index(value, length: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value < length


def iter_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)


class Visual:
    """Was ein Bild über `zeige` ansprechen kann."""

    def __init__(self, spec, where: str, problems: list[str]):
        self.typ = None
        self.ids: set = set()
        self.rows = 0
        self.cols = 0
        self.n = 0
        if spec is None:
            return
        if not isinstance(spec, dict):
            problems.append(f"{where}: visual ist kein Objekt")
            return
        self.typ = spec.get("typ")
        if self.typ not in VISUAL_TYPES:
            problems.append(f"{where}: unbekannter visual.typ {self.typ!r}")
            return
        if self.typ == "graph":
            if not spec.get("funktionen"):
                problems.append(f"{where}: graph ohne funktionen")
            for i, punkt in enumerate(spec.get("punkte") or []):
                if not isinstance(punkt, dict) or "id" not in punkt:
                    problems.append(f"{where}: graph.punkte[{i}] ohne id")
                    continue
                if punkt["id"] in self.ids:
                    problems.append(f"{where}: graph.punkte: id {punkt['id']!r} doppelt")
                self.ids.add(punkt["id"])
                if not (is_number(punkt.get("x")) and is_number(punkt.get("y"))):
                    problems.append(f"{where}: graph.punkte[{i}] ({punkt['id']!r}) ohne numerische x/y")
        elif self.typ == "liste":
            for i, eintrag in enumerate(spec.get("eintraege") or []):
                if not isinstance(eintrag, dict) or "id" not in eintrag:
                    problems.append(f"{where}: liste.eintraege[{i}] ohne id")
                    continue
                if eintrag["id"] in self.ids:
                    problems.append(f"{where}: liste.eintraege: id {eintrag['id']!r} doppelt")
                self.ids.add(eintrag["id"])
        elif self.typ == "matrix":
            zeilen = spec.get("zeilen")
            if not isinstance(zeilen, list) or not zeilen or not all(isinstance(z, list) for z in zeilen):
                problems.append(f"{where}: matrix.zeilen fehlt oder ist keine Liste von Zeilen")
                return
            self.rows = len(zeilen)
            self.cols = len(zeilen[0])
            if any(len(z) != self.cols for z in zeilen):
                problems.append(f"{where}: matrix.zeilen haben unterschiedlich viele Spalten")
            trenn = spec.get("trenn")
            if trenn is not None and not is_index(trenn, self.cols):
                problems.append(f"{where}: matrix.trenn {trenn!r} außerhalb der Spalten")
        elif self.typ == "baum":
            for key in ("pa", "pba", "pbna"):
                if not is_number(spec.get(key)):
                    problems.append(f"{where}: baum.{key} fehlt oder ist keine Zahl")
            for slot in spec.get("gegeben") or []:
                if slot not in TREE_SLOTS:
                    problems.append(f"{where}: baum.gegeben enthält {slot!r} (erlaubt 1–10)")
        elif self.typ in ("histogramm", "zahlenstrahl"):
            n = spec.get("n")
            p = spec.get("p")
            if not (isinstance(n, int) and not isinstance(n, bool) and n > 0):
                problems.append(f"{where}: {self.typ}.n fehlt oder ist keine positive ganze Zahl")
                return
            self.n = n
            if self.typ == "histogramm" or p is not None:
                self.check_p(p, f"{where}: {self.typ}.p", problems)
            if self.typ == "histogramm":
                if "kumuliert" in spec and not isinstance(spec["kumuliert"], bool):
                    problems.append(f"{where}: histogramm.kumuliert muss true oder false sein")
                k_min = spec.get("kMin", 0)
                k_max = spec.get("kMax", n)
                if not (is_index(k_min, n + 1) and is_index(k_max, n + 1) and k_min < k_max):
                    problems.append(f"{where}: histogramm.kMin/kMax müssen ganze Zahlen mit 0 ≤ kMin < kMax ≤ n sein")
                self.check_ranges(spec.get("gegen"), f"{where}: histogramm.gegen", problems)
                self.check_ks(spec.get("werte"), f"{where}: histogramm.werte", problems)
            else:
                self.check_marke(spec.get("marke"), f"{where}: zahlenstrahl.marke", problems)
            self.check_ranges(spec.get("bereiche"), f"{where}: {self.typ}.bereiche", problems)

    @staticmethod
    def check_p(p, where: str, problems: list[str]) -> None:
        if not (is_number(p) and 0 < p < 1):
            problems.append(f"{where} fehlt oder liegt nicht zwischen 0 und 1")

    def check_marke(self, marke, where: str, problems: list[str]) -> None:
        if marke is not None and not (is_number(marke) and 0 <= marke <= self.n):
            problems.append(f"{where} {marke!r} liegt nicht zwischen 0 und {self.n}")

    def check_ks(self, ks, where: str, problems: list[str]) -> None:
        if ks is None:
            return
        if not isinstance(ks, list) or not all(is_index(k, self.n + 1) for k in ks):
            problems.append(f"{where} muss eine Liste ganzer Zahlen von 0 bis {self.n} sein")

    def check_ranges(self, ranges, where: str, problems: list[str]) -> None:
        if ranges is None:
            return
        if not isinstance(ranges, list):
            problems.append(f"{where} ist keine Liste von Bereichen [a, b]")
            return
        for rng in ranges:
            if not (isinstance(rng, list) and len(rng) == 2 and all(is_index(v, self.n + 1) for v in rng)
                    and rng[0] <= rng[1]):
                problems.append(f"{where} enthält {rng!r} (erwartet [a, b] mit 0 ≤ a ≤ b ≤ {self.n})")

    def check_zeige(self, zeige, where: str, problems: list[str]) -> None:
        if not isinstance(zeige, dict):
            problems.append(f"{where}: zeige ist kein Objekt")
            return
        if self.typ is None:
            problems.append(f"{where}: zeige ohne visual auf der Karte")
            return
        allowed = {
            "graph": {"punkte"},
            "liste": {"eintraege"},
            "matrix": {"zeilen", "spalten", "bereich"},
            "baum": {"slots"},
            "histogramm": {"bereiche", "gegen", "werte"},
            "zahlenstrahl": {"bereiche", "marke", "p"},
        }.get(self.typ, set())
        for key in zeige:
            if key not in allowed:
                problems.append(f"{where}: zeige.{key} passt nicht zu visual.typ {self.typ!r}")
        if self.typ in ("graph", "liste"):
            key = "punkte" if self.typ == "graph" else "eintraege"
            for ref in zeige.get(key) or []:
                if ref not in self.ids:
                    problems.append(f"{where}: zeige.{key} verweist auf unbekannte id {ref!r}")
        elif self.typ == "matrix":
            for ref in zeige.get("zeilen") or []:
                if not is_index(ref, self.rows):
                    problems.append(f"{where}: zeige.zeilen enthält {ref!r} (Matrix hat {self.rows} Zeilen)")
            for ref in zeige.get("spalten") or []:
                if not is_index(ref, self.cols):
                    problems.append(f"{where}: zeige.spalten enthält {ref!r} (Matrix hat {self.cols} Spalten)")
            if "bereich" in zeige and zeige["bereich"] not in MATRIX_AREAS:
                problems.append(f"{where}: zeige.bereich {zeige['bereich']!r} (erlaubt A, Ay)")
        elif self.typ == "baum":
            for ref in zeige.get("slots") or []:
                if ref not in TREE_SLOTS:
                    problems.append(f"{where}: zeige.slots enthält {ref!r} (erlaubt 1–10)")
        elif self.typ in ("histogramm", "zahlenstrahl"):
            for key in ("bereiche", "gegen"):
                if key not in zeige:
                    continue
                if zeige[key] is None:
                    problems.append(f"{where}: zeige.{key} ist leer, für „keine Markierung“ [] schreiben")
                else:
                    self.check_ranges(zeige[key], f"{where}: zeige.{key}", problems)
            if "werte" in zeige:
                self.check_ks(zeige["werte"], f"{where}: zeige.werte", problems)
            if "marke" in zeige:
                self.check_marke(zeige["marke"], f"{where}: zeige.marke", problems)
            if "p" in zeige:
                self.check_p(zeige["p"], f"{where}: zeige.p", problems)
            if not zeige:
                problems.append(f"{where}: zeige ist leer")


def validate_step(step, where: str, visual: Visual, problems: list[str]) -> None:
    if not isinstance(step, dict):
        problems.append(f"{where}: Schritt ist kein Objekt")
        return
    typ = step.get("typ")
    if typ not in STEP_TYPES:
        problems.append(f"{where}: unbekannter typ {typ!r}")
        return

    if typ == "text" and not step.get("text"):
        problems.append(f"{where}: text-Schritt ohne text")
    elif typ == "aufdecken" and not step.get("text"):
        problems.append(f"{where}: aufdecken ohne text")
    elif typ == "auswahl":
        optionen = step.get("optionen")
        if not isinstance(optionen, list) or len(optionen) < 2:
            problems.append(f"{where}: auswahl braucht mindestens zwei optionen")
        elif not is_index(step.get("korrekt"), len(optionen)):
            problems.append(
                f"{where}: korrekt {step.get('korrekt')!r} außerhalb der Optionen (0–{len(optionen) - 1})"
            )
    elif typ == "eingabe":
        felder = step.get("felder")
        if not isinstance(felder, list) or not felder:
            problems.append(f"{where}: eingabe ohne felder")
        else:
            for i, feld in enumerate(felder):
                if not isinstance(feld, dict):
                    problems.append(f"{where}: felder[{i}] ist kein Objekt")
                    continue
                if "loesung" not in feld:
                    problems.append(f"{where}: felder[{i}] ohne loesung")
                elif not is_number(feld["loesung"]):
                    problems.append(f"{where}: felder[{i}].loesung {feld['loesung']!r} ist keine Zahl")
                if "toleranz" in feld and not (is_number(feld["toleranz"]) and feld["toleranz"] >= 0):
                    problems.append(f"{where}: felder[{i}].toleranz ist keine nichtnegative Zahl")
                if "zeige" in feld:
                    visual.check_zeige(feld["zeige"], f"{where}.felder[{i}]", problems)
    elif typ == "zuordnen":
        paare = step.get("paare")
        if not isinstance(paare, list) or len(paare) < 2:
            problems.append(f"{where}: zuordnen braucht mindestens zwei paare")
        else:
            for i, paar in enumerate(paare):
                if not isinstance(paar, dict) or not paar.get("links") or not paar.get("rechts"):
                    problems.append(f"{where}: paare[{i}] ohne links/rechts")
    elif typ == "markieren":
        if visual.typ != "matrix":
            problems.append(f"{where}: markieren braucht visual.typ matrix")
        korrekt = step.get("korrekt")
        if not isinstance(korrekt, list):
            problems.append(f"{where}: markieren.korrekt ist keine Liste von Zeilen")
        elif visual.typ == "matrix":
            for ref in korrekt:
                if not is_index(ref, visual.rows):
                    problems.append(f"{where}: markieren.korrekt enthält {ref!r} (Matrix hat {visual.rows} Zeilen)")
        if step.get("bereich", "A") not in MATRIX_AREAS:
            problems.append(f"{where}: markieren.bereich {step.get('bereich')!r} (erlaubt A, Ay)")

    if "zeige" in step:
        visual.check_zeige(step["zeige"], where, problems)


def validate_file(path: Path, checks_by_id: dict) -> list[str]:
    problems: list[str] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        return [f"nicht lesbar/parsebar: {error}"]
    if not isinstance(data, dict):
        return ["Datei enthält kein Objekt"]

    for key in data:
        if key in DERIVED_KEYS:
            problems.append(f"Feld {key!r} wird aus checks.json abgeleitet und gehört nicht in die Datei")
        elif key not in TOP_LEVEL_KEYS:
            problems.append(f"unbekanntes Feld {key!r}")

    check_id = data.get("check_id")
    check = checks_by_id.get(check_id) if isinstance(check_id, str) else None
    if not check_id:
        problems.append("check_id fehlt")
    elif check is None:
        problems.append(f"check_id {check_id!r} fehlt in _data/checks.json")
    else:
        expected_dir = f"{check['Gebiet']}/{check['Lernbereich']}"
        expected_name = f"{int(check['Nummer']):02d}-{check['Sammlung']}.yml"
        actual_dir = path.parent.relative_to(WARMUP_ROOT).as_posix()
        if actual_dir != expected_dir or path.name != expected_name:
            problems.append(f"Pfad passt nicht zum Check, erwartet _data/warmup/{expected_dir}/{expected_name}")
        page = LERNBEREICHE_ROOT / check["Gebiet"] / check["Lernbereich"] / "warmup.md"
        if not page.is_file():
            problems.append(f"Modulseite fehlt: {page.relative_to(REPO_ROOT).as_posix()}")

    if not isinstance(data.get("abschluss"), str) or not data["abschluss"].strip():
        problems.append("abschluss fehlt oder ist leer")

    karten = data.get("karten")
    if not isinstance(karten, list) or not karten:
        problems.append("karten fehlt oder ist leer")
        karten = []

    for k, karte in enumerate(karten, start=1):
        where = f"Karte {k}"
        if not isinstance(karte, dict):
            problems.append(f"{where}: kein Objekt")
            continue
        if karte.get("phase") not in PHASES:
            problems.append(f"{where}: unbekannte phase {karte.get('phase')!r}")
        if not karte.get("titel"):
            problems.append(f"{where}: titel fehlt")
        visual = Visual(karte.get("visual"), where, problems)
        schritte = karte.get("schritte")
        if not isinstance(schritte, list) or not schritte:
            problems.append(f"{where}: schritte fehlt oder ist leer")
            continue
        for s, schritt in enumerate(schritte, start=1):
            validate_step(schritt, f"{where}, Schritt {s}", visual, problems)

    if any(re.search(r"</script", text, re.IGNORECASE) for text in iter_strings(data)):
        problems.append('Text enthält "</script" (bricht die Einbettung als JSON)')

    return problems


def main() -> int:
    checks = json.loads(CHECKS_PATH.read_text(encoding="utf-8"))
    checks_by_id = {c.get("check_id"): c for c in checks if isinstance(c, dict)}

    files = sorted(WARMUP_ROOT.glob("*/*/*.yml")) + sorted(WARMUP_ROOT.glob("*/*/*.yaml"))
    stray = sorted(WARMUP_ROOT.glob("*.y*ml")) + sorted(WARMUP_ROOT.glob("*/*.y*ml"))
    total_problems = 0

    for path in stray:
        print(f"FEHLER {path.relative_to(REPO_ROOT).as_posix()}: Datendatei gehört nach _data/warmup/<gebiet>/<lernbereich>/")
        total_problems += 1

    for path in files:
        rel = path.relative_to(REPO_ROOT).as_posix()
        problems = validate_file(path, checks_by_id)
        if problems:
            total_problems += len(problems)
            print(f"FEHLER {rel}")
            for problem in problems:
                print(f"  - {problem}")
        else:
            print(f"ok     {rel}")

    print()
    if total_problems:
        print(f"{len(files)} Warm-Up-Dateien geprüft, {total_problems} Problem(e).")
        return 1
    print(f"{len(files)} Warm-Up-Dateien geprüft, keine Probleme.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
