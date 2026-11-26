import math
import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.shared import (
    binom_cdf,
    prob_at_least,
    violates_probability_rounding_policy,
)
from aufgaben.generators.stochastik.binomialverteilung.textbausteine import (
    SCENARIOS,
    environment_probability_question,
    sample_probability_intro_variants,
)


def _prob_deviation_at_most(n: int, p: float, delta: float) -> float:
    """P(|X - mu| <= delta)."""
    mu = n * p
    lower = math.ceil(mu - delta)
    upper = math.floor(mu + delta)
    if lower > upper:
        return 0.0
    return max(0.0, binom_cdf(n=n, p=p, k=upper) - binom_cdf(n=n, p=p, k=lower - 1))


def _prob_deviation_at_least(n: int, p: float, delta: float) -> float:
    """P(|X - mu| >= delta)."""
    mu = n * p
    left = binom_cdf(n=n, p=p, k=math.floor(mu - delta))
    right = prob_at_least(n=n, p=p, k=math.ceil(mu + delta))
    return min(1.0, max(0.0, left + right))


def _factor_text(value: float) -> str:
    if abs(value - int(value)) < 1e-9:
        return str(int(value))
    return str(value).replace(".", ",")


class BinomialUmgebungenGenerator(TaskGenerator):
    """Eine Situation, drei Teilfragen: absolute, relative und Sigma-Umgebung des Erwartungswerts."""

    generator_key = "stochastik.binomialverteilung.umgebungen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        sigma_factors = [1.0, 1.5, 2.0, 2.5, 3.0]

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]

            for _ in range(500):
                n = rng.randint(35, 110)
                p = rng.choice([x / 100 for x in range(22, 79)])
                mu = n * p
                sigma = math.sqrt(n * p * (1 - p))

                delta_abs = rng.randint(2, 6)
                rel_percent = rng.randint(6, 25)
                factor = rng.choice(sigma_factors)
                deltas = [delta_abs, rel_percent / 100 * mu, factor * sigma]
                qualifiers = [rng.choice(["höchstens", "mindestens"]) for _ in deltas]

                probabilities = [
                    _prob_deviation_at_most(n, p, delta) if q == "höchstens" else _prob_deviation_at_least(n, p, delta)
                    for delta, q in zip(deltas, qualifiers)
                ]
                if violates_probability_rounding_policy(probabilities, decimals=4):
                    continue
                # Drei verschiedene Ergebnisse, damit keine Teilfrage die andere verrät.
                if len({round(value, 4) for value in probabilities}) < 3:
                    continue
                break
            else:
                raise ValueError("Konnte keine plausible Umgebungen-Aufgabe erzeugen.")

            intro = rng.choice(
                sample_probability_intro_variants(scenario=scenario, n=n, p_text=f"{int(round(100 * p))}%")
            )
            phrases = [
                f"um {qualifiers[0]} {delta_abs} vom Erwartungswert abweicht",
                f"um {qualifiers[1]} {rel_percent}% vom Erwartungswert abweicht",
                (
                    f"um {qualifiers[2]} eine Standardabweichung vom Erwartungswert abweicht"
                    if factor == 1.0
                    else f"um {qualifiers[2]} die {_factor_text(factor)}-fache Standardabweichung vom Erwartungswert abweicht"
                ),
            ]

            tasks.append(
                Task(
                    einleitung=intro,
                    fragen=[environment_probability_question(scenario=scenario, deviation_phrase=phrase) for phrase in phrases],
                    antworten=[numerical_stochastik_calc(value) for value in probabilities],
                )
            )

        return tasks
