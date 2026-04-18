"""Generator 02 – Graph → Gleichung (quadratisch).

1 Graph, Gleichung in SPF und FF; a ∈ {-2,-1,-0.5,0.5,1,2}.
Nur Funktionen mit zwei reellen Nullstellen (ganzzahlig).
"""

from __future__ import annotations

import math
import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.quadratische_funktionen.shared import (
    A_VALUES,
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

        while len(tasks) < count:
            a = rng.choice(A_VALUES)
            # Ganzzahlige Nullstellen wählen
            x1 = rng.randint(-6, 5)
            x2 = rng.randint(x1 + 1, 7)  # x2 > x1
            if abs(x1) > 7 or abs(x2) > 7:
                continue

            # Scheitel berechnen
            d_raw = (x1 + x2) / 2
            e_raw = -a * ((x2 - x1) / 2) ** 2
            # Scheitel muss im sichtbaren Bereich liegen
            if abs(d_raw) > 7 or abs(e_raw) > 7:
                continue

            # d und e auf halbe Ganzzahlen runden (für schöne Werte)
            d = d_raw
            e = e_raw

            key = (a, x1, x2)
            if key in used:
                continue
            used.add(key)

            # NF für Visual
            a_nf, b_nf, c_nf = spf_to_nf(a, d, e)

            # Sichtbereich um markante Punkte zentrieren
            all_x = [x1, x2, d]
            all_y = [0, 0, e]
            x_lo = min(all_x) - 2
            x_hi = max(all_x) + 2
            y_lo = min(all_y) - 2
            y_hi = max(all_y) + 2
            # Mindestgröße 8 Einheiten, auf ganze Zahlen runden
            x_center = (x_lo + x_hi) / 2
            y_center = (y_lo + y_hi) / 2
            x_span = max(x_hi - x_lo, 8)
            y_span = max(y_hi - y_lo, 8)
            x_lo = math.floor(x_center - x_span / 2)
            x_hi = math.ceil(x_center + x_span / 2)
            y_lo = math.floor(y_center - y_span / 2)
            y_hi = math.ceil(y_center + y_span / 2)

            visual = build_quadratic_visual(
                a_nf, b_nf, c_nf,
                title="Graph von f",
                x_range=(x_lo, x_hi),
            )
            visual["spec"]["layout"]["xaxis"] = {"range": [x_lo, x_hi], "dtick": 1}
            visual["spec"]["layout"]["yaxis"] = {"range": [y_lo, y_hi], "dtick": 1}

            # SPF und FF als je eine Gleichung abfragen
            tasks.append(Task(
                einleitung=(
                    "Bestimmen Sie die Gleichung der quadratischen Funktion "
                    "$ f $ in der Scheitelpunktform und in der faktorisierten Form."
                ),
                fragen=[
                    "Scheitelpunktform",
                    "Faktorisierte Form",
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
