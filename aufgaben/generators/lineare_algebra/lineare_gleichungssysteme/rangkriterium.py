import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc
from aufgaben.generators.base import TaskGenerator


def _numerical_int(value: int) -> str:
    return f"{{1:NUMERICAL:={value}:0}}"


def _random_non_zero_int(rng: random.Random) -> int:
    value = 0
    while value == 0:
        value = rng.randint(-9, 9)
    return value


def _build_case_sequence(count: int, rng: random.Random) -> list[str]:
    cases = ["keine_loesung", "eine_loesung", "unendlich_viele_loesungen"]
    base = count // len(cases)
    rest = count % len(cases)

    sequence: list[str] = []
    for index, case in enumerate(cases):
        amount = base + (1 if index < rest else 0)
        sequence.extend([case] * amount)

    rng.shuffle(sequence)
    return sequence


def _sample_dimensions(case: str, rng: random.Random) -> tuple[int, int]:
    candidates: list[tuple[int, int]] = []
    for rows in range(2, 5):
        for cols in range(2, 5):
            if case == "eine_loesung" and cols > rows:
                continue
            candidates.append((rows, cols))
    return rng.choice(candidates)


def _sample_rank_a(case: str, rows: int, cols: int, rng: random.Random) -> int:
    if case == "eine_loesung":
        return cols

    if case == "unendlich_viele_loesungen":
        max_rank = min(rows, cols - 1)
        return rng.randint(1, max_rank)

    max_rank = min(cols, rows - 1)
    return rng.randint(0, max_rank)


def _sample_pivot_columns(cols: int, rank_a: int, rng: random.Random) -> list[int]:
    if rank_a == 0:
        return []
    if rank_a == cols:
        return list(range(cols))
    return sorted(rng.sample(range(cols), k=rank_a))


def _build_echelon_augmented_matrix(
    rows: int,
    cols: int,
    rank_a: int,
    case: str,
    rng: random.Random,
) -> list[list[int]]:
    matrix: list[list[int]] = []
    pivot_columns = _sample_pivot_columns(cols=cols, rank_a=rank_a, rng=rng)

    for pivot_col in pivot_columns:
        row = [0] * (cols + 1)
        row[pivot_col] = _random_non_zero_int(rng)
        for col in range(pivot_col + 1, cols + 1):
            row[col] = rng.randint(-9, 9)
        matrix.append(row)

    remaining_rows = rows - len(matrix)

    if case == "keine_loesung":
        inconsistent_row = [0] * (cols + 1)
        inconsistent_row[-1] = _random_non_zero_int(rng)
        matrix.append(inconsistent_row)
        remaining_rows -= 1

    for _ in range(remaining_rows):
        matrix.append([0] * (cols + 1))

    return matrix


def _matrix_latex(matrix: list[list[int]], cols: int) -> str:
    col_spec = "c" * cols + "|c"
    row_texts = [" & ".join(str(value) for value in row) for row in matrix]
    rows_latex = r"\\".join(row_texts)
    return (
        r" \left(\begin{array}{"
        + col_spec
        + "}"
        + rows_latex
        + r"\end{array}\right) $$"
    )


def _solution_type_index(case: str) -> int:
    if case == "keine_loesung":
        return 0
    if case == "eine_loesung":
        return 1
    return 2


class LgsRangkriteriumGenerator(TaskGenerator):
    generator_key = "lineare_algebra.lineare_gleichungssysteme.rangkriterium"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen_signatures: set[tuple[tuple[int, ...], ...]] = set()

        case_sequence = _build_case_sequence(count=count, rng=rng)

        for case in case_sequence:
            for _ in range(300):
                rows, cols = _sample_dimensions(case=case, rng=rng)
                rank_a = _sample_rank_a(case=case, rows=rows, cols=cols, rng=rng)
                matrix = _build_echelon_augmented_matrix(
                    rows=rows,
                    cols=cols,
                    rank_a=rank_a,
                    case=case,
                    rng=rng,
                )

                signature = tuple(tuple(row) for row in matrix)
                if signature in seen_signatures:
                    continue
                seen_signatures.add(signature)

                rank_augmented = rank_a + 1 if case == "keine_loesung" else rank_a
                solution_answer = mc(
                    ["Keine Lösung", "eine Lösung", "unendlich viele Lösungen"],
                    correct_index=_solution_type_index(case),
                )

                tasks.append(
                    Task(
                        einleitung=(
                            "Gegeben ist die bereits in Zahlenstufenform vorliegende "
                            "erweiterte Koeffizientenmatrix $$(A|y)="
                            + _matrix_latex(matrix=matrix, cols=cols)
                        ),
                        fragen=[
                            "Bestimmen Sie den Rang von $A$.",
                            "Bestimmen Sie den Rang von $(A|y)$.",
                            "Bestimmen Sie $n$ (Anzahl der Unbekannten).",
                            "Folgerung zur Lösungsmenge:",
                        ],
                        antworten=[
                            _numerical_int(rank_a),
                            _numerical_int(rank_augmented),
                            _numerical_int(cols),
                            solution_answer,
                        ],
                    )
                )
                break
            else:
                raise ValueError("Konnte keine weitere passende Matrix fuer das Rangkriterium erzeugen.")

        return tasks
