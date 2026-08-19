"""Regression über Normalengleichungen (lineares Gleichungssystem).

Mischung: ca. 30 % linear (2x2), 40 % quadratisch (3x3), 30 % kubisch (4x4).
Punktanzahl variiert: linear 2-4, quadratisch 3-4, kubisch genau 4 Punkte.
Bei Minimalanzahl ist der Fit eine exakte Interpolation (gewollt, wird im
Aufgabentext nicht verraten). Annahmefilter: R² >= 0,95 und Formtreue
(siehe shared.model_plausible). Gefragt ist die Regressionsfunktion; das
LGS wird mit GTR oder Gauß-Algorithmus gelöst.
"""

import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.regression.shared import (
    assert_fit_matches,
    fd_deviations,
    make_table,
    model_plausible,
    poly_eval,
    poly_function_answer,
    power_sums,
)

_ANSATZ = {
    1: "f(x) = m \\cdot x + b",
    2: "f(x) = a x^2 + b x + c",
    3: "f(x) = a x^3 + b x^2 + c x + d",
}

_ART = {1: "lineare", 2: "quadratische", 3: "kubische"}

# Punktanzahl je Modellgrad (maximal 4 Datenpunkte).
_N_CHOICES = {1: [2, 3, 4], 2: [3, 4], 3: [4]}

# Skalierung der orthogonalen Abweichungen je Modellgrad.
_SCALES = {1: [0.5, 1.0], 2: [0.25, 0.5], 3: [0.25]}

# x-Werte: arithmetische Folgen (Voraussetzung für orthogonale Abweichungen),
# gruppiert nach (Grad, Punktanzahl).
_X_SETS = {
    (1, 2): [[0, 2], [1, 3], [0, 4], [2, 6], [1, 5]],
    (1, 3): [[0, 1, 2], [1, 2, 3], [0, 2, 4], [1, 3, 5], [2, 4, 6]],
    (1, 4): [[0, 1, 2, 3], [1, 2, 3, 4], [0, 2, 4, 6]],
    (2, 3): [[0, 1, 2], [1, 2, 3], [-1, 0, 1], [0, 2, 4], [2, 3, 4]],
    (2, 4): [[0, 1, 2, 3], [1, 2, 3, 4], [-1, 0, 1, 2], [-2, -1, 0, 1]],
    (3, 4): [[0, 1, 2, 3], [-1, 0, 1, 2], [1, 2, 3, 4], [-2, -1, 0, 1]],
}


def _sample_coeffs(rng: random.Random, degree: int) -> list[float]:
    """Wahre Koeffizienten a_0..a_d, klein und glatt."""
    if degree == 1:
        m = rng.choice([-3, -2, -1.5, -1, 1, 1.5, 2, 3])
        b = rng.choice(range(-5, 10))
        return [float(b), float(m)]
    if degree == 2:
        a = rng.choice([-2, -1.5, -1, -0.5, 0.5, 1, 1.5, 2])
        b = rng.choice(range(-4, 5))
        c = rng.choice(range(-6, 7))
        return [float(c), float(b), float(a)]
    a = rng.choice([-1, -0.5, 0.5, 1])
    b = rng.choice(range(-3, 4))
    c = rng.choice(range(-4, 5))
    d = rng.choice(range(-6, 7))
    return [float(d), float(c), float(b), float(a)]


class RegressionLgsGenerator(TaskGenerator):
    generator_key = "analysis.regression.lgs"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple] = set()

        anteil_linear = round(count * 0.3)
        anteil_kubisch = round(count * 0.3)
        anteil_quadratisch = count - anteil_linear - anteil_kubisch
        degrees = (
            [1] * anteil_linear + [2] * anteil_quadratisch + [3] * anteil_kubisch
        )

        for degree in degrees:
            while True:
                n_points = rng.choice(_N_CHOICES[degree])
                x_values = [float(x) for x in rng.choice(_X_SETS[(degree, n_points)])]
                coeffs = _sample_coeffs(rng, degree)
                deviations = fd_deviations(rng, len(x_values), degree, _SCALES[degree])
                y_values = [
                    round(poly_eval(coeffs, x) + e, 2)
                    for x, e in zip(x_values, deviations)
                ]

                if any(abs(y) > 80 for y in y_values):
                    continue
                if not model_plausible(x_values, y_values, coeffs):
                    continue
                x_pow, xy = power_sums(x_values, y_values, degree)
                if any(abs(value) > 10000 for value in x_pow + xy):
                    continue

                key = (tuple(x_values), tuple(y_values))
                if key in used:
                    continue
                used.add(key)

                assert_fit_matches(x_values, y_values, coeffs)
                break

            table = make_table(x_values, y_values)
            einleitung = f"Gegeben sind die folgenden Wertepaare:{table}"

            fragen = [
                f"Bestimmen Sie die {_ART[degree]} Regressionsfunktion mit dem "
                f"Ansatz $ {_ANSATZ[degree]} $."
            ]
            antworten = [poly_function_answer(coeffs, var="x", func_name="f")]

            tasks.append(Task(einleitung=einleitung, fragen=fragen, antworten=antworten))

        return tasks
