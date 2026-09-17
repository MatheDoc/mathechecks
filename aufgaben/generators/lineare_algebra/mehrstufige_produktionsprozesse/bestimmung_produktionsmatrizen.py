"""Check 3: Bestimmung von Produktionsmatrizen.

Jede Aufgabe enthält drei Teilfragen mit jeweils zwei gegebenen Matrizen.
Mit jeweils neuen Matrizen ist einmal RE, einmal RZ und einmal ZE gesucht.

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
    erzeuge_mpp_triple,
    matrix_latex,
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
            fragen: list[str] = []
            antworten: list[str] = []
            for gesucht in ("RE", "RZ", "ZE"):
                if gesucht == "RE":
                    brauche_inv = None
                elif gesucht == "RZ":
                    brauche_inv = "ZE"
                else:  # ZE
                    brauche_inv = "RZ"

                for _ in range(300):
                    result = erzeuge_mpp_triple(rng, brauche_inv=brauche_inv)
                    if result is None:
                        continue
                    nR, nZ, nE, rz, ze, re = result

                    sig = (
                        tuple(tuple(row) for row in rz),
                        tuple(tuple(row) for row in ze),
                    )
                    if sig in seen:
                        continue
                    seen.add(sig)

                    if gesucht == "RE":
                        teile = {"RZ": rz, "ZE": ze}
                        gesuchte_matrix = re
                        rows, cols = nR, nE
                    elif gesucht == "RZ":
                        teile = {"ZE": ze, "RE": re}
                        gesuchte_matrix = rz
                        rows, cols = nR, nZ
                    else:  # ZE
                        teile = {"RZ": rz, "RE": re}
                        gesuchte_matrix = ze
                        rows, cols = nZ, nE

                    gegeben = r"\(;\quad\)".join(
                        matrix_latex(name, matrix)
                        for name, matrix in teile.items()
                    )
                    fragen.append(
                        f"Gegeben: {gegeben}.\n"
                        f"Gesucht: {var_matrix_latex(gesucht, rows, cols)}."
                    )
                    antworten.append(antwort_matrix(gesuchte_matrix))
                    break
                else:
                    raise ValueError(
                        "Konnte keine weitere Aufgabe für Bestimmung Produktionsmatrizen erzeugen."
                    )

            tasks.append(Task(
                einleitung="Berechnen Sie die fehlende Produktionsmatrix.",
                fragen=fragen,
                antworten=antworten,
            ))

        return tasks
