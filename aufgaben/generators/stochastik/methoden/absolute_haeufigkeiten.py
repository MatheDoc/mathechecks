"""Generator fuer Aufgaben mit absoluten Haeufigkeiten im AB-Kontext.

Erzeugt JSON-Aufgaben fuer die Sammlung "absolute-haeufigkeiten".
Die Kontexte stammen aus textbausteine.py.
"""

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_analysis_calc, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.methoden.textbausteine import SCENARIOS


class AbsoluteHaeufigkeitenGenerator(TaskGenerator):
    generator_key = "stochastik.methoden.absolute_haeufigkeiten"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            scenario = SCENARIOS[index % len(SCENARIOS)]

            # Absolute Haeufigkeiten in den vier disjunkten Feldern der AB-Tafel
            c_pab = rng.randint(8, 95)
            c_panb = rng.randint(8, 95)
            c_pnab = rng.randint(8, 95)
            c_pnanb = rng.randint(8, 95)

            total = c_pab + c_panb + c_pnab + c_pnanb

            probs = {
                "pa": (c_pab + c_panb) / total,
                "pna": (c_pnab + c_pnanb) / total,
                "pb": (c_pab + c_pnab) / total,
                "pnb": (c_panb + c_pnanb) / total,
                "pab": c_pab / total,
                "panb": c_panb / total,
                "pnab": c_pnab / total,
                "pnanb": c_pnanb / total,
                "paub": (c_pab + c_panb + c_pnab) / total,
                "pnaub": (c_pnab + c_pnanb + c_pab) / total,
                "paunb": (c_pab + c_panb + c_pnanb) / total,
                "pnaunb": (c_pnab + c_pnanb + c_panb) / total,
            }

            if rng.choice([True, False]):
                question_keys = ["pa", "pna"]
                if rng.choice([True, False]):
                    question_keys.extend(["paub", "pnanb"])
                else:
                    question_keys.extend(["paunb", "pnab"])
            else:
                question_keys = ["pb", "pnb"]
                if rng.choice([True, False]):
                    question_keys.extend(["pnaub", "panb"])
                else:
                    question_keys.extend(["paub", "pnanb"])

            einleitung = (
                f"{scenario.intro} "
                f"In einer Erhebung wurden insgesamt {total} Faelle beobachtet: "
                f"{c_pab} Faelle, in denen {scenario.prob_texts['pab']}; "
                f"{c_panb} Faelle, in denen {scenario.prob_texts['panb']}; "
                f"{c_pnab} Faelle, in denen {scenario.prob_texts['pnab']}; "
                f"{c_pnanb} Faelle, in denen {scenario.prob_texts['pnanb']}. "
                "Berechnen Sie die Wahrscheinlichkeit der folgenden Ereignisse: Ein zufaellig ausgewaehlter Fall erfuellt"
            )

            fragen = [
                f"{scenario.prob_texts[k]}."
                for k in question_keys
            ]

            antworten = [
                numerical(probs[k], tolerance=0.001, decimals=4)
                for k in question_keys
            ]

            tasks.append(Task(einleitung=einleitung, fragen=fragen, antworten=antworten))

        return tasks

