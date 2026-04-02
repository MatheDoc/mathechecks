import math
import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_analysis_calc, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.textbausteine import SCENARIOS


def _percent_placeholder(value: float) -> str:
    percent = int(round(value * 100))
    return f"{{1:NUMERICAL:={percent}:1}} %"


def _de(value: float, decimals: int) -> str:
    return f"{value:.{decimals}f}".replace(".", ",")


class BinomialKennzahlenNMuGegebenGenerator(TaskGenerator):
    generator_key = "stochastik.binomialverteilung.kennzahlen_n_mu_gegeben"

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
                    f"{scenario.intro_prefix} Es werden insgesamt {n} {scenario.sample_object_plural} betrachtet. "
                    f"Im Durchschnitt sind {_de(mu, 2)} {scenario.success_plural} zu erwarten."
                ),
                (
                    f"{scenario.intro_prefix} Für {n} {scenario.sample_object_plural} wird im Mittel "
                    f"mit {_de(mu, 2)} {scenario.success_plural} gerechnet."
                ),
                (
                    f"{scenario.intro_prefix} {n} {scenario.sample_object_plural} werden zufällig ausgewählt. "
                    f"Der Erwartungswert liegt bei $\\mu = {_de(mu, 2)}$."
                ),
            ]

            tasks.append(
                Task(
                    einleitung=rng.choice(intro_variants),
                    fragen=[
                        (
                            f"Bestimmen Sie die Wahrscheinlichkeit, {scenario.success_event_accusative} "
                            "anzutreffen (in\u00a0% auf eine ganze Zahl gerundet)."
                        ),
                        rng.choice([
                            "Bestimmen Sie die Standardabweichung $\\sigma$ der Zufallsgröße (auf 2 NKS gerundet).",
                            "Berechnen Sie $\\sigma$ (auf 2 NKS gerundet).",
                        ]),
                    ],
                    antworten=[
                        _percent_placeholder(p),
                        numerical(sigma, tolerance=0.01, decimals=4),
                    ],
                )
            )

        return tasks

