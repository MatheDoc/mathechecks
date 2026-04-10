import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.lineare_algebra.matrizenrechnung.shared import (
    entry_questions, mat_add, mat_sub, mat_mul, matrix_to_latex, random_matrix,
)


def _random_invertible_2x2(rng: random.Random) -> list[list[int]]:
    for _ in range(200):
        a = [[1, 0], [0, 1]]
        for _ in range(rng.randint(3, 6)):
            k = rng.choice([-2, -1, 1, 2])
            if rng.random() < 0.5:
                a[1][0] += k * a[0][0]
                a[1][1] += k * a[0][1]
            else:
                a[0][0] += k * a[1][0]
                a[0][1] += k * a[1][1]
        if rng.random() < 0.5:
            a[0] = [-x for x in a[0]]
        if all(abs(a[i][j]) <= 9 for i in range(2) for j in range(2)):
            if not (a[0][0] == a[1][1] and a[0][1] == 0 and a[1][0] == 0):
                return a
    return [[1, 1], [0, 1]]


def _inverse_2x2_det1(a: list[list[int]]) -> list[list[int]]:
    det = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    return [[det * a[1][1], -det * a[0][1]],
            [-det * a[1][0], det * a[0][0]]]


# ---------------------------------------------------------------------------
#  Gleichungstypen
#  Jeder Typ liefert: (eq_latex, solution_latex, given_matrices_dict, X)
#  given_matrices_dict: {"A": matrix, "B": matrix, ...}
# ---------------------------------------------------------------------------

def _type_ax_eq_b(rng, A, A_inv, X):
    """A · X = B  =>  X = A⁻¹ · B"""
    B = mat_mul(A, X)
    return (r"A \cdot X = B",
            r"A^{-1} \cdot B",
            {"A": A, "B": B})


def _type_xa_eq_b(rng, A, A_inv, X):
    """X · A = B  =>  X = B · A⁻¹"""
    B = mat_mul(X, A)
    return (r"X \cdot A = B",
            r"B \cdot A^{-1}",
            {"A": A, "B": B})


def _type_ax_plus_b_eq_c(rng, A, A_inv, X):
    """A · X + B = C  =>  X = A⁻¹ · (C − B)"""
    B = random_matrix(rng, 2, 2, low=-5, high=5)
    AX = mat_mul(A, X)
    C = mat_add(AX, B)
    return (r"A \cdot X + B = C",
            r"A^{-1} \cdot (C - B)",
            {"A": A, "B": B, "C": C})


def _type_xa_plus_b_eq_c(rng, A, A_inv, X):
    """X · A + B = C  =>  X = (C − B) · A⁻¹"""
    B = random_matrix(rng, 2, 2, low=-5, high=5)
    XA = mat_mul(X, A)
    C = mat_add(XA, B)
    return (r"X \cdot A + B = C",
            r"(C - B) \cdot A^{-1}",
            {"A": A, "B": B, "C": C})


def _type_a_eq_b_minus_cx(rng, A, A_inv, X):
    """A = B − C · X  =>  X = C⁻¹ · (B − A)"""
    # Here C is the invertible matrix
    C = A
    B = mat_add(random_matrix(rng, 2, 2, low=-5, high=5),
                mat_mul(C, X))
    # verify: B - C·X should give our "A" matrix
    A_given = mat_sub(B, mat_mul(C, X))
    return (r"A = B - C \cdot X",
            r"C^{-1} \cdot (B - A)",
            {"A": A_given, "B": B, "C": C})


def _type_a_eq_b_minus_xc(rng, A, A_inv, X):
    """A = B − X · C  =>  X = (B − A) · C⁻¹"""
    C = A
    B = mat_add(random_matrix(rng, 2, 2, low=-5, high=5),
                mat_mul(X, C))
    A_given = mat_sub(B, mat_mul(X, C))
    return (r"A = B - X \cdot C",
            r"(B - A) \cdot C^{-1}",
            {"A": A_given, "B": B, "C": C})


