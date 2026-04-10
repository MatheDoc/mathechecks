import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.lineare_algebra.matrizenrechnung.shared import (
    entry_questions, mat_add, mat_sub, matrix_to_latex, random_matrix,
    scalar_mul,
)

_DIMENSIONS = [(2, 2), (2, 3), (3, 2), (3, 3)]


def _build_operations():
    return [
        (
            r"A + B",
            lambda A, B, s: mat_add(A, B),
        ),
        (
            r"A - B",
            lambda A, B, s: mat_sub(A, B),
        ),
        (
            r"\lambda \cdot A",
            lambda A, B, s: scalar_mul(s, A),
        ),
        (
            r"\lambda \cdot (A + B)",
            lambda A, B, s: scalar_mul(s, mat_add(A, B)),
        ),
        (
            r"\lambda \cdot A + B",
            lambda A, B, s: mat_add(scalar_mul(s, A), B),
        ),
        (
            r"A - \lambda \cdot B",
            lambda A, B, s: mat_sub(A, scalar_mul(s, B)),
        ),
        (
            r"\lambda \cdot (A - B) + A",
            lambda A, B, s: mat_add(scalar_mul(s, mat_sub(A, B)), A),
        ),
        (
            r"\lambda \cdot A - B",
            lambda A, B, s: mat_sub(scalar_mul(s, A), B),
        ),
        (
            r"A + \lambda \cdot B",
            lambda A, B, s: mat_add(A, scalar_mul(s, B)),
        ),
    ]


class AddSubSkalarGenerator(TaskGenerator):
    generator_key = "lineare_algebra.matrizenrechnung.addition_subtraktion_skalarmultiplikation"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen: set[tuple] = set()
        operations = _build_operations()

        for _ in range(count):
            for _ in range(300):
                rows, cols = rng.choice(_DIMENSIONS)
                A = random_matrix(rng, rows, cols)
                B = random_matrix(rng, rows, cols)
                scalars = [v for v in range(-5, 6) if v not in (0, 1)]
                lam = rng.choice(scalars)

                op_label, op_func = rng.choice(operations)
                result = op_func(A, B, lam)

                sig = (op_label, tuple(tuple(r) for r in A),
                       tuple(tuple(r) for r in B), lam)
                if sig in seen:
                    continue
                seen.add(sig)

                a_latex = matrix_to_latex(A)
                b_latex = matrix_to_latex(B)

                einleitung = (
                    f"Gegeben sind die Matrizen "
                    f"$$ A = {a_latex}, \\quad B = {b_latex} $$ "
                    f"und der Skalar $ \\lambda = {lam} $. "
                    f"Berechne $ {op_label} $."
                )

                fragen, antworten = entry_questions(result)
                tasks.append(Task(
                    einleitung=einleitung,
                    fragen=fragen,
                    antworten=antworten,
                ))
                break
            else:
                raise ValueError(
                    "Konnte keine weitere Aufgabe fuer Addition/Subtraktion/Skalarmultiplikation erzeugen."
                )

        return tasks
