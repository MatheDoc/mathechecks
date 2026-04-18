"""Generator 09 – Gleichung aufstellen (quadratisch).

Varianten: Scheitel+Punkt, 2 NS+Punkt, 3 Punkte.
Ganzzahlige a, b, c. Kein Matrixverfahren nötig.
"""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.quadratische_funktionen.shared import (
    A_VALUES_INT,
    display_eq,
    fmt,
    nf_latex,
)


class GleichungAufstellenQuadGenerator(TaskGenerator):
    generator_key = "analysis.quadratische_funktionen.gleichung_aufstellen_quad"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        variants = ["scheitel_punkt", "zwei_ns_punkt", "drei_punkte"]

        while len(tasks) < count:
            variant = rng.choice(variants)
            if variant == "scheitel_punkt":
                task = self._scheitel_punkt(rng)
            elif variant == "zwei_ns_punkt":
                task = self._zwei_ns_punkt(rng)
            else:
                task = self._drei_punkte(rng)
            if task is not None:
                tasks.append(task)

        return tasks

    def _scheitel_punkt(self, rng: random.Random) -> Task:
        """Scheitel S(d|e) und ein weiterer Punkt gegeben → NF."""
        a = rng.choice(A_VALUES_INT)
        d = rng.randint(-4, 4)
        e = rng.randint(-6, 6)

        # Weiterer Punkt: x ≠ d
        px = d + rng.choice([-3, -2, -1, 1, 2, 3])
        py = a * (px - d) ** 2 + e

        # NF berechnen
        b_nf = -2 * a * d
        c_nf = a * d**2 + e

        return Task(
            einleitung=(
                f"Die Parabel $ f $ hat den Scheitel $ S({fmt(d)} \\mid {fmt(e)}) $ "
                f"und geht durch den Punkt $ P({fmt(px)} \\mid {fmt(py)}) $.\n\n"
                f"Bestimmen Sie die Gleichung in Normalform $ f(x)=ax^2+bx+c $."
            ),
            fragen=["Normalform"],
            antworten=[
                f"$ f(x)= ${numerical_analysis_calc(a)}$ x^2+ ${numerical_analysis_calc(b_nf)}$ x+ ${numerical_analysis_calc(c_nf)}",
            ],
        )

    def _zwei_ns_punkt(self, rng: random.Random) -> Task:
        """2 Nullstellen und ein weiterer Punkt → NF."""
        x1 = rng.randint(-5, 5)
        x2 = rng.randint(-5, 5)
        while x1 == x2:
            x2 = rng.randint(-5, 5)

        # Weiterer Punkt: weder x1 noch x2
        px = rng.randint(-6, 6)
        while px == x1 or px == x2:
            px = rng.randint(-6, 6)

        # a so bestimmen, dass ganzzahlig
        denom = (px - x1) * (px - x2)
        if denom == 0:
            return None
        # py = a · (px-x1)(px-x2) → wähle a ganzzahlig
        a = rng.choice(A_VALUES_INT)
        py = a * denom

        b = -a * (x1 + x2)
        c = a * x1 * x2

        x_lo, x_hi = sorted([x1, x2])

        return Task(
            einleitung=(
                f"Die Parabel $ f $ hat die Nullstellen "
                f"$ x_1 = {fmt(x_lo)} $ und $ x_2 = {fmt(x_hi)} $ "
                f"und geht durch den Punkt $ P({fmt(px)} \\mid {fmt(py)}) $.\n\n"
                f"Bestimmen Sie die Gleichung in Normalform $ f(x)=ax^2+bx+c $."
            ),
            fragen=["Normalform"],
            antworten=[
                f"$ f(x)= ${numerical_analysis_calc(float(a))}$ x^2+ ${numerical_analysis_calc(float(b))}$ x+ ${numerical_analysis_calc(float(c))}",
            ],
        )

    def _drei_punkte(self, rng: random.Random) -> Task | None:
        """3 Punkte → NF. Einfache ganzzahlige Koeffizienten."""
        a = rng.choice(A_VALUES_INT)
        b = rng.randint(-4, 4)
        c = rng.randint(-6, 6)

        # 3 verschiedene x-Werte (klein)
        x_vals = rng.sample(range(-4, 5), 3)
        x_vals.sort()
        points = [(x, a * x**2 + b * x + c) for x in x_vals]

        # Prüfe ob y-Werte nicht zu groß
        if any(abs(y) > 40 for _, y in points):
            return None

        p1, p2, p3 = points

        return Task(
            einleitung=(
                f"Die Parabel $ f $ geht durch die Punkte "
                f"$ A({fmt(p1[0])} \\mid {fmt(p1[1])}) $, "
                f"$ B({fmt(p2[0])} \\mid {fmt(p2[1])}) $ und "
                f"$ C({fmt(p3[0])} \\mid {fmt(p3[1])}) $.\n\n"
                f"Bestimmen Sie die Gleichung in Normalform $ f(x)=ax^2+bx+c $."
            ),
            fragen=["Normalform"],
            antworten=[
                f"$ f(x)= ${numerical_analysis_calc(float(a))}$ x^2+ ${numerical_analysis_calc(float(b))}$ x+ ${numerical_analysis_calc(float(c))}",
            ],
        )
