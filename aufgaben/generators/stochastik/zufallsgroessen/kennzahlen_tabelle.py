"""Kennzahlen diskreter Zufallsgrö�Yen aus Wahrscheinlichkeitstabelle �?" 4 Varianten.

Jede Aufgabe zeigt eine 5-elementige Wahrscheinlichkeitsverteilung als visual-Tabelle
(spec.type = "wkt-tabelle"). None-Einträge in x bzw. p markieren fehlende Zellen.

Varianten (je ein Generator, je eine Sammlung):
    1. KennzahlenTabelleFehlWsk        �?" eine P_i und eine x_i fehlen, E(X) gegeben
    2. KennzahlenTabelleEW             �?" volle Tabelle, E(X) berechnen
    3. KennzahlenTabelleSigma          �?" volle Tabelle + E(X) gegeben, �f(X) berechnen
    4. KennzahlenTabelleFehlWsk2       �?" zwei P_i fehlen, E(X) gegeben, beide bestimmen
"""

from __future__ import annotations

import random
from math import sqrt

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator


# �"?�"? Hilfsfunktionen �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?

def _fmt(value: float, dec: int) -> str:
    """Zahl mit deutschem Dezimalkomma formatieren."""
    if dec == 0:
        return str(int(round(value)))
    return f"{value:.{dec}f}".replace(".", ",")


def _wkt_visual(x_disp: list[int | None], p_disp: list[float | None]) -> dict:
    """visual-Spec für eine Wahrscheinlichkeitstabelle. None �?' leere Zelle."""
    return {
        "type": "plot",
        "spec": {
            "type": "wkt-tabelle",
            "x": x_disp,
            "p": p_disp,
        },
    }


_EINLEITUNG = "Die Tabelle zeigt die Wahrscheinlichkeitsverteilung einer Zufallsgrö�Ye \\( X \\)."


def _gen_data(rng: random.Random) -> tuple[list[int], list[float], float, float]:
    """Erzeugt (x, p, E(X), �f(X)) mit Σ p_i = 1,00 (auf 2 NKS).

    x-Werte: ganzzahlig, streng aufsteigend (Schritte 1�?"3).
    P-Werte: auf 2 NKS gerundet, Summe = 1,00 (exakt).
    E(X): auf 4 NKS gerundet.
    �f(X): auf 4 NKS gerundet.
    """
    x = [rng.randint(-5, -2)]
    for _ in range(4):
        x.append(x[-1] + rng.randint(1, 3))

    while True:
        h = [rng.randint(1, 99) for _ in range(5)]
        s = sum(h)
        p = [round(hi / s, 2) for hi in h]
        if round(sum(p), 2) == 1.0:
            break

    ex = round(sum(xi * pi for xi, pi in zip(x, p)), 4)
    var = sum((xi - ex) ** 2 * pi for xi, pi in zip(x, p))
    sx = round(sqrt(var), 4)
    return x, p, ex, sx


# �"?�"? Variante 1: Fehlende Wahrscheinlichkeit + fehlender x-Wert �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?

class KennzahlenTabelleFehlWskGenerator(TaskGenerator):
    """Eine Wahrscheinlichkeit und ein x-Wert fehlen, E(X) ist gegeben."""

    generator_key = "stochastik.zufallsgroessen.kennzahlen_tabelle_fehlende_wsk"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        for _ in range(count):
            x, p, ex, _sx = _gen_data(rng)
            idx_p = rng.randint(0, 4)
            idx_x = (idx_p + rng.randint(1, 4)) % 5
            x_disp: list[int | None] = [xi if i != idx_x else None for i, xi in enumerate(x)]
            p_disp: list[float | None] = [round(pi, 2) if i != idx_p else None for i, pi in enumerate(p)]
            frage = (
                "Bestimmen Sie den fehlenden Wert der Zufallsgrö�Ye und die fehlende Wahrscheinlichkeit."
                f" Es ist bekannt, dass \\( E(X) = {_fmt(ex, 4)} \\)."
            )
            antwort = (
                f"\\( x_i= \\) {numerical(float(x[idx_x]), tolerance=0.5, decimals=0)}"
                f" und \\( P(X={x[idx_p]})= \\) {numerical_stochastik_calc(p[idx_p])}"
            )
            tasks.append(Task(
                einleitung=_EINLEITUNG,
                fragen=[frage],
                antworten=[antwort],
                visual=_wkt_visual(x_disp, p_disp),
            ))
        return tasks


# �"?�"? Variante 2: Erwartungswert �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?

class KennzahlenTabelleEWGenerator(TaskGenerator):
    """Volle Tabelle gegeben �?" E(X) berechnen."""

    generator_key = "stochastik.zufallsgroessen.kennzahlen_tabelle_ew"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        for _ in range(count):
            x, p, ex, _sx = _gen_data(rng)
            p_disp: list[float | None] = [round(pi, 2) for pi in p]
            frage = "Bestimmen Sie den Erwartungswert."
            antwort = "\\( E(X)= \\) " + numerical_stochastik_calc(ex)
            tasks.append(Task(
                einleitung=_EINLEITUNG,
                fragen=[frage],
                antworten=[antwort],
                visual=_wkt_visual(list(x), p_disp),
            ))
        return tasks


# �"?�"? Variante 3: Standardabweichung �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?

class KennzahlenTabelleSigmaGenerator(TaskGenerator):
    """Volle Tabelle + E(X) gegeben �?" �f(X) berechnen (auf 4 NKS)."""

    generator_key = "stochastik.zufallsgroessen.kennzahlen_tabelle_sigma"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        for _ in range(count):
            x, p, ex, sx = _gen_data(rng)
            p_disp: list[float | None] = [round(pi, 2) for pi in p]
            frage = (
                "Bestimmen Sie die Standardabweichung (auf 4 Dezimalstellen gerundet)."
                f" Es ist bekannt, dass \\( E(X) = {_fmt(ex, 4)} \\)."
            )
            antwort = "\\( \\sigma(X)= \\) " + numerical_stochastik_calc(sx)
            tasks.append(Task(
                einleitung=_EINLEITUNG,
                fragen=[frage],
                antworten=[antwort],
                visual=_wkt_visual(list(x), p_disp),
            ))
        return tasks


# �"?�"? Variante 4: Zwei fehlende Wahrscheinlichkeiten �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?

class KennzahlenTabelleFehlWsk2Generator(TaskGenerator):
    """Zwei Wahrscheinlichkeiten fehlen, E(X) gegeben �?" beide P_i bestimmen."""

    generator_key = "stochastik.zufallsgroessen.kennzahlen_tabelle_fehlende_wsk_zwei"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        for _ in range(count):
            x, p, ex, _sx = _gen_data(rng)
            idx1 = rng.randint(0, 4)
            idx2 = (idx1 + rng.randint(1, 4)) % 5
            hidden = {idx1, idx2}
            p_disp: list[float | None] = [round(pi, 2) if i not in hidden else None for i, pi in enumerate(p)]
            frage = (
                "Bestimmen Sie die fehlenden Wahrscheinlichkeiten."
                f" Es ist bekannt, dass \\( E(X) = {_fmt(ex, 4)} \\)."
            )
            num1 = numerical_stochastik_calc(p[idx1])
            num2 = numerical_stochastik_calc(p[idx2])
            antwort = (
                f"\\( P(X={x[idx1]})= \\) {num1}"
                f" und \\( P(X={x[idx2]})= \\) {num2}"
            )
            tasks.append(Task(
                einleitung=_EINLEITUNG,
                fragen=[frage],
                antworten=[antwort],
                visual=_wkt_visual(list(x), p_disp),
            ))
        return tasks

