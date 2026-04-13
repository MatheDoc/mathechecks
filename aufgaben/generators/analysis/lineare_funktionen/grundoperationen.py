"""Generatoren für Checks 05–06 (Grundoperationen).

05  Punktprobe + Lage            (punktprobe)
06  Funktionswerte / Umkehrwerte (funktionswerte-umkehrwerte)
"""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc, mc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.lineare_funktionen.shared import (
    display_eq,
    linear_latex,
    sample_linear,
)


# ===================================================================
# Check 05 – Punktprobe + Lage
# ===================================================================

class PunktprobeGenerator(TaskGenerator):
    """Punktprobe und Lage (auf / über / unter dem Graphen)."""

    generator_key = "analysis.lineare_funktionen.punktprobe"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, float, int, int]] = set()

        while len(tasks) < count:
            m, b = sample_linear(rng)
            px = rng.randint(-6, 6)
            py = rng.randint(-10, 10)

            key = (m, b, px, py)
            if key in used:
                continue
            used.add(key)

            f_px = m * px + b
            eq = linear_latex(m, b)

            # Lage bestimmen
            if py == f_px:
                lage_text = "auf dem Graphen"
                lage_idx = 0
            elif py > f_px:
                lage_text = "oberhalb des Graphen"
                lage_idx = 1
            else:
                lage_text = "unterhalb des Graphen"
                lage_idx = 2

            options = ["auf dem Graphen", "oberhalb des Graphen", "unterhalb des Graphen"]

            tasks.append(Task(
                einleitung=(
                    f"Gegeben:{display_eq(eq)}"
                    f"Untersuchen Sie die Lage des Punktes $ P({px}|{py}) $ "
                    "bezüglich des Graphen von $ f $."
                ),
                fragen=[
                    f"$ f({px}) $",
                    f"Der Punkt $ P({px}|{py}) $ liegt …",
                ],
                antworten=[
                    f"$ f({px}) = ${numerical_analysis_calc(f_px)}",
                    mc(options, lage_idx),
                ],
            ))

        return tasks


# ===================================================================
# Check 06 – Funktionswerte und Umkehrwerte
# ===================================================================

class FunktionswerteUmkehrwerteGenerator(TaskGenerator):
    """Funktionswert f(x₀) und Umkehrwert f(x)=y₀."""

    generator_key = "analysis.lineare_funktionen.funktionswerte_umkehrwerte"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, float, int, int]] = set()

        while len(tasks) < count:
            m, b = sample_linear(rng)

            # x₀ für Funktionswert
            x0 = rng.randint(-6, 6)
            y0_fw = m * x0 + b

            # y₀ für Umkehrwert – so wählen, dass x ganzzahlig wird
            x_inv = rng.randint(-8, 8)
            y0_inv = m * x_inv + b

            key = (m, b, x0, x_inv)
            if key in used:
                continue
            if x0 == x_inv:
                continue
            used.add(key)

            eq = linear_latex(m, b)

            # y0_inv auf ganze Zahl oder halbe runden für saubere Ausgabe
            y0_display = int(y0_inv) if y0_inv == int(y0_inv) else round(y0_inv, 2)

            tasks.append(Task(
                einleitung=f"Gegeben:{display_eq(eq)}",
                fragen=[
                    f"Berechnen Sie $ f({x0}) $.",
                    f"Berechnen Sie $ x $ mit $ f(x) = {y0_display} $.",
                ],
                antworten=[
                    f"$ f({x0}) = ${numerical_analysis_calc(y0_fw)}",
                    f"$ x = ${numerical_analysis_calc(x_inv)}",
                ],
            ))

        return tasks
