"""Vier-Felder-Tafel vervollständigen - ohne Information zur stochastischen Unabhängigkeit.

3 Zellen der Tafel sind gegeben. Muster (5 mögliche Kombinationstypen):

  1. {1oder2oder3oder4} UND {5oder6} UND {7oder8}
       -> eine Innenzelle + eine Spalten-Randwkt + eine Zeilen-Randwkt
  2. beliebige 3 von {1,2,3,4}
       -> drei der vier Schnittwahrscheinlichkeiten
  3. [1∩4 ODER 2∩3] UND eines aus {5,6,7,8}
       -> Diagonalpaar + eine Randwkt
  4. [1∩2 ODER 3∩4] UND eines aus {7,8}
       -> vollständige Zeile + Zeilen-Randwkt
  5. [1∩3 ODER 2∩4] UND eines aus {5,6}
       -> vollständige Spalte + Spalten-Randwkt

Slot-Nummerierung:
  1 = P(A∩B)   2 = P(A∩¬B)   3 = P(¬A∩B)   4 = P(¬A∩¬B)
  5 = P(A)     6 = P(¬A)      7 = P(B)     8 = P(¬B)
"""

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_analysis_calc, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.methoden.shared import sample_ab_case, vft_slots
from aufgaben.generators.stochastik.methoden.textbausteine import SCENARIOS


def _pick_given_slots(rng: random.Random) -> list[int]:
    pattern = rng.randint(1, 5)
    if pattern == 1:
        return [rng.choice([1, 2, 3, 4]), rng.choice([5, 6]), rng.choice([7, 8])]
    elif pattern == 2:
        inner = [1, 2, 3, 4]
        rng.shuffle(inner)
        return inner[:3]
    elif pattern == 3:
        diag = rng.choice([[1, 4], [2, 3]])
        extra = rng.choice([5, 6, 7, 8])
        return diag + [extra]
    elif pattern == 4:
        row = rng.choice([[1, 2], [3, 4]])
        extra = rng.choice([7, 8])
        return row + [extra]
    else:  # pattern == 5
        col = rng.choice([[1, 3], [2, 4]])
        extra = rng.choice([5, 6])
        return col + [extra]


class MethodenVierfelderErstellenOhneUnabhGenerator(TaskGenerator):
    generator_key = "stochastik.methoden.vierfelder_erstellen_ohneUnabh"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]
            case = sample_ab_case(rng=rng, scenario=scenario)
            slots = vft_slots(case)
            given_slots = _pick_given_slots(rng)
            given_set = set(given_slots)

            intro = (
                f"<p>{scenario.intro}</p>"
                f"<p>$A$: {scenario.event_a}<br>"
                f"$B$: {scenario.event_b}</p>"
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


