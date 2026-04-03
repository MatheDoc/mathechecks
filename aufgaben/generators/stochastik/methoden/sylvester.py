"""Generator fuer Kontextaufgaben mit zwei Ereignissen A und B (Sammlung "sylvester").

Die Kontexte stammen aus textbausteine.py, die Wahrscheinlichkeiten aus shared.py.
"""

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_analysis_calc, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.methoden.shared import ab_intro, extended_probs, sample_ab_case
from aufgaben.generators.stochastik.methoden.textbausteine import SCENARIOS


_LATEX = {
    "pa": r"P(A)",
    "pna": r"P(\overline{A})",
    "pb": r"P(B)",
    "pnb": r"P(\overline{B})",
    "pab": r"P(A\cap B)",
    "paub": r"P(A\cup B)",
}

_ANCHOR3_OPTS = [
    ("pa", "pb", "pab"),
    ("pa", "pb", "paub"),
    ("pa", "pab", "paub"),
    ("pb", "pab", "paub"),
]

_QUESTION_PAIRS = [
    ("pnb", "paub"),
    ("pna", "pab"),
    ("pnb", "pab"),
    ("pna", "pb"),
]


def _latex_decimal(value: float) -> str:
    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return text.replace(".", "{,}")


def _percent_text(value: float) -> str:
    text = f"{value * 100:.2f}".rstrip("0").rstrip(".")
    return text.replace(".", ",") + "%"


def _given_text(key: str, value: float, scenario, rng: random.Random) -> str:
    if rng.random() < 0.4:
        return f"die Wahrscheinlichkeit, dass {scenario.prob_texts[key]}, {_percent_text(value)} betraegt"
    return f"$ {_LATEX[key]} $$ = $$ {_latex_decimal(value)} $"


def _question_text(key: str, scenario, rng: random.Random) -> str:
    if rng.random() < 0.5:
        return f"die Wahrscheinlichkeit, dass {scenario.prob_texts[key]}."
    return f"$ {_LATEX[key]} $."


class SylvesterGenerator(TaskGenerator):
    generator_key = "stochastik.methoden.sylvester"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]
            case = sample_ab_case(rng=rng, scenario=scenario)
            probs = extended_probs(case)

            anchor_keys = rng.choice(_ANCHOR3_OPTS)
            g0 = _given_text(anchor_keys[0], probs[anchor_keys[0]], scenario, rng)
            g1 = _given_text(anchor_keys[1], probs[anchor_keys[1]], scenario, rng)
            g2 = _given_text(anchor_keys[2], probs[anchor_keys[2]], scenario, rng)

            q1, q2 = rng.choice(_QUESTION_PAIRS)

            einleitung = (
                ab_intro(scenario)
                + f"Es ist bekannt, dass {g0}, dass {g1} und dass {g2}. "
                "Berechnen Sie (auf 4 NKS gerundet)"
            )

            fragen = [
                _question_text(q1, scenario, rng),
                _question_text(q2, scenario, rng),
            ]
            antworten = [
                numerical_stochastik_calc(probs[q1]),
                numerical_stochastik_calc(probs[q2]),
            ]

            tasks.append(Task(einleitung=einleitung, fragen=fragen, antworten=antworten))

        return tasks


