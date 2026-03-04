import math
import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.shared import (
    binom_cdf,
    prob_at_least,
    violates_probability_rounding_policy,
)
from aufgaben.generators.stochastik.binomialverteilung.textbausteine import SCENARIOS


def _sample_parameters(rng: random.Random) -> tuple[int, float]:
    n = rng.randint(20, 100)
    p = rng.choice([x / 100 for x in range(20, 81)])
    return n, p


def _prob_deviation_at_most(n: int, p: float, sigma_factor: float) -> float:
    mu = n * p
    sigma = math.sqrt(n * p * (1 - p))
    delta = sigma_factor * sigma
    lower = math.ceil(mu - delta)
    upper = math.floor(mu + delta)
    if lower > upper:
        return 0.0
    left = binom_cdf(n=n, p=p, k=lower - 1)
    right = binom_cdf(n=n, p=p, k=upper)
    return max(0.0, right - left)


def _prob_deviation_at_least(n: int, p: float, sigma_factor: float) -> float:
    mu = n * p
    sigma = math.sqrt(n * p * (1 - p))
    delta = sigma_factor * sigma
    left_bound = math.floor(mu - delta)
    right_bound = math.ceil(mu + delta)
    left = binom_cdf(n=n, p=p, k=left_bound)
    right = prob_at_least(n=n, p=p, k=right_bound)
    return min(1.0, max(0.0, left + right))


def _factor_text(value: float) -> str:
    if abs(value - int(value)) < 1e-9:
        return str(int(value))
    return str(value).replace(".", ",")


class BinomialUmgebungenSigmaGenerator(TaskGenerator):
    generator_key = "stochastik.binomialverteilung.umgebungen_sigma"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        sigma_factors = [1.0, 1.5, 2.0, 2.5, 3.0]

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]

            for _ in range(300):
                n, p = _sample_parameters(rng)
                p_percent = int(round(100 * p))
                factor = rng.choice(sigma_factors)
                at_most = rng.choice([True, False])

                if at_most:
                    probability = _prob_deviation_at_most(n=n, p=p, sigma_factor=factor)
                    qualifier = "höchstens"
                else:
                    probability = _prob_deviation_at_least(n=n, p=p, sigma_factor=factor)
                    qualifier = "mindestens"

                if violates_probability_rounding_policy([probability], decimals=4):
                    continue
                break
            else:
                raise ValueError("Konnte keine plausible Umgebung-sigma-Aufgabe erzeugen.")

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

            factor_text = _factor_text(factor)
            question = (
                f"Bestimmen Sie die Wahrscheinlichkeit, dass die Anzahl der {scenario.success_plural} um "
                f"{qualifier} die {factor_text}-fache Standardabweichung vom Erwartungswert abweicht "
                f"(auf 4 NKS gerundet)."
            )

            tasks.append(
                Task(
                    einleitung=intro,
                    fragen=[question],
                    antworten=[numerical(probability, tolerance=0.0001, decimals=4)],
                )
            )

        return tasks
