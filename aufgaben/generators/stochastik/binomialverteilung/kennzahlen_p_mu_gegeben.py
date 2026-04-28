import math
import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_analysis_calc, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.textbausteine import SCENARIOS, probability_intro_variants


def _percent_text(value: float) -> str:
    return f"{int(round(value * 100))}%"


def _de(value: float, decimals: int) -> str:
    return f"{value:.{decimals}f}".replace(".", ",")


class BinomialKennzahlenPMuGegebenGenerator(TaskGenerator):
    generator_key = "stochastik.binomialverteilung.kennzahlen_p_mu_gegeben"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]

            n = rng.randint(110, 290)
            p = rng.choice([x / 100 for x in range(20, 81)])
            mu = n * p
            sigma = math.sqrt(n * p * (1 - p))
            probability_intros = probability_intro_variants(scenario=scenario, p_text=_percent_text(p))

            intro_variants = [
                (
                    f"{probability_intros[0]} Im Durchschnitt sind {_de(mu, 2)} {scenario.success_plural} zu erwarten."
                ),
                (
                    f"{scenario.intro_prefix} Es gilt p = {_percent_text(p)} und die durchschnittlich erwartete "
                    f"Anzahl liegt bei $\\mu = {_de(mu, 2)}$."
                ),
                (
                    f"{probability_intros[2]} Der Erwartungswert beträgt $\\mu = {_de(mu, 2)}$."
                ),
            ]

            tasks.append(
                Task(
                    einleitung=rng.choice(intro_variants),
                    fragen=[
                        (
                            f"Bestimmen Sie, wie viele {scenario.sample_object_plural} insgesamt betrachtet "
                            "werden (als ganze Zahl)."
                        ),
                        rng.choice([
                            "Bestimmen Sie die Standardabweichung $\\sigma$ der Zufallsgröße (auf 2 NKS gerundet).",
                            "Berechnen Sie $\\sigma$ (auf 2 NKS gerundet).",
                        ]),
                    ],
                    antworten=[
                        numerical(n, tolerance=0, decimals=0),
                        numerical(sigma, tolerance=0.01, decimals=4),
                    ],
                )
            )

        return tasks

