import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical
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
            f"{intro_prefix} In einer Stichprobe von {n} {sample_object_plural} "
            f"liegt die Wahrscheinlichkeit, {success_event_accusative} anzutreffen, bei {p_percent}%."
        ),
        (
            f"{intro_prefix} {n} {sample_object_plural} werden zufällig ausgewählt. "
            f"Mit einer Wahrscheinlichkeit von {p_percent}% tritt {success_event_accusative} auf."
        ),
    ]
    return rng.choice(variants)


def _build_question(
    rng: random.Random,
    amount_text: str,
    event_text: str,
    success_plural: str,
    comp_text: str,
    alpha_percent: int,
) -> str:
    modal = "muss" if amount_text == "mindestens" else "darf"
    variants = [
        (
            f"Bestimmen Sie den Schwellenwert k, der {amount_text} in der Stichprobe sein {modal}, damit die "
            f"Wahrscheinlichkeit für {event_text} {success_plural} {comp_text} {alpha_percent}% beträgt."
        ),
        (
            f"Geben Sie k so an, dass das Ereignis \"{event_text} {success_plural}\" mit einer Wahrscheinlichkeit von "
            f"{comp_text} {alpha_percent}% eintritt und k dabei {amount_text} ist."
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
                    amount_text = "höchstens"
                elif kind == "at_least" and comparator == "le":
                    objective = "min"
                    amount_text = "mindestens"
                elif kind == "at_most" and comparator == "ge":
                    objective = "min"
                    amount_text = "mindestens"
                else:
                    objective = "max"
                    amount_text = "höchstens"

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
                    event_text = "mindestens diese Anzahl"
                else:
                    event_text = "höchstens diese Anzahl"

                question = _build_question(
                    rng=rng,
                    amount_text=amount_text,
                    event_text=event_text,
                    success_plural=scenario.success_plural,
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
