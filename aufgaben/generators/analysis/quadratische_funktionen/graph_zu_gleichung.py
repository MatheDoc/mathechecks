"""Generator 02 – Graph → Gleichung (quadratisch).

1 Graph, Gleichung in SPF und FF; a ∈ {-2,-1,-0.5,0.5,1,2}.
Nur Funktionen mit zwei reellen Nullstellen (ganzzahlig).
"""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.quadratische_funktionen.shared import (
    build_quadratic_visual,
    fmt,
    nf_to_ff,
    spf_to_nf,
)


class GraphZuGleichungQuadGenerator(TaskGenerator):
    generator_key = "analysis.quadratische_funktionen.graph_zu_gleichung_quad"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, int, int]] = set()

        a_pool = [-2, -1, -0.5, -0.25, 0.25, 0.5, 1, 2]

        while len(tasks) < count:
            a = rng.choice(a_pool)
            # Ganzzahlige Nullstellen mit gleicher Parität → d ganzzahlig
            x1 = rng.randint(-6, 5)
            x2 = rng.randint(x1 + 1, 7)  # x2 > x1
            if abs(x1) > 7 or abs(x2) > 7:
                continue
            if (x1 + x2) % 2 != 0:
                continue  # d wäre nicht ganzzahlig

            # Scheitel berechnen
            d = (x1 + x2) // 2
            e_raw = -a * ((x2 - x1) // 2) ** 2
            # e muss ganzzahlig sein (vom Graphen ablesbar)
            if e_raw != int(e_raw):
                continue
            e = int(e_raw)
            # Scheitel muss im sichtbaren Bereich liegen
            if abs(d) > 7 or abs(e) > 7:
                continue

            key = (a, x1, x2)
            if key in used:
                continue
            used.add(key)

            # NF für Visual
            a_nf, b_nf, c_nf = spf_to_nf(a, d, e)

            visual = build_quadratic_visual(
                a_nf, b_nf, c_nf,
                title="Graph von f",
            )

            # SPF und FF als je eine Gleichung abfragen
            tasks.append(Task(
                einleitung=(
                    "Bestimmen Sie die Gleichung der quadratischen Funktion "
                    "$ f $ in der angegebenen Form."
                ),
                fragen=[
                    "Scheitelpunktform:",
                    "Faktorisierte Form:",
                ],
                antworten=[
                    (
                        f"$ f(x) = ${numerical_analysis_calc(a)}"
                        f"$ (x - ${numerical_analysis_calc(d)}"
                        f"$)^2 + ${numerical_analysis_calc(e)}"
                    ),
                    (
                        f"$ f(x) = ${numerical_analysis_calc(a)}"
                        f"$ (x - ${numerical_analysis_calc(x1)}"
                        f"$)(x - ${numerical_analysis_calc(x2)}$)$"
                    ),
                ],
                visual=visual,
            ))

        return tasks
