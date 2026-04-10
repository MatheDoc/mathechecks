import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.lineare_algebra.matrizenrechnung.shared import (
    entry_questions, mat_mul, matrix_to_latex, random_matrix,
)


class MatrizenmultiplikationGenerator(TaskGenerator):
    generator_key = "lineare_algebra.matrizenrechnung.matrizenmultiplikation"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen: set[tuple] = set()
        dims = [2, 3, 4]

        for _ in range(count):
            for _ in range(300):
                m = rng.choice(dims)
                n = rng.choice(dims)
                p = rng.choice(dims)

                A = random_matrix(rng, m, n)
                B = random_matrix(rng, n, p)
                C = mat_mul(A, B)

                sig = (tuple(tuple(r) for r in A), tuple(tuple(r) for r in B))
                if sig in seen:
                    continue
                seen.add(sig)

                a_latex = matrix_to_latex(A)
                b_latex = matrix_to_latex(B)

                einleitung = (
                    f"Gegeben sind die Matrizen "
                    f"$$ A = {a_latex}, \\quad B = {b_latex} $$ "
                    f"Berechne $ A \\cdot B $."
                )

                fragen, antworten = entry_questions(C)
                tasks.append(Task(
                    einleitung=einleitung,
                    fragen=fragen,
                    antworten=antworten,
                ))
                break
            else:
                raise ValueError(
                    "Konnte keine weitere Aufgabe fuer Matrizenmultiplikation erzeugen."
                )

        return tasks
