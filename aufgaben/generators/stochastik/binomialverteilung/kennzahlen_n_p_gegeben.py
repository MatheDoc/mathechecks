import math
import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_analysis_calc, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.textbausteine import SCENARIOS, sample_probability_intro_variants


def _percent_text(value: float) -> str:
    return f"{int(round(value * 100))}%"


class BinomialKennzahlenNPGegebenGenerator(TaskGenerator):
    generator_key = "stochastik.binomialverteilung.kennzahlen_n_p_gegeben"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]

            n = rng.randint(110, 290)
            p = rng.choice([x / 100 for x in range(20, 81)])
            mu = n * p
            sigma = math.sqrt(n * p * (1 - p))

            p_text = _percent_text(p)
            tasks.append(
                Task(
                    einleitung=rng.choice(
                        sample_probability_intro_variants(
                            scenario=scenario,
                            n=n,
                            p_text=p_text,
                        )
                    ),
                    fragen=[
                        rng.choice([
                            f"Bestimmen Sie, wie viele {scenario.success_plural} im Durchschnitt zu erwarten sind.",
                            "Bestimmen Sie den Erwartungswert $\\mu$ der Zufallsgröße.",
                            f"Bestimmen Sie, wie viele {scenario.success_plural} im Mittel zu erwarten sind.",
                        ]),
                        rng.choice([
                            "Bestimmen Sie die Standardabweichung $\\sigma$ der Zufallsgröße (auf 2 NKS gerundet).",
                            "Berechnen Sie $\\sigma$ (auf 2 NKS gerundet).",
                        ]),
                    ],
                    antworten=[
                        numerical_stochastik_calc(mu),
                        numerical(sigma, tolerance=0.01, decimals=4),
                    ],
                )
            )

        return tasks


