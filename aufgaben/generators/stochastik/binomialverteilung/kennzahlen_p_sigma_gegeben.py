import math
import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_analysis_calc, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.textbausteine import SCENARIOS


def _percent_text(value: float) -> str:
    return f"{int(round(value * 100))}%"


def _de(value: float, decimals: int) -> str:
    return f"{value:.{decimals}f}".replace(".", ",")


class BinomialKennzahlenPSigmaGegebenGenerator(TaskGenerator):
    generator_key = "stochastik.binomialverteilung.kennzahlen_p_sigma_gegeben"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]

            n = rng.randint(110, 290)
            p = rng.choice([x / 100 for x in range(20, 81)])
            mu = n * p
            sigma = math.sqrt(n * p * (1 - p))

            intro_variants = [
                (
                    f"{scenario.intro_prefix} Die Wahrscheinlichkeit für {scenario.success_event_accusative} "
                    f"beträgt {_percent_text(p)}. Die Standardabweichung beträgt \\(\\sigma = {_de(sigma, 4)}\\)."
                ),
                (
                    f"{scenario.intro_prefix} Mit Wahrscheinlichkeit {_percent_text(p)} tritt "
                    f"{scenario.success_event_accusative} auf. Für die Zufallsgrö�Ye gilt "
                    f"\\(\\sigma = {_de(sigma, 4)}\\)."
                ),
            ]

            tasks.append(
                Task(
                    einleitung=rng.choice(intro_variants),
                    fragen=[
                        rng.choice([
                            f"Bestimmen Sie, wie viele {scenario.success_plural} im Durchschnitt zu erwarten sind.",
                            "Bestimmen Sie den Erwartungswert \\(\\mu\\) der Zufallsgrö�Ye.",
                        ]),
                        (
                            f"Bestimmen Sie die Anzahl der insgesamt betrachteten {scenario.sample_object_plural} "
                            "(als ganze Zahl)."
                        ),
                    ],
                    antworten=[
                        numerical_stochastik_calc(mu),
                        numerical(n, tolerance=0, decimals=0),
                    ],
                )
            )

        return tasks


