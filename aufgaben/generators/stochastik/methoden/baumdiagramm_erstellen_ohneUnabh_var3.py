"""Check 3 - Baumdiagramm vervollständigen (Pfadadditionsregel).

Gegeben sind immer genau 3 Wahrscheinlichkeiten:
  1. Beide Endwkt eines Astes: {7,8} oder {9,10}
  2. Eine weitere Wkt aus dem anderen Ast:
    wenn {7,8} -> {5, 6, 9, 10};  wenn {9,10} -> {3, 4, 7, 8}

Lösungsweg: Pfadaddition -> P(A) = P(A∩B) + P(A∩¬B) bzw. P(¬A) analog,
danach Komplementregel + ggf. umgestellte Pfadmultiplikation.
"""

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_analysis_calc, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.methoden.shared import ABCase, sample_ab_case
from aufgaben.generators.stochastik.methoden.textbausteine import SCENARIOS


def _slot_probabilities(case: ABCase) -> dict[int, float]:
    return {
        1: case.p_a,
        2: case.p_not_a,
        3: case.p_b_given_a,
        4: case.p_not_b_given_a,
        5: case.p_b_given_not_a,
        6: case.p_not_b_given_not_a,
        7: case.p_a_and_b,
        8: case.p_a_and_not_b,
        9: case.p_not_a_and_b,
        10: case.p_not_a_and_not_b,
    }


def _build_tree_visual(case: ABCase, given_slots: list[int]) -> dict:
    return {
        "type": "plot",
        "spec": {
            "type": "ab-tree",
            "pa": case.p_a,
            "pba": case.p_b_given_a,
            "pbna": case.p_b_given_not_a,
            "givenSlots": sorted(given_slots),
        },
    }


# ---------------------------------------------------------------------------
# 8 Kombinationen: beide Endwkt eines Astes + 1 Wkt anderer Ast
# ---------------------------------------------------------------------------
_PATTERNS: list[set[int]] = []

# A-Ast komplett (7,8) + eine Wkt vom ¬A-Ast
for _other in (5, 6, 9, 10):
    _PATTERNS.append({7, 8, _other})

# ¬A-Ast komplett (9,10) + eine Wkt vom A-Ast
for _other in (3, 4, 7, 8):
    _PATTERNS.append({9, 10, _other})


class MethodenBaumdiagrammErstellenOhneUnabhVar3Generator(TaskGenerator):
    generator_key = "stochastik.methoden.baumdiagramm_erstellen_ohneUnabh_var3"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]
            case = sample_ab_case(rng=rng, scenario=scenario)
            slot_probs = _slot_probabilities(case)

            given_slots = rng.choice(_PATTERNS)

            intro = (
                f"<p>{scenario.intro}</p>"
                f"<p>\\(A\\): {scenario.event_a}<br>"
                f"\\(B\\): {scenario.event_b}</p>"
                "<p>Vervollständigen Sie das Baumdiagramm (auf 4 NKS gerundet).</p>"
            )

            fragen = ["" for _ in range(10)]
            antworten = [
                "---"
                if idx in given_slots
                else numerical_stochastik_calc(slot_probs[idx])
                for idx in range(1, 11)
            ]

            tasks.append(
                Task(
                    einleitung=intro,
                    fragen=fragen,
                    antworten=antworten,
                    visual=_build_tree_visual(case, list(given_slots)),
                )
            )

        return tasks


