"""Check 2 (bedingte-wahrscheinlichkeiten) - Baumdiagramm vervollständigen mit Unabhängigkeit.

Kernidee: A und B sind stochastisch unabhängig, d. h. P(B|A) = P(B|¬A) = P(B).
Der vollständige Baum ist daher aus P(A) und P(B) bestimmbar.

Als Hilfestellung wird nur der Hinweis zur stochastischen Unabhängigkeit gegeben
sowie genau 2 Wahrscheinlichkeiten aus folgenden Kombinationen:

  Fall 1: 1 oder 2  + beliebige aus {3,4,5,6,7,8,9,10}
  Fall 2: 3,4,5 oder 6 + beliebige aus {1,2,7,8,9,10}
  Fall 3: 7 -> {1..6, 8, 9};  8 -> {1..6, 7, 10}
  Fall 4: 9 -> {1..6, 7, 10}; 10 -> {1..6, 8, 9}

Insgesamt 36 eindeutige Kombinationen (ungeordnete Paare).
"""

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.methoden.shared import ABCase, ab_intro, sample_ab_case_independent
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
# 36 eindeutige Kombinationen (ungeordnete Paare)
# ---------------------------------------------------------------------------
_seen: set[frozenset[int]] = set()
_PATTERNS: list[frozenset[int]] = []


def _add(a: int, b: int) -> None:
    p = frozenset({a, b})
    if p not in _seen:
        _seen.add(p)
        _PATTERNS.append(p)


# Fall 1: Anker 1 oder 2 + beliebig aus {3..10}
for _anchor in (1, 2):
    for _other in range(3, 11):
        _add(_anchor, _other)

# Fall 2: Anker 3,4,5,6 + beliebig aus {1,2,7,8,9,10}
for _anchor in (3, 4, 5, 6):
    for _other in (1, 2, 7, 8, 9, 10):
        _add(_anchor, _other)

# Fall 3: Anker 7 -> {1..6,8,9}; Anker 8 -> {1..6,7,10}
for _other in (1, 2, 3, 4, 5, 6, 8, 9):
    _add(7, _other)
for _other in (1, 2, 3, 4, 5, 6, 7, 10):
    _add(8, _other)

# Fall 4: Anker 9 -> {1..6,7,10}; Anker 10 -> {1..6,8,9}
for _other in (1, 2, 3, 4, 5, 6, 7, 10):
    _add(9, _other)
for _other in (1, 2, 3, 4, 5, 6, 8, 9):
    _add(10, _other)

del _seen, _anchor, _other


class MethodenBaumdiagrammErstellenMitUnabhGenerator(TaskGenerator):
    generator_key = "stochastik.methoden.baumdiagramm_erstellen_mit_unabh"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]
            case = sample_ab_case_independent(rng=rng, scenario=scenario)
            slot_probs = _slot_probabilities(case)

            given_slots = rng.choice(_PATTERNS)

            independence_clause = (
                scenario.independence_claim
                if scenario.independence_claim
                else "$A$ und $B$ sind stochastisch unabhängig."
            )

            intro = (
                ab_intro(scenario)
                + independence_clause
                + "Vervollständigen Sie das Baumdiagramm (auf 4 NKS gerundet)."
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

