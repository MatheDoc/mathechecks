"""Generator 07 – Funktionswerte und Umkehrwerte (quadratisch).

Funktionswert: x₀ einsetzen → f(x₀) berechnen.
Umkehrwert: f(x) = y₀ → quadratische Gleichung mit p-q-Formel lösen (zwei Lösungen).
"""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.quadratische_funktionen.shared import (
    display_eq,
    fmt,
    nf_latex,
    sample_nf_nice,
)


class FunktionswerteUmkehrwerteQuadGenerator(TaskGenerator):
    """Funktionswert f(x₀) und Umkehrwert f(x) = y₀ für quadratische Funktionen."""

    generator_key = "analysis.quadratische_funktionen.funktionswerte_umkehrwerte_quad"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, float, float, int, int]] = set()

        while len(tasks) < count:
            a, b, c, ns1, ns2 = sample_nf_nice(rng)

            # x₀ für Funktionswert
            x0 = rng.randint(-5, 5)
            y0_fw = a * x0**2 + b * x0 + c

            # x_inv für Umkehrwert – zweite Lösung über Symmetrie
            x_inv = rng.randint(-6, 6)
            y0_inv = a * x_inv**2 + b * x_inv + c
            # Zweite Lösung: symmetrisch zur Achse d = (ns1+ns2)/2
            x_inv2 = int(ns1 + ns2) - x_inv

            # Trivialfälle vermeiden
            if y0_inv == 0:  # wäre Nullstellenaufgabe
                continue
            if x_inv == x_inv2:  # doppelte Lösung am Scheitel
                continue
            if x0 == x_inv and x0 == x_inv2:
                continue
            if abs(y0_fw) > 50 or abs(y0_inv) > 50:
                continue

            key = (a, b, c, x0, x_inv)
            if key in used:
                continue
            used.add(key)

            eq = nf_latex(a, b, c)
            x_sol_min = min(x_inv, x_inv2)
            x_sol_max = max(x_inv, x_inv2)

            tasks.append(Task(
                einleitung=f"Gegeben:{display_eq(eq)}",
                fragen=[
                    f"Berechnen Sie $ f({fmt(x0)}) $.",
                    f"Berechnen Sie alle $ x $ mit $ f(x) = {fmt(y0_inv)} $.",
                ],
                antworten=[
                    f"$ f({fmt(x0)}) = ${numerical_analysis_calc(y0_fw)}",
                    (
                        f"$ x_1 = ${numerical_analysis_calc(x_sol_min)}"
                        f"\n$ x_2 = ${numerical_analysis_calc(x_sol_max)}"
                    ),
                ],
            ))

        return tasks
