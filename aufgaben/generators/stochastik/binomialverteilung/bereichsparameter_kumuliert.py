import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.shared import (
    max_successes_for_at_most,
    min_successes_for_at_least,
)
from aufgaben.generators.stochastik.binomialverteilung.textbausteine import SCENARIOS


def _bounded_int(rng: random.Random, lower: int, upper: int) -> int:
    if upper <= lower:
        return lower
    return rng.randint(lower, upper)


def _sample_parameters(rng: random.Random) -> tuple[int, float]:
    n = rng.randint(24, 95)
    p = rng.choice([x / 100 for x in range(20, 81)])
    return n, p


def _to_cdf_difference(a: int, b: int) -> tuple[int, int]:
    return b, a - 1


def _cdf_answer_from_interval(a: int, b: int) -> str:
    upper_k, lower_k = _to_cdf_difference(a=a, b=b)
    return (
        "\\( P = P(X\\leq \\)"
        f"{numerical(upper_k, tolerance=0, decimals=0)}"
        "\\( ) - P(X\\leq \\)"
        f"{numerical(lower_k, tolerance=0, decimals=0)}"
        "\\( ) \\)"
    )


class BinomialBereichsparameterKumuliertGenerator(TaskGenerator):
    generator_key = "stochastik.binomialverteilung.bereichsparameter_kumuliert"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]
            n, p = _sample_parameters(rng)
            p_percent = int(round(100 * p))

            exact_k = _bounded_int(rng, max(0, int(n * p * 0.75)), min(n, int(n * p * 1.25)))
            at_least_k = _bounded_int(rng, max(0, int(n * p * 0.8)), min(n, int(n * p * 1.1)))
            less_than_k = _bounded_int(rng, max(1, int(n * p * 0.9)), min(n, int(n * p * 1.25)))

            lower_open = _bounded_int(rng, max(0, int(n * p * 0.55)), min(n - 2, int(n * p * 0.95)))
            upper_closed = _bounded_int(
                rng,
                max(lower_open + 2, int(n * p * 1.02)),
                min(n, int(n * p * 1.35)),
            )

            percent_value = _bounded_int(rng, 18, 78)
            percent_is_at_least = rng.choice([True, False])

            if percent_is_at_least:
                percent_question = (
                    f"Von den {scenario.group_dative_plural} sind mindestens {percent_value}% "
                    f"{scenario.success_plural}."
                )
                percent_a = min_successes_for_at_least(n * percent_value / 100)
                percent_b = n
            else:
                percent_question = (
                    f"Von den {scenario.group_dative_plural} sind höchstens {percent_value}% "
                    f"{scenario.success_plural}."
                )
                percent_a = 0
                percent_b = max_successes_for_at_most(n * percent_value / 100)

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

            intro = (
                f"{rng.choice(intro_variants)}</p> <p>Formulieren Sie die gesuchte Wahrscheinlichkeit so, dass diese "
                "ausschließlich mithilfe von Ausdrücken der Form \\( P(X \\leq k) \\) dargestellt wird. "
                "Tritt ein angezeigter Term in der Lösung nicht auf, setzen Sie \\( k=-1 \\)."
            )

            questions = [
                f"Von den {scenario.group_dative_plural} sind genau {exact_k} {scenario.success_plural}.",
                f"Von den {scenario.group_dative_plural} sind mindestens {at_least_k} {scenario.success_plural}.",
                f"Von den {scenario.group_dative_plural} sind weniger als {less_than_k} {scenario.success_plural}.",
                (
                    f"Von den {scenario.group_dative_plural} sind mehr als {lower_open} und höchstens "
                    f"{upper_closed} {scenario.success_plural}."
                ),
                percent_question,
            ]

            answers = [
                _cdf_answer_from_interval(a=exact_k, b=exact_k),
                _cdf_answer_from_interval(a=at_least_k, b=n),
                _cdf_answer_from_interval(a=0, b=less_than_k - 1),
                _cdf_answer_from_interval(a=lower_open + 1, b=upper_closed),
                _cdf_answer_from_interval(a=percent_a, b=percent_b),
            ]

            tasks.append(Task(einleitung=intro, fragen=questions, antworten=answers))

        return tasks
