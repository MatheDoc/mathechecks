import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.shared import binom_cdf, prob_at_least
from aufgaben.generators.stochastik.binomialverteilung.textbausteine import SCENARIOS


def _p_placeholder(value: float) -> str:
    p_text = f"{value:.2f}".replace(".", ",")
    return "{1:NUMERICAL:=" + p_text + ":0}"


def _build_intro(rng: random.Random, intro_prefix: str, n: int, sample_object_plural: str) -> str:
    variants = [
        f"{intro_prefix} Es werden insgesamt {n} {sample_object_plural} betrachtet.",
        f"{intro_prefix} Die Stichprobe umfasst {n} {sample_object_plural}.",
        f"{intro_prefix} {n} {sample_object_plural} werden zufällig ausgewählt und untersucht.",
    ]
    return rng.choice(variants)


def _build_question(rng: random.Random, amount_text: str, event_text: str, comp_text: str, alpha_percent: int, success_event_accusative: str) -> str:
    variants = [
        (
            f"Bestimmen Sie die Wahrscheinlichkeit p für {success_event_accusative}, die {amount_text}, damit die "
            f"Wahrscheinlichkeit für {event_text} {comp_text} {alpha_percent}% beträgt (auf 2 NKS gerundet)."
        ),
        (
            f"Geben Sie p so an (auf 2 NKS), dass das Ereignis \"{event_text}\" mit einer Wahrscheinlichkeit von "
            f"{comp_text} {alpha_percent}% eintritt und p dabei {amount_text}."
        ),
    ]
    return rng.choice(variants)


def _prob_event(kind: str, n: int, p: float, k: int) -> float:
    if kind == "at_least":
        return prob_at_least(n=n, p=p, k=k)
    return binom_cdf(n=n, p=p, k=k)


def _search_solution(
    kind: str,
    n: int,
    k: int,
    comparator: str,
    alpha: float,
    objective: str,
) -> float | None:
    grid = [x / 100 for x in range(5, 96)]
    candidates: list[float] = []
    for p in grid:
        value = _prob_event(kind=kind, n=n, p=p, k=k)
        if comparator == "ge" and value >= alpha:
            candidates.append(p)
        elif comparator == "le" and value <= alpha:
            candidates.append(p)
    if not candidates:
        return None
    return min(candidates) if objective == "min" else max(candidates)


class BinomialNpkPGenerator(TaskGenerator):
    generator_key = "stochastik.binomialverteilung.npk_p"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]

            for _ in range(300):
                n = rng.randint(100, 295)
                target_p = rng.choice([x / 100 for x in range(18, 82)])
                kind = rng.choice(["at_least", "at_most"])

                center = int(round(n * target_p))
                k = max(6, min(n - 6, center + rng.randint(-20, 20)))

                if kind == "at_least":
                    comparator = rng.choice(["ge", "le"])
                else:
                    comparator = rng.choice(["ge", "le"])

                if kind == "at_least" and comparator == "ge":
                    objective = "min"
                    amount_text = "mindestens sein muss"
                elif kind == "at_least" and comparator == "le":
                    objective = "max"
                    amount_text = "höchstens sein darf"
                elif kind == "at_most" and comparator == "le":
                    objective = "min"
                    amount_text = "mindestens sein muss"
                else:
                    objective = "max"
                    amount_text = "höchstens sein darf"

                value_here = _prob_event(kind=kind, n=n, p=target_p, k=k)
                alpha_percent = int(round(value_here * 100))
                alpha_percent = max(12, min(88, alpha_percent))
                alpha = alpha_percent / 100

                solved = _search_solution(
                    kind=kind,
                    n=n,
                    k=k,
                    comparator=comparator,
                    alpha=alpha,
                    objective=objective,
                )
                if solved is None or abs(solved - target_p) > 1e-12:
                    continue

                intro = _build_intro(
                    rng=rng,
                    intro_prefix=scenario.intro_prefix,
                    n=n,
                    sample_object_plural=scenario.sample_object_plural,
                )

                if kind == "at_least":
                    event_text = f"mindestens {k} {scenario.success_plural}"
                else:
                    event_text = f"höchstens {k} {scenario.success_plural}"

                comp_text = "mindestens" if comparator == "ge" else "höchstens"
                question = _build_question(
                    rng=rng,
                    amount_text=amount_text,
                    event_text=event_text,
                    comp_text=comp_text,
                    alpha_percent=alpha_percent,
                    success_event_accusative=scenario.success_event_accusative,
                )

                tasks.append(
                    Task(
                        einleitung=intro,
                        fragen=[question],
                        antworten=[_p_placeholder(target_p)],
                    )
                )
                break
            else:
                raise ValueError("Konnte keine eindeutige npk-p Aufgabe erzeugen.")

        return tasks
