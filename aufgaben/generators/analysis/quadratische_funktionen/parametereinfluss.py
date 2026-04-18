"""Generator 12 – Parametereinfluss (quadratisch).

SPF gegeben: Scheitel? Öffnung? Streckung?
"""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc, mc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.quadratische_funktionen.shared import (
    A_VALUES,
    display_eq,
    fmt,
    spf_latex,
)


class ParametereinflussQuadGenerator(TaskGenerator):
    generator_key = "analysis.quadratische_funktionen.parametereinfluss_quad"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, float, float]] = set()

        while len(tasks) < count:
            a = rng.choice(A_VALUES)
            d = rng.randint(-5, 5)
            e = rng.randint(-6, 6)
            key = (a, float(d), float(e))
            if key in used:
                continue
            used.add(key)

            eq = spf_latex(a, float(d), float(e))

            oeffnung_options = ["nach oben", "nach unten"]
            oeffnung_idx = 0 if a > 0 else 1

            streckung_options = ["gestaucht", "normal ($ |a|=1 $)", "gestreckt"]
            abs_a = abs(a)
            if abs_a < 1:
                streckung_idx = 0
            elif abs_a == 1:
                streckung_idx = 1
            else:
                streckung_idx = 2

            tasks.append(Task(
                einleitung=f"Gegeben:{display_eq(eq)}",
                fragen=[
                    "Scheitel: $ x_S = $",
                    "Scheitel: $ y_S = $",
                    "Öffnungsrichtung?",
                    "Streckung/Stauchung?",
                ],
                antworten=[
                    numerical_analysis_calc(d),
                    numerical_analysis_calc(e),
                    mc(oeffnung_options, oeffnung_idx),
                    mc(streckung_options, streckung_idx),
                ],
            ))

        return tasks
