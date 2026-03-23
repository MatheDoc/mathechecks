"""Check 2 �?" Baumdiagramm vervollständigen (Pfadmultiplikation umgestellt).

Kernidee: Die Pfadmultiplikationsregel a·b = c kann *nicht* direkt
angewendet werden, sondern muss mindestens einmal nach b umgestellt
werden: b = c / a.

Gegeben sind immer genau 3 Wahrscheinlichkeiten:
  1. Eine Endwahrscheinlichkeit (Blatt): 7, 8, 9 oder 10
  2. Eine Wkt aus demselben Ast:
       wenn 7|8 �?' {1, 3, 4};  wenn 9|10 �?' {2, 5, 6}
  3. Eine Wkt aus dem anderen Ast:
       wenn 7|8 �?' {5, 6, 9, 10};  wenn 9|10 �?' {3, 4, 7, 8}

Damit ist der gesamte Baum bestimmbar (7 Werte zu berechnen).
"""

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_stochastik_calc
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
# 48 Kombinationen: 1 Endwkt + 1 gleicher Ast + 1 anderer Ast
# ---------------------------------------------------------------------------
_PATTERNS: list[set[int]] = []

# Endwkt aus A-Ast (7 oder 8)
for _end in (7, 8):
    for _same in (1, 3, 4):
        for _other in (5, 6, 9, 10):
            _PATTERNS.append({_end, _same, _other})

# Endwkt aus ¬A-Ast (9 oder 10)
for _end in (9, 10):
    for _same in (2, 5, 6):
        for _other in (3, 4, 7, 8):
            _PATTERNS.append({_end, _same, _other})


class MethodenBaumdiagrammErstellenOhneUnabhVar2Generator(TaskGenerator):
    generator_key = "stochastik.methoden.baumdiagramm_erstellen_ohneUnabh_var2"

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

