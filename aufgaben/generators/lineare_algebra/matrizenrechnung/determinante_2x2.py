import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.lineare_algebra.matrizenrechnung.shared import (
    det_2x2, matrix_to_latex, numerical_int, random_matrix,
)


class Determinante2x2Generator(TaskGenerator):
    generator_key = "lineare_algebra.matrizenrechnung.determinante_2x2"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen: set[tuple] = set()

        for _ in range(count):
            for _ in range(300):
                A = random_matrix(rng, 2, 2)

                sig = tuple(tuple(r) for r in A)
                if sig in seen:
                    continue
                seen.add(sig)

                det_val = det_2x2(A)
                a_latex = matrix_to_latex(A)

                einleitung = (
                    f"Berechne die Determinante der Matrix "
                    f"$$ A = {a_latex} $$"
                )

                tasks.append(Task(
                    einleitung=einleitung,
                    fragen=["$ \\det(A) = $"],
                    antworten=[numerical_int(det_val)],
                ))
                break
            else:
                raise ValueError(
                    "Konnte keine weitere Aufgabe fuer Determinante 2x2 erzeugen."
                )

        return tasks
