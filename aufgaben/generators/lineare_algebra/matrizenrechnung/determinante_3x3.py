import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.lineare_algebra.matrizenrechnung.shared import (
    det_3x3, matrix_to_latex, numerical_int, random_matrix,
)


class Determinante3x3Generator(TaskGenerator):
    generator_key = "lineare_algebra.matrizenrechnung.determinante_3x3"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen: set[tuple] = set()

        nonzero_target = count // 2

        for task_idx in range(count):
            want_nonzero = task_idx < nonzero_target

            for _ in range(300):
                A = random_matrix(rng, 3, 3)

                zero_count = sum(1 for row in A for v in row if v == 0)
                if zero_count > 4:
                    continue

                det_val = det_3x3(A)

                if want_nonzero and det_val == 0:
                    continue

                sig = tuple(tuple(r) for r in A)
                if sig in seen:
                    continue
                seen.add(sig)

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
                    "Konnte keine weitere Aufgabe fuer Determinante 3x3 erzeugen."
                )

        return tasks
