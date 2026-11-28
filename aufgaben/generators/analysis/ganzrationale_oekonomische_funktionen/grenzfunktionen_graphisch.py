"""Kennzahlen aus den Graphen der Grenzfunktionen ablesen (Polypol und Monopol gemischt).

Drei Aufgabenarten im Wechsel:
- Angebotspolypol: Diagramm mit E' (= p konstant) und K'
- Angebotsmonopol: Diagramm mit E'(x) = 2·a2·x + a1 und K'
- nur G' (Marktform abwechselnd): Nullstelle = Gewinnmaximum,
  Hochpunkt = stärkster Gewinnanstieg (Wendestelle von G), Vorzeichen von G'.

Teilfragen der E'/K'-Aufgaben (je fünf):
- beide: Übergang degressiv/progressiv (Tiefpunkt von K'), minimale Grenzkosten,
  gewinnmaximale Menge (Schnitt von E' und K'), Grenzgewinn E'(x0) − K'(x0)
- Polypol: Marktpreis (Wert von E')
- Monopol: erlösmaximale Menge (Nullstelle von E')
"""

from __future__ import annotations

import math
import random

from aufgaben.core.models import Task
from aufgaben.core.tolerances import graph_read_tolerance_from_span
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.kennzahlen_graphisch_e1k3 import (
    _sample_template_scaled_parameters as _sample_polypol,
)
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.kennzahlen_graphisch_e2k3 import (
    _sample_template_scaled_parameters as _sample_monopol,
)
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _format_number,
    _num_tol,
)
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.szenarien import (
    szenario_folge,
)

# Farben wie in den übrigen Trainingsdiagrammen (economic-curves): E grün, K rot, G blau
FARBE_E = "#2ca02c"
FARBE_K = "#d62728"


def _js(value: float) -> str:
    """Zahl für math.js-Terme ohne Exponentialschreibweise."""
    text = f"{value:.10f}".rstrip("0").rstrip(".")
    return text if text not in ("", "-0") else "0"


def _nice(value: float) -> float:
    if value == 0:
        return 0.0
    exponent = math.floor(math.log10(abs(value)))
    factor = 10 ** (1 - exponent)
    return round(value * factor) / factor


def _kurve(term: str, name: str, beschreibung: str, farbe: str) -> dict:
    return {
        "term": term, "variable": "x", "mode": "lines", "name": name,
        "description": beschreibung, "line": {"color": farbe, "width": 2.5},
    }


def _k_strich_term(k3: float, k2: float, k1: float) -> str:
    return f"{_js(3 * k3)}*x^2+{_js(2 * k2)}*x+{_js(k1)}".replace("+-", "-")


def _grenzgewinn_stelle(rng: random.Random, x_gmax: float, x_ende: float) -> float:
    for _ in range(50):
        if rng.random() < 0.5:
            x0 = _nice(x_gmax * rng.uniform(0.35, 0.7))
        else:
            x0 = _nice(x_gmax * rng.uniform(1.15, 1.4))
        if 0 < x0 < 0.95 * x_ende and abs(x0 - x_gmax) > 0.1 * x_gmax:
            return x0
    return _nice(x_gmax * 0.5)


def _polypol_task(rng: random.Random, used: set, satz: str) -> Task:
    ks = None
    for _ in range(5000):
        k3, k2, k1, k0, price, _x_gs, _x_gg, x_gmax, capacity = _sample_polypol(rng)
        key = ("polypol", k3, k2, k1, k0, price)
        ks = lambda x, k3=k3, k2=k2, k1=k1: (3 * k3 * x + 2 * k2) * x + k1
        k_min = ks(-k2 / (3 * k3))
        # Ablesbare Größenordnung und deutlich getrennte Kennzahlen im Grenzdiagramm
        if key in used or not 5.0 <= price <= 80.0:
            continue
        if not 0.15 * max(price, k1) <= k_min <= 0.8 * price:
            continue
        used.add(key)
        break
    else:
        raise ValueError("Keine geeigneten Polypol-Parameter für das Grenzdiagramm gefunden.")
    x_w = -k2 / (3 * k3)
    x_ende = float(capacity)
    y_max = max(price, k1) * 1.3
    x_tol = graph_read_tolerance_from_span(x_ende)
    y_tol = graph_read_tolerance_from_span(y_max)
    x0 = _grenzgewinn_stelle(rng, x_gmax, x_ende)

    items = [
        ("Bestimmen Sie die Menge beim Übergang vom degressiven zum progressiven Kostenwachstum.",
         _num_tol(x_w, 2 * x_tol)),
        ("Bestimmen Sie die minimalen Grenzkosten.", _num_tol(ks(x_w), y_tol)),
        ("Bestimmen Sie die gewinnmaximale Menge.", _num_tol(x_gmax, x_tol)),
        ("Bestimmen Sie den Marktpreis.", _num_tol(price, y_tol)),
        (f"Bestimmen Sie den Grenzgewinn bei einer Absatzmenge von {_format_number(x0)} ME.",
         _num_tol(price - ks(x0), 2 * y_tol)),
    ]
    curves = [
        _kurve(_js(price), "E'(x)", "Grenzerlösfunktion", FARBE_E),
        _kurve(_k_strich_term(k3, k2, k1), "K'(x)", "Grenzkostenfunktion", FARBE_K),
    ]
    einleitung = (
        f"{satz} Das Diagramm zeigt die Graphen der Grenzerlösfunktion $E'$ und der "
        "Grenzkostenfunktion $K'$. Lesen Sie die Werte so genau wie möglich ab."
    )
    return _task(einleitung, items, curves, x_ende, 0.0, y_max)


