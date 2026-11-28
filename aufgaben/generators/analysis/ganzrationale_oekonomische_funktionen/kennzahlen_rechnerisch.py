"""Kennzahlen ökonomischer Funktionen berechnen (Polypol und Monopol gemischt).

Gerade Aufgabenindizes: Angebotspolypol mit Kapazitätsgrenze,
ungerade: Angebotsmonopol. Je Aufgabe sechs Teilfragen
(Auswahl siehe ``_select_kennzahlen_items`` in ``shared.py``).
"""

import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _align_equations,
    _e2k3_kennzahlen_items,
    _erlös_latex,
    _erlös_quadratic_latex,
    _kennzahlen_items,
    _poly3_latex,
    _preis_latex,
    _preis_linear_latex,
    _sample_e2k3_parameters,
    _sample_kennzahlen_parameters,
    _select_kennzahlen_items,
)
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.szenarien import (
    szenario_folge,
)


def _polypol_task(rng: random.Random, used: set, satz: str, variante: int) -> Task | None:
    (
        k3,
        k2,
        k1,
        k0,
        price,
        x_break_even_low,
        x_break_even_high,
        x_gain_max,
        capacity,
    ) = _sample_kennzahlen_parameters(rng, for_graph=False)
    key = ("polypol", k3, k2, k1, k0, price, capacity)
    if key in used:
        return None
    used.add(key)

    gleichungen = _align_equations([
        _preis_latex(price),
        _erlös_latex(price),
        _poly3_latex("K", k3, k2, k1, k0),
        _poly3_latex("G", -k3, -k2, price - k1, -k0),
    ])
    einleitung = (
        f"{satz} Es gilt:{gleichungen}"
        f"Die Kapazitätsgrenze beträgt {capacity} Mengeneinheiten. "
        "Runden Sie auf zwei Nachkommastellen."
    )
    items = _kennzahlen_items(
        rng=rng,
        k3=k3,
        k2=k2,
        k1=k1,
        k0=k0,
        price=price,
        x_break_even_low=x_break_even_low,
        x_break_even_high=x_break_even_high,
        x_gain_max=x_gain_max,
        capacity=capacity,
    )
    auswahl = _select_kennzahlen_items(items, "polypol", variante)
    return Task(
        einleitung=einleitung,
        fragen=[frage for frage, _ in auswahl],
        antworten=[antwort for _, antwort in auswahl],
    )


def _monopol_task(rng: random.Random, used: set, satz: str, variante: int) -> Task | None:
    (
        a2,
        a1,
        k3,
        k2,
        k1,
        k0,
        x_break_even_low,
        x_break_even_high,
        x_gain_max,
    ) = _sample_e2k3_parameters(rng, for_graph=False)
    key = ("monopol", a2, a1, k3, k2, k1, k0)
    if key in used:
        return None
    used.add(key)

    gleichungen = _align_equations([
        _preis_linear_latex(a2, a1),
        _erlös_quadratic_latex(a2, a1),
        _poly3_latex("K", k3, k2, k1, k0),
        _poly3_latex("G", -k3, a2 - k2, a1 - k1, -k0),
    ])
    einleitung = f"{satz} Es gilt:{gleichungen}Runden Sie auf zwei Nachkommastellen."
    items = _e2k3_kennzahlen_items(
        rng=rng,
        a2=a2,
        a1=a1,
        k3=k3,
        k2=k2,
        k1=k1,
        k0=k0,
        x_break_even_low=x_break_even_low,
        x_break_even_high=x_break_even_high,
        x_gain_max=x_gain_max,
    )
    auswahl = _select_kennzahlen_items(items, "monopol", variante)
    return Task(
        einleitung=einleitung,
        fragen=[frage for frage, _ in auswahl],
        antworten=[antwort for _, antwort in auswahl],
    )


class EconomicPolynomialKennzahlenRechnerischGenerator(TaskGenerator):
    """Erzeugt gemischte Kennzahlen-Aufgaben (rechnerisch) für Polypol und Monopol."""

    generator_key = "analysis.ganzrationale_oekonomische_funktionen.kennzahlen_rechnerisch"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        szenarien = szenario_folge(rng, count)
        tasks: list[Task] = []
        used: set = set()

        while len(tasks) < count:
            index = len(tasks)
            variante = index // 2
            if index % 2 == 0:
                task = _polypol_task(rng, used, szenarien[index].polypol, variante)
            else:
                task = _monopol_task(rng, used, szenarien[index].monopol, variante)
            if task is not None:
                tasks.append(task)

        return tasks
