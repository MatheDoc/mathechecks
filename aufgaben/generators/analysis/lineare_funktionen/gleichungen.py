"""Generatoren für Checks 07–08 (Gleichungen / Ungleichungen).

07  Nullstellen + Vorzeichenbereiche  (nullstellen-vorzeichen)
08  Schnittpunkte + Vergleichsbereiche (schnittpunkte-vergleich)
"""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc, mc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.lineare_funktionen.shared import (
    display_eq,
    fmt_number,
    linear_latex,
    sample_linear_nice_null,
    sample_two_linear_intersecting,
)


# ===================================================================
# Check 07 – Nullstellen + Vorzeichenbereiche
# ===================================================================

class NullstellenVorzeichenGenerator(TaskGenerator):
    """Nullstelle berechnen, Vorzeichen links/rechts angeben."""

    generator_key = "analysis.lineare_funktionen.nullstellen_vorzeichen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, float]] = set()

        while len(tasks) < count:
            m, b = sample_linear_nice_null(rng)
            if (m, b) in used:
                continue
            used.add((m, b))

            x0 = -b / m  # ganzzahlig per Konstruktion
            eq = linear_latex(m, b)

            # Vorzeichen links/rechts der Nullstelle
            if m > 0:
                links = "negativ"
                rechts = "positiv"
            else:
                links = "positiv"
                rechts = "negativ"

            options_vz = ["positiv", "negativ"]
            idx_links = options_vz.index(links)
            idx_rechts = options_vz.index(rechts)

            tasks.append(Task(
                einleitung=f"Gegeben:{display_eq(eq)}",
                fragen=[
                    "Nullstelle $ x_0 = $",
                    "$ f(x) $ ist links der Nullstelle …",
                    "$ f(x) $ ist rechts der Nullstelle …",
                ],
                antworten=[
                    f"$ x_0 = ${numerical_analysis_calc(x0)}",
                    mc(options_vz, idx_links),
                    mc(options_vz, idx_rechts),
                ],
            ))

        return tasks


# ===================================================================
# Check 08 – Schnittpunkte + Vergleichsbereiche
# ===================================================================

class SchnittpunkteVergleichGenerator(TaskGenerator):
    """Schnittpunkt zweier Geraden und Vergleich links/rechts."""

    generator_key = "analysis.lineare_funktionen.schnittpunkte_vergleich"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, float, float, float]] = set()

        while len(tasks) < count:
            m1, b1, m2, b2 = sample_two_linear_intersecting(rng)
            key = (m1, b1, m2, b2)
            if key in used:
                continue
            used.add(key)

            x_s = (b2 - b1) / (m1 - m2)
            y_s = m1 * x_s + b1

            eq1 = linear_latex(m1, b1, name="f")
            eq2 = linear_latex(m2, b2, name="g")

            # Wer liegt links vom Schnittpunkt oben?
            # Vergleiche f(x_s - 1) mit g(x_s - 1)
            diff_slope = m1 - m2  # f(x) - g(x) = (m1-m2)x + (b1-b2)
            if diff_slope > 0:
                # f steigt stärker → links f < g, rechts f > g
                links = "$ f(x) < g(x) $"
                rechts = "$ f(x) > g(x) $"
                idx_links = 0
                idx_rechts = 1
            else:
                links = "$ f(x) > g(x) $"
                rechts = "$ f(x) < g(x) $"
                idx_links = 1
                idx_rechts = 0

            x_s_display = int(x_s) if x_s == int(x_s) else fmt_number(x_s)

            options_vergleich = ["$ f(x) < g(x) $", "$ f(x) > g(x) $"]

            tasks.append(Task(
                einleitung=(
                    f"Gegeben:"
                    f"{display_eq(eq1)}"
                    f"{display_eq(eq2)}"
                ),
                fragen=[
                    "Schnittpunkt",
                    "Links der Schnittstelle gilt …",
                    "Rechts der Schnittstelle gilt …",
                ],
                antworten=[
                    f"$ P( ${numerical_analysis_calc(x_s)}$ \\mid ${numerical_analysis_calc(y_s)}$ ) $",
                    mc(options_vergleich, idx_links),
                    mc(options_vergleich, idx_rechts),
                ],
            ))

        return tasks
