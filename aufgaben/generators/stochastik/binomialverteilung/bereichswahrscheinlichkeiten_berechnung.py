import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_analysis_calc, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.shared import (
    max_successes_for_min_failure_percent,
    min_successes_for_max_failure_percent,
    percent_to_threshold_ceil,
    percent_to_threshold_floor,
    prob_at_least,
    prob_at_most_or_at_least,
    prob_between_open_closed,
    prob_exactly,
    prob_less_than,
    violates_probability_rounding_policy,
)
from aufgaben.generators.stochastik.binomialverteilung.textbausteine import SCENARIOS

def _round_rate_to_percent(p: float) -> int:
    return int(round(p * 100))


def _sample_parameters(rng: random.Random) -> tuple[int, float]:
    n = rng.randint(22, 95)
    p = rng.choice([x / 100 for x in range(18, 83)])
    return n, p


def _bounded_int(rng: random.Random, lower: int, upper: int) -> int:
    if upper <= lower:
        return lower
    return rng.randint(lower, upper)


class BinomialBereichswahrscheinlichkeitenBerechnungGenerator(TaskGenerator):
    generator_key = "stochastik.binomialverteilung.bereichswahrscheinlichkeiten_berechnung"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]
            for _ in range(200):
                n, p = _sample_parameters(rng)
                q = 1.0 - p
                p_pct = _round_rate_to_percent(p)

                exact_k = _bounded_int(rng, int(n * p * 0.75), int(n * p * 1.25))
                at_least_k = _bounded_int(rng, int(n * p * 0.8), int(n * p * 1.05))
                less_than_k = _bounded_int(rng, int(n * p * 0.95), int(n * p * 1.25))

                lower_open = _bounded_int(rng, int(n * p * 0.6), int(n * p * 0.95))
                upper_closed = _bounded_int(
                    rng,
                    max(lower_open + 2, int(n * p * 1.05)),
                    int(n * p * 1.35),
                )
                upper_closed = min(upper_closed, n)

                percent_mode_success = rng.choice([True, False])
                percent_direction_at_most = rng.choice([True, False])
                percent_value = _bounded_int(rng, 35, 72)

                if percent_mode_success:
                    if percent_direction_at_most:
                        percent_question = (
                            f"Von den {scenario.group_dative_plural} sind höchstens {percent_value}% "
                            f"{scenario.success_plural}."
                        )
                        percent_threshold = percent_to_threshold_floor(n=n, percent_value=percent_value)
                        percent_probability = prob_less_than(n=n, p=p, k=percent_threshold + 1)
                    else:
                        percent_question = (
                            f"Von den {scenario.group_dative_plural} sind mindestens {percent_value}% "
                            f"{scenario.success_plural}."
                        )
                        percent_threshold = percent_to_threshold_ceil(n=n, percent_value=percent_value)
                        percent_probability = prob_at_least(n=n, p=p, k=percent_threshold)
                else:
                    if percent_direction_at_most:
                        percent_question = (
                            f"Von den {scenario.group_dative_plural} sind höchstens {percent_value}% "
                            f"{scenario.failure_plural}."
                        )
                        success_threshold = min_successes_for_max_failure_percent(
                            n=n,
                            percent_value=percent_value,
                        )
                        percent_probability = prob_at_least(n=n, p=p, k=success_threshold)
                    else:
                        percent_question = (
                            f"Von den {scenario.group_dative_plural} sind mindestens {percent_value}% "
                            f"{scenario.failure_plural}."
                        )
                        success_threshold = max_successes_for_min_failure_percent(
                            n=n,
                            percent_value=percent_value,
                        )
                        percent_probability = prob_less_than(n=n, p=p, k=success_threshold + 1)

                union_left = _bounded_int(rng, int(n * p * 0.45), int(n * p * 0.85))
                union_right = _bounded_int(rng, max(union_left + 4, int(n * p * 1.1)), int(n * p * 1.45))
                union_right = min(union_right, n)

                edge_count = _bounded_int(rng, 2, 5)
                edge_is_first = rng.choice([True, False])
                edge_success = rng.choice([True, False])
                edge_word = "ersten" if edge_is_first else "letzten"
                edge_outcome = scenario.success_plural if edge_success else scenario.failure_plural

                exact_probability = prob_exactly(n=n, p=p, k=exact_k)
                at_least_probability = prob_at_least(n=n, p=p, k=at_least_k)
                less_than_probability = prob_less_than(n=n, p=p, k=less_than_k)
                interval_probability = prob_between_open_closed(
                    n=n,
                    p=p,
                    lower_open=lower_open,
                    upper_closed=upper_closed,
                )
                union_probability = prob_at_most_or_at_least(
                    n=n,
                    p=p,
                    at_most=union_left,
                    at_least=union_right,
                )
                edge_probability = (p if edge_success else q) ** edge_count

                probabilities = [
                    exact_probability,
                    at_least_probability,
                    less_than_probability,
                    interval_probability,
                    percent_probability,
                    union_probability,
                    edge_probability,
                ]
                if not violates_probability_rounding_policy(probabilities=probabilities, decimals=4):
                    break
            else:
                raise ValueError("Konnte keine plausiblen Wahrscheinlichkeiten erzeugen (0/1-Rundungsregel).")

            intro_variants = [
                (
                    f"{scenario.intro_prefix} Es werden {n} {scenario.sample_object_plural} betrachtet. "
                    f"Die Wahrscheinlichkeit f\u00fcr {scenario.success_event_accusative} betr\u00e4gt {p_pct}%."
                ),
                (
                    f"{scenario.intro_prefix} {n} {scenario.sample_object_plural} werden zuf\u00e4llig ausgew\u00e4hlt. "
                    f"Die Wahrscheinlichkeit, {scenario.success_event_accusative} anzutreffen, liegt bei {p_pct}%."
                ),
                (
                    f"{scenario.intro_prefix} In einer Stichprobe von {n} {scenario.sample_object_plural} "
                    f"tritt {scenario.success_event_accusative} mit einer Wahrscheinlichkeit von {p_pct}% auf."
                ),
            ]

            intro = (
                f"{rng.choice(intro_variants)}Bestimmen Sie die Wahrscheinlichkeiten der folgenden Ereignisse "
                "(auf 4 NKS gerundet)."
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
                (
                    f"Von den {scenario.group_dative_plural} sind höchstens {union_left} oder mindestens "
                    f"{union_right} {scenario.success_plural}."
                ),
                (
                    f"Von den {scenario.group_dative_plural} sind die {edge_word} {edge_count} "
                    f"{edge_outcome}."
                ),
            ]

            answers = [
                numerical_stochastik_calc(exact_probability),
                numerical_stochastik_calc(at_least_probability),
                numerical_stochastik_calc(less_than_probability),
                numerical_stochastik_calc(interval_probability),
                numerical_stochastik_calc(percent_probability),
                numerical_stochastik_calc(union_probability),
                numerical_stochastik_calc(edge_probability),
            ]

            tasks.append(Task(einleitung=intro, fragen=questions, antworten=answers))

        return tasks


