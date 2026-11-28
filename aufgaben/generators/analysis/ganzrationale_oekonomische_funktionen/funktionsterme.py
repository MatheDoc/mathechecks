"""Funktionsgleichungen ökonomischer Funktionen aufstellen (Polypol und Monopol gemischt).

Aus zwei gegebenen Funktionen (p, E, K, G) sind die beiden übrigen zu bestimmen.
Gerade Aufgabenindizes: Angebotspolypol (p konstant, E linear),
ungerade: Angebotsmonopol (p linear fallend, E quadratisch).
"""

import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _answers_for_e,
    _answers_for_e_quadratic,
    _answers_for_g,
    _answers_for_k,
    _answers_for_p,
    _answers_for_p_linear,
    _build_intro,
    _erlös_latex,
    _erlös_quadratic_latex,
    _has_max_sig_digits,
    _poly3_latex,
    _preis_latex,
    _preis_linear_latex,
    _sample_cost_coefficients,
    _sample_e2k3_parameters,
)
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.szenarien import (
    szenario_folge,
)
from aufgaben.generators.analysis.shared_numbers import uniform_sig

# Welche zwei Funktionen gegeben sind (Rest wird gesucht). Die Kombination (p, E)
# fehlt bewusst: daraus lassen sich K und G nicht bestimmen.
VARIANTEN: tuple[tuple[str, str], ...] = (
    ("E", "G"),
    ("K", "p"),
    ("p", "G"),
    ("E", "K"),
    ("K", "G"),
)

FRAGE_TEXT = {
    "p": "Bestimmen Sie die Preis-Absatz-Funktion.",
    "E": "Bestimmen Sie die Erlösfunktion.",
    "K": "Bestimmen Sie die Kostenfunktion.",
    "G": "Bestimmen Sie die Gewinnfunktion.",
}
REIHENFOLGE = ("p", "E", "K", "G")


def _polypol_funktionen(rng: random.Random) -> tuple[tuple, dict[str, str], dict[str, str]]:
    while True:
        k3, k2, k1, k0 = _sample_cost_coefficients(rng)
        price = uniform_sig(rng, 3.0, 60.0)
        g1 = round(price - k1, 10)
        if abs(g1) < 1e-9 or not _has_max_sig_digits(g1, max_digits=2):
            continue
        g3, g2, g0 = -k3, -k2, -k0
        terme = {
            "p": _preis_latex(price),
            "E": _erlös_latex(price),
            "K": _poly3_latex("K", k3, k2, k1, k0),
            "G": _poly3_latex("G", g3, g2, g1, g0),
        }
        antworten = {
            "p": _answers_for_p(price),
            "E": _answers_for_e(price),
            "K": _answers_for_k(k3, k2, k1, k0),
            "G": _answers_for_g(g3, g2, g1, g0),
        }
        return (k3, k2, k1, k0, price), terme, antworten


def _monopol_funktionen(rng: random.Random) -> tuple[tuple, dict[str, str], dict[str, str]]:
    a2, a1, k3, k2, k1, k0, *_ = _sample_e2k3_parameters(rng, for_graph=False)
    g3, g2, g1, g0 = -k3, a2 - k2, a1 - k1, -k0
    terme = {
        "p": _preis_linear_latex(a2, a1),
        "E": _erlös_quadratic_latex(a2, a1),
        "K": _poly3_latex("K", k3, k2, k1, k0),
        "G": _poly3_latex("G", g3, g2, g1, g0),
    }
    antworten = {
        "p": _answers_for_p_linear(a2, a1),
        "E": _answers_for_e_quadratic(a2, a1),
        "K": _answers_for_k(k3, k2, k1, k0),
        "G": _answers_for_g(g3, g2, g1, g0),
    }
    return (a2, a1, k3, k2, k1, k0), terme, antworten


class EconomicPolynomialFunctionTermsGenerator(TaskGenerator):
    """Erzeugt gemischte Aufgaben (Polypol/Monopol) zum Aufstellen von p, E, K, G."""

    generator_key = "analysis.ganzrationale_oekonomische_funktionen.funktionsterme"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        szenarien = szenario_folge(rng, count)
        tasks: list[Task] = []
        used_params: set[tuple] = set()

        while len(tasks) < count:
            index = len(tasks)
            marktform = "polypol" if index % 2 == 0 else "monopol"
            # Varianten je Marktform getrennt durchzählen, damit beide alle Varianten sehen.
            gegeben = VARIANTEN[(index // 2) % len(VARIANTEN)]

            if marktform == "polypol":
                params, terme, antworten = _polypol_funktionen(rng)
            else:
                params, terme, antworten = _monopol_funktionen(rng)

            key = (marktform, params, gegeben)
            if key in used_params:
                continue
            used_params.add(key)

            gesucht = [f for f in REIHENFOLGE if f not in gegeben]
            given = [terme[f] for f in REIHENFOLGE if f in gegeben]
            einleitung = _build_intro(given, satz=szenarien[index].satz(marktform))
            tasks.append(
                Task(
                    einleitung=einleitung,
                    fragen=[FRAGE_TEXT[f] for f in gesucht],
                    antworten=[antworten[f] for f in gesucht],
                )
            )

        return tasks
