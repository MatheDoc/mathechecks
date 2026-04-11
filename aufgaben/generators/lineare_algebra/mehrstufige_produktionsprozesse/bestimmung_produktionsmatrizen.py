"""Check 3: Bestimmung von Produktionsmatrizen.

Zwei der drei Matrizen RZ, ZE, RE sind gegeben.
Die fehlende dritte soll berechnet werden.

Fälle:
  RE gesucht  → RE = RZ · ZE                   (immer möglich)
  RZ gesucht  → RZ = RE · ZE⁻¹                 (ZE invertierbar)
  ZE gesucht  → ZE = RZ⁻¹ · RE                 (RZ invertierbar)
"""

import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.lineare_algebra.mehrstufige_produktionsprozesse.mpp_shared import (
    antwort_matrix,
    einleitung_matrizen,
    erzeuge_mpp_triple,
    var_matrix_latex,
)


class BestimmungProduktionsmatrizenGenerator(TaskGenerator):
    generator_key = (
        "lineare_algebra.mehrstufige_produktionsprozesse"
        ".bestimmung_produktionsmatrizen"
    )

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen: set[tuple] = set()

        for _ in range(count):
            for _ in range(300):
                # Zufällig wählen, welche Matrix gesucht ist
                gesucht = rng.choice(["RE", "RZ", "ZE"])

                if gesucht == "RE":
                    brauche_inv = None
                elif gesucht == "RZ":
                    brauche_inv = "ZE"
                else:  # ZE
                    brauche_inv = "RZ"

                result = erzeuge_mpp_triple(rng, brauche_inv=brauche_inv)
                if result is None:
                    continue
                nR, nZ, nE, rz, ze, re = result

                sig = (
                    tuple(tuple(r) for r in rz),
                    tuple(tuple(r) for r in ze),
                    gesucht,
                )
                if sig in seen:
                    continue
                seen.add(sig)

                # Gegebene Matrizen in der Einleitung
                if gesucht == "RE":
                    teile = {"RZ": rz, "ZE": ze}
                    gesuchte_matrix = re
                    name = "RE"
                    rows, cols = nR, nE
                elif gesucht == "RZ":
                    teile = {"ZE": ze, "RE": re}
                    gesuchte_matrix = rz
                    name = "RZ"
                    rows, cols = nR, nZ
                else:  # ZE
                    teile = {"RZ": rz, "RE": re}
                    gesuchte_matrix = ze
                    name = "ZE"
                    rows, cols = nZ, nE

                einleitung = einleitung_matrizen(teile)

                frage = (
                    f"Berechnen Sie "
                    f"{var_matrix_latex(name, rows, cols)}."
                )
                antwort = antwort_matrix(gesuchte_matrix)

                tasks.append(Task(
                    einleitung=einleitung,
                    fragen=[frage],
                    antworten=[antwort],
                ))
                break
            else:
                raise ValueError(
                    "Konnte keine weitere Aufgabe für Bestimmung Produktionsmatrizen erzeugen."
                )

        return tasks
