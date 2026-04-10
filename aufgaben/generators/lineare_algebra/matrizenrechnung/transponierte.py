import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.lineare_algebra.matrizenrechnung.shared import (
    entry_questions, matrix_to_latex, random_matrix, transpose,
)


class TransponierteGenerator(TaskGenerator):
    generator_key = "lineare_algebra.matrizenrechnung.transponierte"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen: set[tuple] = set()
        dims = [2, 3, 4]

        for _ in range(count):
            for _ in range(300):
                m = rng.choice(dims)
                n = rng.choice(dims)
                if rng.random() < 0.6 and m == n:
                    n = rng.choice([d for d in dims if d != m] or dims)

                A = random_matrix(rng, m, n)
                AT = transpose(A)

                sig = tuple(tuple(r) for r in A)
                if sig in seen:
                    continue
                seen.add(sig)

                a_latex = matrix_to_latex(A)
                einleitung = (
                    f"Bestimme die Transponierte $ A^T $ der Matrix "
                    f"$$ A = {a_latex} $$"
                )

                fragen, antworten = entry_questions(AT)
                tasks.append(Task(
                    einleitung=einleitung,
                    fragen=fragen,
                    antworten=antworten,
                ))
                break
            else:
                raise ValueError(
                    "Konnte keine weitere Aufgabe fuer Transponierte erzeugen."
                )

        return tasks