def _type_a_bplusx_eq_c(rng, A, A_inv, X):
    """A · (B + X) = C  =>  X = A⁻¹ · C − B"""
    B = random_matrix(rng, 2, 2, low=-4, high=4)
    BplusX = mat_add(B, X)
    C = mat_mul(A, BplusX)
    return (r"A \cdot (B + X) = C",
            r"A^{-1} \cdot C - B",
            {"A": A, "B": B, "C": C})


def _type_xplusb_a_eq_c(rng, A, A_inv, X):
    """(X + B) · A = C  =>  X = C · A⁻¹ − B"""
    B = random_matrix(rng, 2, 2, low=-4, high=4)
    XplusB = mat_add(X, B)
    C = mat_mul(XplusB, A)
    return (r"(X + B) \cdot A = C",
            r"C \cdot A^{-1} - B",
            {"A": A, "B": B, "C": C})


_EQUATION_TYPES = [
    _type_ax_eq_b,
    _type_xa_eq_b,
    _type_ax_plus_b_eq_c,
    _type_xa_plus_b_eq_c,
    _type_a_eq_b_minus_cx,
    _type_a_eq_b_minus_xc,
    _type_a_bplusx_eq_c,
    _type_xplusb_a_eq_c,
]


def _build_distractors(correct: str, rng: random.Random) -> list[str]:
    """Build 3 plausible but wrong solution forms."""
    pool = [
        r"A^{-1} \cdot B",
        r"B \cdot A^{-1}",
        r"A^{-1} \cdot (C - B)",
        r"(C - B) \cdot A^{-1}",
        r"C^{-1} \cdot (B - A)",
        r"(B - A) \cdot C^{-1}",
        r"A^{-1} \cdot C - B",
        r"C \cdot A^{-1} - B",
        r"A^{-1} \cdot (B - C)",
        r"(B - C) \cdot A^{-1}",
        r"B \cdot A^{-1} - C",
        r"A^{-1} \cdot B - C",
    ]
    candidates = [d for d in pool if d != correct]
    rng.shuffle(candidates)
    return candidates[:3]


class MatrizengleichungenGenerator(TaskGenerator):
    generator_key = "lineare_algebra.matrizenrechnung.matrizengleichungen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen: set[tuple] = set()

        for _ in range(count):
            for _ in range(300):
                A = _random_invertible_2x2(rng)
                A_inv = _inverse_2x2_det1(A)
                X = random_matrix(rng, 2, 2, low=-5, high=5)

                eq_func = rng.choice(_EQUATION_TYPES)
                eq_latex, solution_latex, given = eq_func(rng, A, A_inv, X)

                # Check that all matrix entries stay reasonable
                all_entries = [v for mat in given.values()
                               for row in mat for v in row]
                if any(abs(v) > 30 for v in all_entries):
                    continue

                sig = (eq_latex,
                       tuple(tuple(r) for r in given.get("A", [[]])),
                       tuple(tuple(r) for r in given.get("B", [[]])),
                       tuple(tuple(r) for r in given.get("C", [[]])))
                if sig in seen:
                    continue
                seen.add(sig)

                # Build einleitung
                given_parts = ", \\quad ".join(
                    f"{name} = {matrix_to_latex(mat)}"
                    for name, mat in sorted(given.items())
                )
                einleitung = (
                    f"Löse die Matrizengleichung $ {eq_latex} $ "
                    f"nach $ X $ auf. "
                    f"$$ {given_parts} $$"
                )

                # Frage 1: MC for solution form
                distractors = _build_distractors(solution_latex, rng)
                options = distractors + [solution_latex]
                rng.shuffle(options)
                correct_idx = options.index(solution_latex)
                mc_options_formatted = [f"$ X = {o} $" for o in options]
                mc_answer = mc(mc_options_formatted, correct_idx)

                # Frage 2: Matrix entries
                entry_fragen, entry_antworten = entry_questions(X)

                fragen = [
                    f"Welche Gestalt hat $ X $?",
                    entry_fragen[0],
                ]
                antworten = [
                    mc_answer,
                    entry_antworten[0],
                ]

                tasks.append(Task(
                    einleitung=einleitung,
                    fragen=fragen,
                    antworten=antworten,
                ))
                break
            else:
                raise ValueError(
                    "Konnte keine weitere Aufgabe fuer Matrizengleichungen erzeugen."
                )

        return tasks
