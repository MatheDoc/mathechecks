import math
import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.textbausteine import SCENARIOS


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
            intro_variants = [
                (
                    f"{scenario.intro_prefix} Es werden insgesamt {n} {scenario.sample_object_plural} betrachtet. "
                    f"Die Wahrscheinlichkeit für {scenario.success_event_accusative} beträgt {p_text}."
                ),
                (
                    f"{scenario.intro_prefix} In einer Stichprobe von {n} {scenario.sample_object_plural} "
                    f"liegt die Wahrscheinlichkeit, {scenario.success_event_accusative} anzutreffen, bei {p_text}."
                ),
                (
                    f"{scenario.intro_prefix} {n} {scenario.sample_object_plural} werden zufällig ausgewählt. "
                    f"Mit einer Wahrscheinlichkeit von {p_text} tritt dabei {scenario.success_event_accusative} auf."
                ),
            ]

            tasks.append(
                Task(
                    einleitung=rng.choice(intro_variants),
                    fragen=[
                        rng.choice([
                            f"Bestimmen Sie, wie viele {scenario.success_plural} im Durchschnitt zu erwarten sind.",
                            "Bestimmen Sie den Erwartungswert \\(\\mu\\) der Zufallsgröße.",
                            f"Wie viele {scenario.success_plural} sind im Mittel zu erwarten?",
                        ]),
                        rng.choice([
                            "Bestimmen Sie die Standardabweichung \\(\\sigma\\) der Zufallsgröße (auf 2 NKS gerundet).",
                            "Berechnen Sie \\(\\sigma\\) (auf 2 NKS gerundet).",
                        ]),
                    ],
                    antworten=[
                        numerical(mu, tolerance=0.01, decimals=2),
                        numerical(sigma, tolerance=0.01, decimals=4),
                    ],
                )
            )

        return tasks