def _monopol_task(rng: random.Random, used: set, satz: str) -> Task:
    for _ in range(5000):
        a2, a1, k3, k2, k1, k0, _x_gs, _x_gg, x_gmax = _sample_monopol(rng)
        key = ("monopol", a2, a1, k3, k2, k1, k0)
        ks = lambda x, k3=k3, k2=k2, k1=k1: (3 * k3 * x + 2 * k2) * x + k1
        k_min = ks(-k2 / (3 * k3))
        sm_probe = -a1 / a2
        if key in used or not 10.0 <= a1 <= 150.0:
            continue
        if k_min < 0.12 * a1 or abs(x_gmax - sm_probe / 2) < 0.08 * sm_probe:
            continue
        used.add(key)
        break
    else:
        raise ValueError("Keine geeigneten Monopol-Parameter für das Grenzdiagramm gefunden.")
    es = lambda x: 2 * a2 * x + a1
    x_w = -k2 / (3 * k3)
    sm = -a1 / a2
    x_emax = sm / 2
    x_ende = sm
    y_max = max(a1, k1) * 1.15
    y_min = -0.4 * a1
    x_tol = graph_read_tolerance_from_span(x_ende)
    y_tol = graph_read_tolerance_from_span(y_max - y_min)
    x0 = _grenzgewinn_stelle(rng, x_gmax, x_ende)

    items = [
        ("Bestimmen Sie die Menge beim Übergang vom degressiven zum progressiven Kostenwachstum.",
         _num_tol(x_w, 2 * x_tol)),
        ("Bestimmen Sie die minimalen Grenzkosten.", _num_tol(ks(x_w), y_tol)),
        ("Bestimmen Sie die gewinnmaximale Menge.", _num_tol(x_gmax, x_tol)),
        ("Bestimmen Sie die erlösmaximale Menge.", _num_tol(x_emax, x_tol)),
        (f"Bestimmen Sie den Grenzgewinn bei einer Absatzmenge von {_format_number(x0)} ME.",
         _num_tol(es(x0) - ks(x0), 2 * y_tol)),
    ]
    curves = [
        _kurve(f"{_js(2 * a2)}*x+{_js(a1)}".replace("+-", "-"), "E'(x)", "Grenzerlösfunktion", FARBE_E),
        _kurve(_k_strich_term(k3, k2, k1), "K'(x)", "Grenzkostenfunktion", FARBE_K),
    ]
    einleitung = (
        f"{satz} Das Diagramm zeigt die Graphen der Grenzerlösfunktion $E'$ und der "
        "Grenzkostenfunktion $K'$. Lesen Sie die Werte so genau wie möglich ab."
    )
    return _task(einleitung, items, curves, x_ende, y_min, y_max)


FARBE_G = "#1f77b4"


def _mc(rng: random.Random, richtig: str, falsch: list[str]) -> str:
    optionen = [f"={richtig}"] + list(falsch)
    rng.shuffle(optionen)
    return "{1:MC:~" + "~".join(optionen) + "}"


