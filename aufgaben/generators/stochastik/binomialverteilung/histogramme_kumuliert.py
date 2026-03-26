import random

from aufgaben.core.tolerances import graph_read_tolerance_from_span
from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_analysis_calc, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.shared import (
    prob_at_least,
    prob_between_open_closed,
    prob_exactly,
    prob_less_than,
    violates_probability_rounding_policy,
)
from aufgaben.generators.stochastik.binomialverteilung.textbausteine import SCENARIOS


def _sample_parameters(rng: random.Random) -> tuple[int, float]:
    n = rng.randint(10, 18)
    p = rng.choice([x / 100 for x in range(20, 81)])
    return n, p


def _build_visual(n: int, p: float) -> dict:
    return {
        "type": "plot",
        "spec": {
            "type": "binomial-histogramm-kumuliert",
            "n": n,
            "p": p,
        },
    }



class BinomialHistogrammeKumuliertGenerator(TaskGenerator):
    generator_key = "stochastik.binomialverteilung.histogramme_kumuliert"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]

            for _ in range(220):
                n, p = _sample_parameters(rng)

                center = int(round(n * p))
                exact_k = min(n - 1, max(1, center + rng.randint(-2, 2)))
                at_least_k = min(n - 1, max(1, center + rng.randint(-1, 3)))
                less_than_k = min(n, max(2, center + rng.randint(0, 4)))

                lower_open = min(n - 3, max(0, center + rng.randint(-3, 0)))
                upper_closed = min(n, max(lower_open + 2, lower_open + rng.randint(2, 5)))

                exact_probability = prob_exactly(n=n, p=p, k=exact_k)
                at_least_probability = prob_at_least(n=n, p=p, k=at_least_k)
                less_than_probability = prob_less_than(n=n, p=p, k=less_than_k)
                interval_probability = prob_between_open_closed(
                    n=n,
                    p=p,
                    lower_open=lower_open,
                    upper_closed=upper_closed,
                )

                probabilities = [
                    exact_probability,
                    at_least_probability,
                    less_than_probability,
                    interval_probability,
                ]

                if violates_probability_rounding_policy(probabilities=probabilities, decimals=2):
                    continue
                break
            else:
                raise ValueError("Konnte keine plausiblen Histogramm-Aufgabe (kumuliert) erzeugen.")

            p_percent = int(round(100 * p))
            intro_base_variants = [
                f"{scenario.intro_prefix} Es werden {n} {scenario.sample_object_plural} betrachtet.",
                f"{scenario.intro_prefix} {n} {scenario.sample_object_plural} werden zufällig ausgewählt.",
                f"{scenario.intro_prefix} In einer Stichprobe befinden sich {n} {scenario.sample_object_plural}.",
            ]
            intro = (
                f"{rng.choice(intro_base_variants)}</p> "
                f"<p>Das Histogramm zeigt die kumulierte Verteilung der Zufallsgröße X, die die Anzahl der "
                f"{scenario.success_plural} angibt.</p> <p>Bestimmen Sie die Wahrscheinlichkeiten "
                f"der folgenden Ereignisse (auf 2 NKS gerundet)."
            )

            questions = [
                f"Von den {scenario.group_dative_plural} sind genau {exact_k} {scenario.success_plural}.",
                f"Von den {scenario.group_dative_plural} sind mindestens {at_least_k} {scenario.success_plural}.",
                f"Von den {scenario.group_dative_plural} sind weniger als {less_than_k} {scenario.success_plural}.",
                (
                    f"Von den {scenario.group_dative_plural} sind mehr als {lower_open} und höchstens "
                    f"{upper_closed} {scenario.success_plural}."
                ),
            ]

            answers = [
                numerical(exact_probability, tolerance=graph_read_tolerance_from_span(1.02), decimals=2),
                numerical(at_least_probability, tolerance=graph_read_tolerance_from_span(1.02), decimals=2),
                numerical(less_than_probability, tolerance=graph_read_tolerance_from_span(1.02), decimals=2),
                numerical(interval_probability, tolerance=graph_read_tolerance_from_span(1.02), decimals=2),
            ]

            visual = _build_visual(n=n, p=p)

            tasks.append(Task(einleitung=intro, fragen=questions, antworten=answers, visual=visual))

        return tasks

