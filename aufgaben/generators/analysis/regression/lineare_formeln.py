"""Lineare Regression rechnerisch mit den Regressionsformeln.

Fragen: Mittelwerte, Steigung m und y-Achsenabschnitt b. Die Daten sind so
konstruiert, dass alle gesuchten Werte höchstens 2 Nachkommastellen haben
(Abweichungen orthogonal zu 1 und x => Regression trifft die wahre Gerade).
Annahmefilter: R² >= 0,95, damit die Punktwolke optisch linear wirkt.
"""

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.regression.shared import (
    assert_fit_matches,
    linear_stats,
    make_table,
    model_plausible,
    triple_deviations,
)

_M_CHOICES = [-2.5, -2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
_B_CHOICES = [b / 2 for b in range(4, 41)]  # 2.0 bis 20.0 in 0.5er-Schritten


def _is_two_decimals(value: float) -> bool:
    return abs(round(value * 100) - value * 100) < 1e-6


def _sample_x_values(rng: random.Random) -> list[int]:
    """Kleine ganzzahlige, aufsteigende x-Werte mit ganzzahligem S_xx."""
    while True:
        n = rng.choice([4, 5, 6])
        x_values = sorted(rng.sample(range(0, 9), n))
        total = sum(x_values)
        # S_xx = Σx² − (Σx)²/n ganzzahlig; zugleich wird x̄ "schön".
        if (total * total) % n != 0:
            continue
        return x_values


class RegressionLineareFormelnGenerator(TaskGenerator):
    generator_key = "analysis.regression.lineare_formeln"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple] = set()

        while len(tasks) < count:
            x_values = _sample_x_values(rng)
            m_true = rng.choice(_M_CHOICES)
            b_true = rng.choice(_B_CHOICES)
            deviations = triple_deviations(rng, [float(x) for x in x_values])
            y_values = [
                round(m_true * x + b_true + e, 2)
                for x, e in zip(x_values, deviations)
            ]

            x_mean, y_mean, s_xx, s_xy, m, b = linear_stats(
                [float(x) for x in x_values], y_values
            )

            if not all(
                _is_two_decimals(value) for value in (x_mean, y_mean, m, b, s_xx, s_xy)
            ):
                continue
            if any(y < 0 or y > 60 for y in y_values):
                continue
            if abs(m - m_true) > 1e-9 or abs(b - b_true) > 1e-9:
                continue
            if not model_plausible(
                [float(x) for x in x_values], y_values, [b_true, m_true]
            ):
                continue

            key = (tuple(x_values), tuple(y_values))
            if key in used:
                continue
            used.add(key)

            assert_fit_matches([float(x) for x in x_values], y_values, [b, m])

            table = make_table(x_values, y_values)
            einleitung = f"Gegeben sind die folgenden Wertepaare:{table}"

            tasks.append(
                Task(
                    einleitung=einleitung,
                    fragen=[
                        "Berechnen Sie den Mittelwert $ \\bar{x} $ der $ x $-Werte.",
                        "Berechnen Sie den Mittelwert $ \\bar{y} $ der $ y $-Werte.",
                        "Berechnen Sie die Steigung $ m $ der Regressionsgeraden.",
                        "Berechnen Sie den $ y $-Achsenabschnitt $ b $ der Regressionsgeraden.",
                    ],
                    antworten=[
                        f"$ \\bar{{x}} = ${numerical_analysis_calc(x_mean)}",
                        f"$ \\bar{{y}} = ${numerical_analysis_calc(y_mean)}",
                        f"$ m = ${numerical_analysis_calc(m)}",
                        f"$ b = ${numerical_analysis_calc(b)}",
                    ],
                )
            )

        return tasks
