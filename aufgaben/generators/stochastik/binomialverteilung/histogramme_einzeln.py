import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical
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
    p = rng.choice([x / 100 for x in range(22, 79)])
    return n, p


def _pmf_values(n: int, p: float) -> list[float]:
    return [prob_exactly(n=n, p=p, k=k) for k in range(n + 1)]


def _build_visual(n: int, pmf: list[float]) -> dict:
    x_values = list(range(n + 1))
    max_y = max(pmf)
    y_max = min(1.0, max(0.12, max_y * 1.2))

    return {
        "type": "plot",
        "spec": {
            "type": "plotly",
            "traces": [
                {
                    "kind": "bar",
                    "x": x_values,
                    "y": pmf,
                    "name": "P(X = k)",
                    "marker": {
                        "color": "rgba(209, 213, 219, 0.95)",
                        "line": {"color": "rgba(107, 114, 128, 0.9)", "width": 1},
                    },
                    "hoverinfo": "x+y",
                }
            ],
            "layout": {
                "xaxis": {
                    "title": "k",
                    "dtick": 1,
                    "range": [-0.5, n + 0.5],
                },
                "yaxis": {
                    "title": "P(X = k)",
                    "range": [0, y_max],
                    "tickformat": ".2f",
                },
                "showlegend": False,
                "bargap": 0,
                "bargroupgap": 0,
            },
            "width": 760,
            "height": 520,
            "scale": 1,
        },
    }


class BinomialHistogrammeEinzelnGenerator(TaskGenerator):
    generator_key = "stochastik.binomialverteilung.histogramme_einzeln"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]

            for _ in range(220):
                n, p = _sample_parameters(rng)

                center = int(round(n * p))
                exact_k = min(n - 1, max(1, center + rng.randint(-2, 2)))
                more_than_k = min(n - 2, max(0, center + rng.randint(-3, 1)))
                at_most_k = min(n - 1, max(1, center + rng.randint(-1, 3)))

                interval_low = min(n - 3, max(0, center + rng.randint(-3, 0)))
                interval_high_exclusive = min(
                    n,
                    max(interval_low + 2, interval_low + rng.randint(2, 5)),
                )

                exact_probability = prob_exactly(n=n, p=p, k=exact_k)
                more_than_probability = prob_at_least(n=n, p=p, k=more_than_k + 1)
                at_most_probability = prob_less_than(n=n, p=p, k=at_most_k + 1)
                interval_probability = prob_between_open_closed(
                    n=n,
                    p=p,
                    lower_open=interval_low - 1,
                    upper_closed=interval_high_exclusive - 1,
                )

                probabilities = [
                    exact_probability,
                    more_than_probability,
                    at_most_probability,
                    interval_probability,
                ]

                if violates_probability_rounding_policy(probabilities=probabilities, decimals=2):
                    continue
                break
            else:
                raise ValueError("Konnte keine plausiblen Histogramm-Aufgabe (einzeln) erzeugen.")

            p_percent = int(round(100 * p))
            intro_base_variants = [
                f"{scenario.intro_prefix} Es werden {n} {scenario.sample_object_plural} betrachtet.",
                f"{scenario.intro_prefix} {n} {scenario.sample_object_plural} werden zufällig ausgewählt.",
                f"{scenario.intro_prefix} In einer Stichprobe befinden sich {n} {scenario.sample_object_plural}.",
            ]
            intro = (
                f"{rng.choice(intro_base_variants)}</p> "
                f"<p>Das Histogramm zeigt die Verteilung der Zufallsgröße X, die die Anzahl der "
                f"{scenario.success_plural} angibt.</p> <p>Bestimmen Sie die Wahrscheinlichkeiten "
                f"der folgenden Ereignisse (auf 2 NKS gerundet)."
            )

            questions = [
                f"Von den {scenario.group_dative_plural} sind genau {exact_k} {scenario.success_plural}.",
                f"Von den {scenario.group_dative_plural} sind mehr als {more_than_k} {scenario.success_plural}.",
                f"Von den {scenario.group_dative_plural} sind höchstens {at_most_k} {scenario.success_plural}.",
                (
                    f"Von den {scenario.group_dative_plural} sind mindestens {interval_low} und weniger als "
                    f"{interval_high_exclusive} {scenario.success_plural}."
                ),
            ]

            answers = [
                numerical(exact_probability, tolerance=0.01, decimals=2),
                numerical(more_than_probability, tolerance=0.01, decimals=2),
                numerical(at_most_probability, tolerance=0.01, decimals=2),
                numerical(interval_probability, tolerance=0.01, decimals=2),
            ]

            visual = _build_visual(n=n, pmf=_pmf_values(n=n, p=p))

            tasks.append(Task(einleitung=intro, fragen=questions, antworten=answers, visual=visual))

        return tasks
