import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _format_number,
    _num,
    _poly3_value,
    _sample_k3_cost_coefficients_from_exact_kennzahlen,
)


def _rank_of_matrix(rows: list[list[float]], eps: float = 1e-9) -> int:
    matrix = [row[:] for row in rows]
    if not matrix:
        return 0

    row_count = len(matrix)
    col_count = len(matrix[0])
    rank = 0
    pivot_row = 0

    for col in range(col_count):
        pivot = None
        for row in range(pivot_row, row_count):
            if abs(matrix[row][col]) > eps:
                pivot = row
                break
        if pivot is None:
            continue

        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        pivot_value = matrix[pivot_row][col]
        matrix[pivot_row] = [value / pivot_value for value in matrix[pivot_row]]

        for row in range(row_count):
            if row == pivot_row:
                continue
            factor = matrix[row][col]
            if abs(factor) <= eps:
                continue
            matrix[row] = [
                left - factor * right
                for left, right in zip(matrix[row], matrix[pivot_row])
            ]

        rank += 1
        pivot_row += 1
        if pivot_row == row_count:
            break

    return rank


class ErtragsgesetzlicheKostenSteckbriefK3Generator(TaskGenerator):
    """Erzeugt Steckbriefaufgaben für kubische ertragsgesetzliche Kostenfunktionen."""

    generator_key = "analysis.ertragsgesetzliche_kostenfunktionen.steckbrief_k3"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, float, float, float]] = set()

        for _ in range(count):
            while True:
                (
                    k3,
                    k2,
                    k1,
                    k0,
                    x_wende,
                    x_betriebsminimum,
                    x_betriebsoptimum,
                    kurzfristige_preisuntergrenze,
                    langfristige_preisuntergrenze,
                ) = _sample_k3_cost_coefficients_from_exact_kennzahlen(rng)

                coeff_key = (k3, k2, k1, k0)
                if coeff_key in used:
                    continue

                def kosten(x: float) -> float:
                    return _poly3_value(k3, k2, k1, k0, x)

                def stueckkosten(x: float) -> float:
                    return kosten(x) / x

                def var_stueckkosten(x: float) -> float:
                    return k3 * (x ** 2) + k2 * x + k1

                def grenzkosten(x: float) -> float:
                    return 3.0 * k3 * (x ** 2) + 2.0 * k2 * x + k1

                x_kosten = float(rng.randint(max(2, int(x_wende)), max(3, int(3 * x_wende))))
                x_stueck = float(rng.choice([2, 4, 5, 25]))
                x_var = float(rng.randint(max(2, int(x_wende)), max(3, int(3 * x_wende))))
                x_grenz = float(rng.randint(max(2, int(x_wende)), max(3, int(3 * x_wende))))

                clues: dict[int, tuple[str, list[float], float]] = {
                    0: (
                        f"Die Fixkosten betragen {_format_number(k0)} GE.",
                        [0.0, 0.0, 0.0, 1.0],
                        k0,
                    ),
                    1: (
                        f"Die Kosten bei {_format_number(x_kosten)} ME betragen {_format_number(kosten(x_kosten))} GE.",
                        [x_kosten ** 3, x_kosten ** 2, x_kosten, 1.0],
                        kosten(x_kosten),
                    ),
                    2: (
                        f"Die Stückkosten bei {_format_number(x_stueck)} ME betragen {_format_number(stueckkosten(x_stueck))} GE/ME.",
                        [x_stueck ** 2, x_stueck, 1.0, 1.0 / x_stueck],
                        stueckkosten(x_stueck),
                    ),
                    3: (
                        f"Die variablen Stückkosten bei {_format_number(x_var)} ME betragen {_format_number(var_stueckkosten(x_var))} GE/ME.",
                        [x_var ** 2, x_var, 1.0, 0.0],
                        var_stueckkosten(x_var),
                    ),
                    4: (
                        f"Die Grenzkosten bei {_format_number(x_grenz)} ME betragen {_format_number(grenzkosten(x_grenz))} GE/ME.",
                        [3.0 * (x_grenz ** 2), 2.0 * x_grenz, 1.0, 0.0],
                        grenzkosten(x_grenz),
                    ),
                    5: (
                        f"Der Übergang vom degressiven zum progressiven Kostenwachstum findet bei {_format_number(x_wende)} ME statt.",
                        [6.0 * x_wende, 2.0, 0.0, 0.0],
                        0.0,
                    ),
                    6: (
                        f"Das Betriebsminimum beträgt {_format_number(x_betriebsminimum)} ME.",
                        [2.0 * x_betriebsminimum, 1.0, 0.0, 0.0],
                        0.0,
                    ),
                    7: (
                        f"Das Betriebsoptimum beträgt {_format_number(x_betriebsoptimum)} ME.",
                        [2.0 * x_betriebsoptimum, 1.0, 0.0, -(1.0 / (x_betriebsoptimum ** 2))],
                        0.0,
                    ),
                    8: (
                        f"Die kurzfristige Preisuntergrenze beträgt {_format_number(kurzfristige_preisuntergrenze)} GE/ME.",
                        [
                            x_betriebsminimum ** 2,
                            x_betriebsminimum,
                            1.0,
                            0.0,
                        ],
                        kurzfristige_preisuntergrenze,
                    ),
                    9: (
                        f"Die langfristige Preisuntergrenze beträgt {_format_number(langfristige_preisuntergrenze)} GE/ME.",
                        [
                            x_betriebsoptimum ** 2,
                            x_betriebsoptimum,
                            1.0,
                            1.0 / x_betriebsoptimum,
                        ],
                        langfristige_preisuntergrenze,
                    ),
                }

                success = False
                for _selection_try in range(120):
                    selected = [
                        rng.randint(0, 1),
                        rng.randint(2, 3),
                        rng.randint(4, 7),
                    ]
                    if selected[2] in {4, 5}:
                        selected.append(rng.randint(6, 7))
                    elif selected[2] == 6:
                        selected.append(8)
                    else:
                        selected.append(9)

                    matrix = [clues[idx][1] for idx in selected]
                    if _rank_of_matrix(matrix) < 4:
                        continue

                    intro_parts = [clues[idx][0] for idx in selected]
                    success = True
                    break

                if not success:
                    continue

                used.add(coeff_key)

                intro = "Es liegen folgende Informationen vor:" + "".join(
                    f"</p> <p>{part}" for part in intro_parts
                )

                answer = (
                    "\\( K(x)= \\)"
                    f"{_num(k3)}"
                    "\\( x^3 \\)+"
                    f"{_num(k2)}"
                    "\\( x^2 \\)+"
                    f"{_num(k1)}"
                    "\\( x \\)+"
                    f"{_num(k0)}"
                )

                tasks.append(
                    Task(
                        einleitung=intro,
                        fragen=["Bestimmen Sie die kubische Kostenfunktion."],
                        antworten=[answer],
                    )
                )
                break

        return tasks
