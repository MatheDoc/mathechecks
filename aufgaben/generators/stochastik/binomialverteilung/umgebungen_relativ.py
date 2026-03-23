import math
import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_analysis_calc, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.shared import (
    binom_cdf,
    prob_at_least,
    violates_probability_rounding_policy,
)
from aufgaben.generators.stochastik.binomialverteilung.textbausteine import SCENARIOS


def _sample_parameters(rng: random.Random) -> tuple[int, float]:
    n = rng.randint(35, 120)
    p = rng.choice([x / 100 for x in range(22, 79)])
    return n, p


def _prob_deviation_at_most(n: int, p: float, relative_delta: float) -> float:
    mu = n * p
    delta = relative_delta * mu
    lower = math.ceil(mu - delta)
    upper = math.floor(mu + delta)
    if lower > upper:
        return 0.0
    left = binom_cdf(n=n, p=p, k=lower - 1)
    right = binom_cdf(n=n, p=p, k=upper)
    return max(0.0, right - left)


def _prob_deviation_at_least(n: int, p: float, relative_delta: float) -> float:
    mu = n * p
    delta = relative_delta * mu
    left_bound = math.floor(mu - delta)
    right_bound = math.ceil(mu + delta)
    left = binom_cdf(n=n, p=p, k=left_bound)
    right = prob_at_least(n=n, p=p, k=right_bound)
    return min(1.0, max(0.0, left + right))


class BinomialUmgebungenRelativGenerator(TaskGenerator):
    generator_key = "stochastik.binomialverteilung.umgebungen_relativ"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]

            for _ in range(300):
                n, p = _sample_parameters(rng)
                p_percent = int(round(100 * p))

                relative_percent = rng.randint(6, 38)
                relative_delta = relative_percent / 100
                at_most = rng.choice([True, False])

                if at_most:
                    probability = _prob_deviation_at_most(n=n, p=p, relative_delta=relative_delta)
                    qualifier = "höchstens"
                else:
                    probability = _prob_deviation_at_least(n=n, p=p, relative_delta=relative_delta)
                    qualifier = "mindestens"

                if violates_probability_rounding_policy([probability], decimals=4):
                    continue
                break
            else:
                raise ValueError("Konnte keine plausible Umgebung-relativ-Aufgabe erzeugen.")

            intro_variants = [
                (
                    f"{scenario.intro_prefix} Es werden {n} {scenario.sample_object_plural} betrachtet. "
                    f"Die Wahrscheinlichkeit für {scenario.success_event_accusative} beträgt {p_percent}%."
                ),
                (
                    f"{scenario.intro_prefix} {n} {scenario.sample_object_plural} werden zufällig ausgewählt. "
                    f"Die Wahrscheinlichkeit, {scenario.success_event_accusative} anzutreffen, liegt bei {p_percent}%."
                ),
                (
                    f"{scenario.intro_prefix} In einer Stichprobe von {n} {scenario.sample_object_plural} "
                    f"tritt {scenario.success_event_accusative} mit einer Wahrscheinlichkeit von {p_percent}% auf."
                ),
            ]
            intro = rng.choice(intro_variants)

            question = (
                f"Bestimmen Sie die Wahrscheinlichkeit, dass die Anzahl der {scenario.success_plural} um "
                f"{qualifier} {relative_percent}% vom Erwartungswert abweicht (auf 4 NKS gerundet)."
            )

            tasks.append(
                Task(
                    einleitung=intro,
                    fragen=[question],
                    antworten=[numerical_stochastik_calc(probability)],
                )
            )

        return tasks


