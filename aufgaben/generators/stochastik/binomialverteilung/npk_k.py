import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_analysis_calc, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.shared import binom_cdf, prob_at_least
from aufgaben.generators.stochastik.binomialverteilung.textbausteine import SCENARIOS


def _prob_event(kind: str, n: int, p: float, k: int) -> float:
    if kind == "at_least":
        return prob_at_least(n=n, p=p, k=k)
    return binom_cdf(n=n, p=p, k=k)


def _build_intro(
    rng: random.Random,
    intro_prefix: str,
    n: int,
    sample_object_plural: str,
    success_event_accusative: str,
    p_percent: int,
) -> str:
    variants = [
        (
            f"{intro_prefix} Es werden {n} {sample_object_plural} betrachtet. "
            f"Die Wahrscheinlichkeit für {success_event_accusative} beträgt {p_percent}%."
        ),
        (
            f"{intro_prefix} Die Stichprobe umfasst {n} {sample_object_plural}. "
            f"Dabei liegt die Wahrscheinlichkeit, {success_event_accusative} anzutreffen, bei {p_percent}%."
        ),
        (
            f"{intro_prefix} {n} {sample_object_plural} werden zufällig ausgewählt. "
            f"Für jedes einzelne Element der Stichprobe beträgt die Wahrscheinlichkeit für {success_event_accusative} {p_percent}%."
        ),
    ]
    return rng.choice(variants)


def _build_question(
    rng: random.Random,
    event_phrase: str,
    objective: str,
    comp_text: str,
    alpha_percent: int,
) -> str:
    threshold_text = "kleinsten" if objective == "min" else "größten"
    variants = [
        (
            f"Bestimmen Sie den {threshold_text} Wert von k, für den die Wahrscheinlichkeit, {event_phrase}, "
            f"{comp_text} {alpha_percent}% beträgt."
        ),
        (
            f"Bestimmen Sie den {threshold_text} Schwellenwert k, sodass die Wahrscheinlichkeit, {event_phrase}, "
            f"{comp_text} {alpha_percent}% beträgt."
        ),
    ]
    return rng.choice(variants)


def _search_solution(
    kind: str,
    n: int,
    p: float,
    comparator: str,
    alpha: float,
    objective: str,
) -> int | None:
    candidates: list[int] = []
    for k in range(0, n + 1):
        value = _prob_event(kind=kind, n=n, p=p, k=k)
        if comparator == "ge" and value >= alpha:
            candidates.append(k)
        elif comparator == "le" and value <= alpha:
            candidates.append(k)
    if not candidates:
        return None
    return min(candidates) if objective == "min" else max(candidates)


class BinomialNpkKGenerator(TaskGenerator):
    generator_key = "stochastik.binomialverteilung.npk_k"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]

            for _ in range(300):
                n = rng.randint(110, 290)
                p = rng.choice([x / 100 for x in range(20, 81)])
                kind = rng.choice(["at_least", "at_most"])
                target_k = max(6, min(n - 6, int(round(n * p)) + rng.randint(-15, 15)))

                comparator = rng.choice(["ge", "le"])

                if kind == "at_least" and comparator == "ge":
                    objective = "max"
                elif kind == "at_least" and comparator == "le":
                    objective = "min"
                elif kind == "at_most" and comparator == "ge":
                    objective = "min"
                else:
                    objective = "max"

                value_here = _prob_event(kind=kind, n=n, p=p, k=target_k)
                alpha_percent = int(round(value_here * 100))
                alpha_percent = max(12, min(88, alpha_percent))
                alpha = alpha_percent / 100

                solved = _search_solution(
                    kind=kind,
                    n=n,
                    p=p,
                    comparator=comparator,
                    alpha=alpha,
                    objective=objective,
                )
                if solved != target_k:
                    continue

                p_percent = int(round(100 * p))
                intro = _build_intro(
                    rng=rng,
                    intro_prefix=scenario.intro_prefix,
                    n=n,
                    sample_object_plural=scenario.sample_object_plural,
                    success_event_accusative=scenario.success_event_accusative,
                    p_percent=p_percent,
                )

                comp_text = "mindestens" if comparator == "ge" else "höchstens"
                if kind == "at_least":
                    event_phrase = f"in der Stichprobe mindestens k {scenario.success_plural} zu beobachten"
                else:
                    event_phrase = f"in der Stichprobe höchstens k {scenario.success_plural} zu beobachten"

                question = _build_question(
                    rng=rng,
                    event_phrase=event_phrase,
                    objective=objective,
                    comp_text=comp_text,
                    alpha_percent=alpha_percent,
                )

                tasks.append(
                    Task(
                        einleitung=intro,
                        fragen=[question],
                        antworten=[numerical(target_k, tolerance=0, decimals=0)],
                    )
                )
                break
            else:
                raise ValueError("Konnte keine eindeutige npk-k Aufgabe erzeugen.")

        return tasks

