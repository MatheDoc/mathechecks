"""Check 2: Matrizenelemente – Interpretation.

Drei Produktionsmatrizen RZ, ZE, RE sind gegeben. Die Schüler
beantworten drei Fragen zu einzelnen Elementen der Matrizen.
"""

import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.lineare_algebra.mehrstufige_produktionsprozesse.mpp_shared import (
    einleitung_matrizen,
    erzeuge_mpp_triple,
    numerical_int,
)

# Fragetexte pro Matrixtyp ─────────────────────────────────────────────────

_FRAGE_RZ = (
    "Bestimmen Sie die Anzahl der Mengeneinheiten von R{row}, "
    "die für Herstellung von einer Mengeneinheit von Z{col} nötig sind."
)

_FRAGE_ZE = (
    "Bestimmen Sie die Anzahl der Mengeneinheiten von Z{row}, "
    "die für Herstellung von einer Mengeneinheit von E{col} nötig sind."
)

_FRAGE_RE = (
    "Bestimmen Sie die Anzahl der Mengeneinheiten von R{row}, "
    "die für Herstellung von einer Mengeneinheit von E{col} nötig sind."
)


# ──────────────────────────────────────────────────────────────────────────

class MatrizenelementeInterpretationGenerator(TaskGenerator):
    generator_key = (
        "lineare_algebra.mehrstufige_produktionsprozesse"
        ".matrizenelemente_interpretation"
    )

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen: set[tuple] = set()

        for _ in range(count):
            for _ in range(300):
                result = erzeuge_mpp_triple(rng)
                if result is None:
                    continue
                nR, nZ, nE, rz, ze, re = result

                sig = (
                    tuple(tuple(r) for r in rz),
                    tuple(tuple(r) for r in ze),
                )
                if sig in seen:
                    continue

                # 3 Fragen: je eine zu RZ, ZE, RE (zufällige Reihenfolge)
                candidates = []

                # RZ-Fragen
                for i in range(nR):
                    for j in range(nZ):
                        candidates.append(("RZ", i, j, rz[i][j],
                                           _FRAGE_RZ.format(row=i + 1, col=j + 1)))
                # ZE-Fragen
                for i in range(nZ):
                    for j in range(nE):
                        candidates.append(("ZE", i, j, ze[i][j],
                                           _FRAGE_ZE.format(row=i + 1, col=j + 1)))
                # RE-Fragen
                for i in range(nR):
                    for j in range(nE):
                        candidates.append(("RE", i, j, re[i][j],
                                           _FRAGE_RE.format(row=i + 1, col=j + 1)))

                # Wähle je eine Frage pro Matrix
                rz_pool = [c for c in candidates if c[0] == "RZ"]
                ze_pool = [c for c in candidates if c[0] == "ZE"]
                re_pool = [c for c in candidates if c[0] == "RE"]

                chosen = [
                    rng.choice(rz_pool),
                    rng.choice(ze_pool),
                    rng.choice(re_pool),
                ]
                rng.shuffle(chosen)

                seen.add(sig)

                einleitung = einleitung_matrizen({
                    "RZ": rz, "ZE": ze, "RE": re,
                })

                fragen = [c[4] for c in chosen]
                antworten = [numerical_int(c[3]) for c in chosen]

                tasks.append(Task(
                    einleitung=einleitung,
                    fragen=fragen,
                    antworten=antworten,
                ))
                break
            else:
                raise ValueError(
                    "Konnte keine weitere Aufgabe für Matrizenelemente-Interpretation erzeugen."
                )

        return tasks
