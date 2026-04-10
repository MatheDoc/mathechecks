import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.lineare_algebra.matrizenrechnung.shared import (
    det_nxn, matrix_to_latex, numerical_int,
)


def _random_4x4_with_zeros(rng: random.Random, min_zeros: int = 4) -> list[list[int]]:
    entries = [rng.randint(-6, 6) for _ in range(16)]
    zero_positions = rng.sample(range(16), k=rng.randint(min_zeros, 7))
    for pos in zero_positions:
        entries[pos] = 0
    return [entries[i * 4:(i + 1) * 4] for i in range(4)]


class Determinante4x4Generator(TaskGenerator):
    generator_key = "lineare_algebra.matrizenrechnung.determinante_4x4"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen: set[tuple] = set()

        for _ in range(count):
            for _ in range(300):
                A = _random_4x4_with_zeros(rng)

                sig = tuple(tuple(r) for r in A)
                if sig in seen:
                    continue
                seen.add(sig)

                det_val = det_nxn(A)
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
                    "Konnte keine weitere Aufgabe fuer Determinante 4x4 erzeugen."
                )

        return tasks