def _grenzgewinn_task(rng: random.Random, used: set, szenario, marktform: str) -> Task:
    """Nur G' gegeben: Nullstelle (Gewinnmaximum), Hochpunkt (stärkster Gewinnanstieg), Vorzeichen."""
    for _ in range(5000):
        if marktform == "polypol":
            k3, k2, k1, k0, price, _x_gs, _x_gg, x_gmax, capacity = _sample_polypol(rng)
            e2, e1, x_ende = 0.0, price, float(capacity)
            key = ("gs-polypol", k3, k2, k1, k0, price)
            if not 5.0 <= price <= 80.0:
                continue
        else:
            a2, a1, k3, k2, k1, k0, _x_gs, _x_gg, x_gmax = _sample_monopol(rng)
            e2, e1, x_ende = a2, a1, -a1 / a2
            key = ("gs-monopol", a2, a1, k3, k2, k1, k0)
            if not 10.0 <= a1 <= 150.0:
                continue
        if key in used:
            continue
        # G'(x) = −3·k3·x² + 2·(e2 − k2)·x + (e1 − k1)
        c2, c1, c0 = -3 * k3, 2 * (e2 - k2), e1 - k1
        gs = lambda x, c2=c2, c1=c1, c0=c0: (c2 * x + c1) * x + c0
        x_h = (e2 - k2) / (3 * k3)
        gs_max = gs(x_h)
        # Hochpunkt deutlich im Inneren und vor dem Gewinnmaximum, ablesbare Größenordnung
        if not (0.15 * x_gmax < x_h < 0.8 * x_gmax) or not 3.0 <= gs_max <= 150.0:
            continue
        used.add(key)
        break
    else:
        raise ValueError("Keine geeigneten Parameter für die Grenzgewinn-Aufgabe gefunden.")

    y_max = 1.25 * gs_max
    y_min = 1.05 * max(min(gs(0.0), gs(x_ende)), -1.2 * gs_max)
    x_tol = graph_read_tolerance_from_span(x_ende)
    y_tol = graph_read_tolerance_from_span(y_max - y_min)
    vorher = rng.random() < 0.5
    x0 = _nice(x_gmax * (rng.uniform(0.35, 0.7) if vorher else rng.uniform(1.15, 1.35)))
    x1 = _nice(x_gmax * (rng.uniform(1.15, 1.35) if vorher else rng.uniform(0.35, 0.7)))
    x0 = min(x0, 0.95 * x_ende)
    x1 = min(x1, 0.95 * x_ende)
    steigt = gs(x1) > 0

    items = [
        ("Bestimmen Sie die gewinnmaximale Menge.", _num_tol(x_gmax, x_tol)),
        ("Bestimmen Sie die Menge, bei der der Gewinn am stärksten steigt.", _num_tol(x_h, 2 * x_tol)),
        ("Bestimmen Sie den maximalen Grenzgewinn.", _num_tol(gs_max, y_tol)),
        (f"Bestimmen Sie den Grenzgewinn bei einer Absatzmenge von {_format_number(x0)} ME.",
         _num_tol(gs(x0), y_tol)),
        (f"Geben Sie an, wie sich der Gewinn bei einer Absatzmenge von {_format_number(x1)} ME verändert.",
         _mc(rng, "Der Gewinn steigt." if steigt else "Der Gewinn fällt.", [
             "Der Gewinn fällt." if steigt else "Der Gewinn steigt.",
             "Der Gewinn ist dort maximal.",
         ])),
    ]
    term = f"{_js(c2)}*x^2+{_js(c1)}*x+{_js(c0)}".replace("+-", "-")
    curves = [_kurve(term, "G'(x)", "Grenzgewinnfunktion", FARBE_G)]
    einleitung = (
        f"{szenario.satz(marktform)} Das Diagramm zeigt den Graphen der Grenzgewinnfunktion $G'$. "
        "Lesen Sie die Werte so genau wie möglich ab."
    )
    return _task(einleitung, items, curves, x_ende, y_min, y_max, titel="Grenzgewinn")


def _task(einleitung, items, curves, x_ende, y_min, y_max, titel="Grenzerlös und Grenzkosten") -> Task:
    visual = {
        "type": "plot",
        "spec": {
            "type": "expression-curves",
            "title": titel,
            "curves": curves,
            "points": 301,
            "layout": {
                "title": titel,
                "xaxis": {"title": "Menge x in ME", "range": [0.0, x_ende * 1.04],
                          "zeroline": True, "showline": True},
                "yaxis": {"title": "GE/ME", "range": [y_min, y_max], "zeroline": True, "showline": True},
            },
            "funktionen": [
                {"name": c["name"], "term": c["term"], "beschreibung": c["description"]} for c in curves
            ],
        },
    }
    return Task(
        einleitung=einleitung,
        fragen=[f for f, _ in items],
        antworten=[a for _, a in items],
        visual=visual,
    )


class EconomicPolynomialGrenzfunktionenGraphischGenerator(TaskGenerator):
    """Erzeugt gemischte Aufgaben zum Ablesen an Grenzerlös- und Grenzkostenfunktion."""

    generator_key = "analysis.ganzrationale_oekonomische_funktionen.grenzfunktionen_graphisch"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        szenarien = szenario_folge(rng, count)
        used: set = set()
        tasks: list[Task] = []
        for index in range(count):
            art = index % 3
            if art == 0:
                tasks.append(_polypol_task(rng, used, szenarien[index].polypol))
            elif art == 1:
                tasks.append(_monopol_task(rng, used, szenarien[index].monopol))
            else:
                marktform = "polypol" if (index // 3) % 2 == 0 else "monopol"
                tasks.append(_grenzgewinn_task(rng, used, szenarien[index], marktform))
        return tasks
