import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.lineare_algebra.matrizenrechnung.shared import (
    entry_questions, inverse_nxn, matrix_to_latex, random_invertible,
)


class Inverse3x3Generator(TaskGenerator):
    generator_key = "lineare_algebra.matrizenrechnung.inverse_3x3"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen: set[tuple] = set()

        for _ in range(count):
            for _ in range(300):
                A = random_invertible(rng, 3, max_entry=9, steps_range=(5, 9), max_zeros=1)

                sig = tuple(tuple(r) for r in A)
                if sig in seen:
                    continue
                seen.add(sig)

                A_inv = inverse_nxn(A)

                # Reject if inverse entries get too large
                if any(abs(A_inv[i][j]) > 15 for i in range(3) for j in range(3)):
                    continue

                einleitung = (
                    f"Gegeben: $ A = {matrix_to_latex(A)} $"
                )

                fragen = [
                    "Bestimme die inverse Matrix "
                    f"$ A^{{-1}} = {_var_matrix_latex(3)} $."
                ]
                _, antworten = entry_questions(A_inv)

                tasks.append(Task(
                    einleitung=einleitung,
                    fragen=fragen,
                    antworten=antworten,
                ))
                break
            else:
                raise ValueError("Konnte keine weitere Aufgabe fuer Inverse 3x3 erzeugen.")

        return tasks


def _var_matrix_latex(n: int) -> str:
    names = [chr(ord("a") + i) for i in range(n * n)]
    rows = []
    for i in range(n):
        rows.append(" & ".join(names[i * n:(i + 1) * n]))
    return r"\begin{pmatrix} " + r" \\ ".join(rows) + r" \end{pmatrix}"
