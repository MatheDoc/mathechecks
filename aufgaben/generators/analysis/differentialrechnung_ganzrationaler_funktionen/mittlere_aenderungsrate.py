"""Generator für Check 01 – Mittlere Änderungsrate."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.differentialrechnung_ganzrationaler_funktionen.shared import (
    display_eq,
    fmt,
    polynomial_latex,
    sample_centered_quadratic,
)


class MittlereAenderungsrateGenerator(TaskGenerator):
    generator_key = "analysis.differentialrechnung_ganzrationaler_funktionen.mittlere_aenderungsrate"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[tuple[float, ...], int, int]] = set()

        while len(tasks) < count:
            case, _center, _distance = sample_centered_quadratic(rng)
            interval = _sample_interval(rng, case)
            if interval is None:
                continue

            left, right, avg_rate = interval
            key = (case.signature(), left, right)
            if key in used:
                continue
            used.add(key)

            trend_options = ["steigt im Mittel", "fällt im Mittel"]
            trend_index = 0 if avg_rate > 0 else 1

            tasks.append(
                Task(
                    einleitung=(
                        f"Gegeben:\n\n{display_eq(polynomial_latex(case))}\n\n"
                        f"Berechnen Sie die mittlere Änderungsrate von $ f $ "
                        f"im Intervall $ [{fmt(left)};{fmt(right)}] $."
                    ),
                    fragen=[
                        f"die mittlere Änderungsrate von $ f $ auf $ [{fmt(left)};{fmt(right)}] $.",
                    ],
                    antworten=[
                        f"$ m = ${numerical_analysis_calc(avg_rate)}",
                    ],
                )
            )

        return tasks


def _sample_interval(rng: random.Random, case) -> tuple[int, int, float] | None:
    for _ in range(60):
        left, right = sorted(rng.sample(range(-3, 4), 2))
        avg_rate = (case.evaluate(right) - case.evaluate(left)) / (right - left)
        if abs(avg_rate) < 0.5 or abs(avg_rate) > 12.0:
            continue
        return left, right, avg_rate
    return None