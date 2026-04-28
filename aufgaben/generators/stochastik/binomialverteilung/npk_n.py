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


def _search_solution(
    kind: str,
    p: float,
    k: int,
    comparator: str,
    alpha: float,
    n_min: int,
    n_max: int,
    objective: str,
) -> int | None:
    candidates: list[int] = []
    for n in range(n_min, n_max + 1):
        value = _prob_event(kind=kind, n=n, p=p, k=k)
        if comparator == "ge" and value >= alpha:
            candidates.append(n)
        elif comparator == "le" and value <= alpha:
            candidates.append(n)
    if not candidates:
        return None
    return min(candidates) if objective == "min" else max(candidates)


def _random_percent_phrase(p: float) -> str:
    pct = int(round(p * 100))
    return f"{pct}%"


def _build_intro(
    rng: random.Random,
    intro_prefix: str,
    success_event_accusative: str,
    success_plural: str,
    group_dative_plural: str,
    p: float,
) -> str:
    p_text = _random_percent_phrase(p)
    variants = [
        f"{intro_prefix} Die Wahrscheinlichkeit für {success_event_accusative} beträgt {p_text}.",
        f"{intro_prefix} Die Wahrscheinlichkeit, {success_event_accusative} anzutreffen, liegt bei {p_text}.",
        f"{intro_prefix} Unter den {group_dative_plural} liegt die Wahrscheinlichkeit, {success_event_accusative} anzutreffen, bei {p_text}.",
    ]
    return rng.choice(variants)


def _build_question(
    rng: random.Random,
    sample_object_plural: str,
    objective: str,
    event_phrase: str,
    comp_text: str,
) -> str:
    if objective == "min":
        quantity_text = "mindestens untersucht werden müssen"
    else:
        quantity_text = "höchstens untersucht werden dürfen"

    variants = [
        (
            f"Bestimmen Sie, wie viele {sample_object_plural} {quantity_text}, damit die Wahrscheinlichkeit, "
            f"{event_phrase}, {comp_text} beträgt."
        ),
        (
            f"Bestimmen Sie, wie viele {sample_object_plural} {quantity_text}, sodass die Wahrscheinlichkeit, "
            f"{event_phrase}, {comp_text} beträgt."
        ),
    ]
    return rng.choice(variants)


class BinomialNpkNGenerator(TaskGenerator):
    generator_key = "stochastik.binomialverteilung.npk_n"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]

            for _ in range(300):
                target_n = rng.randint(95, 290)
                p = rng.choice([x / 100 for x in range(20, 81)])
                kind = rng.choice(["at_least", "at_most"])

                center = int(round(target_n * p))
                if kind == "at_least":
                    k = max(8, min(target_n - 4, center + rng.randint(-12, 10)))
                    comparator = rng.choice(["ge", "le"])
                else:
                    k = max(6, min(target_n - 6, center + rng.randint(-10, 12)))
                    comparator = rng.choice(["ge", "le"])

                if kind == "at_least" and comparator == "ge":
                    objective = "min"
                elif kind == "at_least" and comparator == "le":
                    objective = "max"
                elif kind == "at_most" and comparator == "le":
                    objective = "min"
                else:
                    objective = "max"

                value_here = _prob_event(kind=kind, n=target_n, p=p, k=k)
                alpha_percent = int(round(value_here * 100))
                alpha_percent = max(12, min(88, alpha_percent))
                alpha = alpha_percent / 100

                solved = _search_solution(
                    kind=kind,
                    p=p,
                    k=k,
                    comparator=comparator,
                    alpha=alpha,
                    n_min=max(k + 2, 30),
                    n_max=320,
                    objective=objective,
                )
                if solved != target_n:
                    continue

                if kind == "at_least":
                    event_phrase = f"in der Stichprobe mindestens {k} {scenario.success_plural} zu beobachten"
                else:
                    event_phrase = f"in der Stichprobe höchstens {k} {scenario.success_plural} zu beobachten"

                if comparator == "ge":
                    comp_text = f"mindestens {alpha_percent}%"
                else:
                    comp_text = f"höchstens {alpha_percent}%"

                intro = _build_intro(
                    rng=rng,
                    intro_prefix=scenario.intro_prefix,
                    success_event_accusative=scenario.success_event_accusative,
                    success_plural=scenario.success_plural,
                    group_dative_plural=scenario.group_dative_plural,
                    p=p,
                )

                question = _build_question(
                    rng=rng,
                    sample_object_plural=scenario.sample_object_plural,
                    objective=objective,
                    event_phrase=event_phrase,
                    comp_text=comp_text,
                )

                tasks.append(
                    Task(
                        einleitung=intro,
                        fragen=[question],
                        antworten=[numerical(target_n, tolerance=0, decimals=0)],
                    )
                )
                break
            else:
                raise ValueError("Konnte keine eindeutige npk-n Aufgabe erzeugen.")

        return tasks

