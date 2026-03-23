"""Vier-Felder-Tafel vervollständigen �?" mit Hinweis zur stochastischen Unabhängigkeit.

Nur 2 Zellen der Tafel sind gegeben. Dank P(B|A) = P(B|¬A) = P(B) genügt das.

Muster (3 mögliche Kombinationstypen):

  1. eines von {[1,2], [3,4], [1,3], [2,4]}
       �?' vollständige Zeile oder Spalte der Innenzellen
  2. {5oder6} UND {7oder8}
       �?' je eine Randwahrscheinlichkeit
  3. {1oder2oder3oder4} UND {5oder6oder7oder8}
       �?' eine Innenzelle + eine Randwahrscheinlichkeit

Slot-Nummerierung:
  1 = P(A�^�B)   2 = P(A�^�B�")   3 = P(�?�^�B)   4 = P(�?�^�B�")
  5 = P(A)     6 = P(�?)      7 = P(B)     8 = P(B�")
"""

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_analysis_calc, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.methoden.shared import sample_ab_case_independent, vft_slots
from aufgaben.generators.stochastik.methoden.textbausteine import SCENARIOS


def _pick_given_slots(rng: random.Random) -> list[int]:
    pattern = rng.randint(1, 3)
    if pattern == 1:
        return list(rng.choice([[1, 2], [3, 4], [1, 3], [2, 4]]))
    elif pattern == 2:
        return [rng.choice([5, 6]), rng.choice([7, 8])]
    else:  # pattern == 3
        return [rng.choice([1, 2, 3, 4]), rng.choice([5, 6, 7, 8])]


class MethodenVierfelderErstellenInfoUnabhGenerator(TaskGenerator):
    generator_key = "stochastik.methoden.vierfelder_erstellen_mitUnabh"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]
            case = sample_ab_case_independent(rng=rng, scenario=scenario)
            slots = vft_slots(case)
            given_slots = _pick_given_slots(rng)
            given_set = set(given_slots)

            intro = (
                f"<p>{scenario.intro}</p>"
                f"<p>\\(A\\): {scenario.event_a}<br>"
                f"\\(B\\): {scenario.event_b}</p>"
                f"<p>Die Ereignisse \\(A\\) und \\(B\\) sind stochastisch unabhängig.</p>"
                "<p>Vervollständigen Sie (auf 4 NKS gerundet) die Vier-Felder-Tafel.</p>"
            )

            fragen = ["" for _ in range(8)]
            antworten = [
                "---" if idx in given_set
                else numerical_stochastik_calc(slots[idx])
                for idx in range(1, 9)
            ]

            tasks.append(
                Task(
                    einleitung=intro,
                    fragen=fragen,
                    antworten=antworten,
                    visual={
                        "type": "plot",
                        "spec": {
                            "type": "vft",
                            "slots": {str(k): v for k, v in slots.items()},
                            "givenSlots": sorted(given_slots),
                        },
                    },
                )
            )

        return tasks


