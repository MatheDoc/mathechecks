import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.methoden.shared import ABCase, sample_ab_case
from aufgaben.generators.stochastik.methoden.textbausteine import SCENARIOS


def _slot_probabilities(case: ABCase) -> dict[int, float]:
    """Kanonische Slot-Zuordnung 1..10 auf die 10 Baumwahrscheinlichkeiten."""
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
    """Kompakter ab-tree Spec – Rendering erfolgt clientseitig in preview.js."""
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


class MethodenBaumdiagrammCheck1Generator(TaskGenerator):
    generator_key = "stochastik.methoden.baumdiagramm_check1"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]
            case = sample_ab_case(rng=rng, scenario=scenario)
            slot_probs = _slot_probabilities(case)

            given_slots = {
                rng.choice([1, 2]),
                rng.choice([3, 4]),
                rng.choice([5, 6]),
            }

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
                else numerical(slot_probs[idx], tolerance=0.0001, decimals=4)
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
