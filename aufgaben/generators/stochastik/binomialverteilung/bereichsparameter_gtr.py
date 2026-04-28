import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_analysis_calc, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.shared import (
    max_successes_for_at_most,
    max_successes_for_less_than,
    min_successes_for_at_least,
    min_successes_for_more_than,
)
from aufgaben.generators.stochastik.binomialverteilung.textbausteine import (
    SCENARIOS,
    join_sentences,
    sample_probability_intro_variants,
)


def _bounded_int(rng: random.Random, lower: int, upper: int) -> int:
    if upper <= lower:
        return lower
    return rng.randint(lower, upper)


def _sample_parameters(rng: random.Random) -> tuple[int, float]:
    n = rng.randint(24, 99)
    p = rng.choice([x / 100 for x in range(20, 81)])
    return n, p


def _gtr_answer(a: int, b: int, n: int, p: float) -> str:
    p_text = f"{p:.2f}".replace(".", ",")
    p_placeholder = "{1:NUMERICAL:=" + p_text + ":0}"
    return (
        "Bcd(a,b,n,p) = Bcd("
        f"{numerical(a, tolerance=0, decimals=0)},"
        f"{numerical(b, tolerance=0, decimals=0)},"
        f"{numerical(n, tolerance=0, decimals=0)},"
        f"{p_placeholder}"
        ")"
    )


class BinomialBereichsparameterGTRGenerator(TaskGenerator):
    generator_key = "stochastik.binomialverteilung.bereichsparameter_gtr"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]
            n, p = _sample_parameters(rng)
            p_percent = int(round(100 * p))

            exact_k = _bounded_int(rng, max(0, int(n * p * 0.75)), min(n, int(n * p * 1.25)))
            more_than_k = _bounded_int(rng, max(0, int(n * p * 0.75)), min(n - 1, int(n * p * 1.05)))
            at_most_k = _bounded_int(rng, max(0, int(n * p * 0.9)), min(n, int(n * p * 1.25)))

            lower_at_least = _bounded_int(rng, max(0, int(n * p * 0.65)), min(n - 2, int(n * p * 0.95)))
            upper_less_than = _bounded_int(
                rng,
                max(lower_at_least + 2, int(n * p * 1.02)),
                min(n + 1, int(n * p * 1.4) + 1),
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

            intro = join_sentences(
                rng.choice(
                    sample_probability_intro_variants(
                        scenario=scenario,
                        n=n,
                        p_text=f"{p_percent}%",
                    )
                ),
                "Bestimmen Sie zu den folgenden Ereignissen die Bernoulli-Parameter entsprechend der Eingabe im GTR.",
            )

            questions = [
                f"Von den {scenario.group_dative_plural} sind genau {exact_k} {scenario.success_plural}.",
                f"Von den {scenario.group_dative_plural} sind mehr als {more_than_k} {scenario.success_plural}.",
                f"Von den {scenario.group_dative_plural} sind höchstens {at_most_k} {scenario.success_plural}.",
                (
                    f"Von den {scenario.group_dative_plural} sind mindestens {lower_at_least} und weniger als "
                    f"{upper_less_than} {scenario.success_plural}."
                ),
                percent_question,
            ]

            answers = [
                _gtr_answer(a=exact_k, b=exact_k, n=n, p=p),
                _gtr_answer(
                    a=min_successes_for_more_than(more_than_k),
                    b=n,
                    n=n,
                    p=p,
                ),
                _gtr_answer(a=0, b=at_most_k, n=n, p=p),
                _gtr_answer(
                    a=min_successes_for_at_least(lower_at_least),
                    b=max_successes_for_less_than(upper_less_than),
                    n=n,
                    p=p,
                ),
                _gtr_answer(a=percent_a, b=percent_b, n=n, p=p),
            ]

            tasks.append(Task(einleitung=intro, fragen=questions, antworten=answers))

        return tasks

