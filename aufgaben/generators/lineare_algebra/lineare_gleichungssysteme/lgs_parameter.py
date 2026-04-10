"""Check 4: Mehrdeutig lösbare LGS (3×3 mit Parameterlösung).

Erzeugt 3×3-LGS mit Rang 2, die unendlich viele Lösungen besitzen.
Der Schüler setzt x₃ = t und bestimmt x₁ = a₁ + b₁·t, x₂ = a₂ + b₂·t.
Alle Koeffizienten sind ganzzahlig.
"""

import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator


def _numerical_int(value: int) -> str:
    return f"{{1:NUMERICAL:={value}:0}}"


def _term_tex(coeff: int, var: str, is_first: bool) -> str:
    """Einzelnen Term c·x_i als LaTeX-String formatieren."""
    if coeff == 0:
        return ""
    abs_c = abs(coeff)
    if is_first:
        if coeff == 1:
            return var
        if coeff == -1:
            return f"-{var}"
        return f"{coeff}{var}"
    sign = "+" if coeff > 0 else "-"
    if abs_c == 1:
        return f"{sign}{var}"
    return f"{sign}{abs_c}{var}"


def _equation_tex(coeffs: tuple, rhs: int) -> str:
    parts: list[str] = []
    for j, c in enumerate(coeffs):
        term = _term_tex(c, f"x_{{{j + 1}}}", len(parts) == 0)
        if term:
            parts.append(term)
    if not parts:
        parts.append("0")
    return "".join(parts) + f"&={rhs}"


class LgsParameterGenerator(TaskGenerator):
    generator_key = "lineare_algebra.lineare_gleichungssysteme.lgs_parameter"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        seen: set[tuple] = set()

        for _ in range(count):
            for _ in range(500):
                task = self._try_generate(rng, seen)
                if task is not None:
                    tasks.append(task)
                    break
            else:
                raise ValueError(
                    "Konnte keine weitere Aufgabe für LGS-Parameter erzeugen."
                )

        return tasks

    def _try_generate(
        self, rng: random.Random, seen: set[tuple]
    ) -> Task | None:
        # ---- Lösungskoeffizienten wählen ----
        # x₁ = a₁ + b₁·t,  x₂ = a₂ + b₂·t,  x₃ = t
        b1 = rng.choice([x for x in range(-3, 4) if x != 0])
        b2 = rng.choice([x for x in range(-3, 4) if x != 0])
        a1 = rng.randint(-6, 6)
        a2 = rng.randint(-6, 6)

        # ---- Echelon-Form konstruieren ----
        # Zeile 1: p·x₁ + q·x₂ + r·x₃ = d₁
        # Zeile 2:         s·x₂ + u·x₃ = d₂
        # Zeile 3:                    0 = 0
        p = rng.choice([-2, -1, 1, 1, 1, 2])
        q = rng.randint(-4, 4)
        s = rng.choice([-2, -1, 1, 1, -1, 2])

        r = -(p * b1 + q * b2)
        u = -(s * b2)
        d1 = p * a1 + q * a2
        d2 = s * a2

        if abs(r) > 9 or abs(u) > 9:
            return None
        if abs(d1) > 40 or abs(d2) > 40:
            return None

        # ---- Gauß "rückgängig machen" → Original-LGS ----
        alpha = rng.choice([x for x in range(-2, 3) if x != 0])
        beta = rng.choice([x for x in range(-2, 3) if x != 0])
        gamma = rng.choice([x for x in range(-2, 3) if x != 0])

        e_row1 = (p, q, r, d1)
        e_row2 = (0, s, u, d2)

        row1 = e_row1
        row2 = tuple(e_row2[i] + alpha * e_row1[i] for i in range(4))
        row3 = tuple(beta * e_row1[i] + gamma * e_row2[i] for i in range(4))

        rows = [row1, row2, row3]

        # Plausibilitätsfilter
        for row in rows:
            if any(abs(c) > 15 for c in row):
                return None
            if all(c == 0 for c in row[:3]):
                return None

        # Zeilen mischen
        rng.shuffle(rows)

        sig = tuple(rows[0] + rows[1] + rows[2])
        if sig in seen:
            return None
        seen.add(sig)

        # ---- LaTeX erzeugen ----
        eqs = [_equation_tex(row[:3], row[3]) for row in rows]
        lgs_tex = "\\\\".join(eqs) + "\\\\"
        frage = f"\\( \\begin{{align}}{lgs_tex} \\end{{align}} \\)"

        antwort = (
            f"\\( x_1=\\){_numerical_int(a1)}"
            f"\\( +\\){_numerical_int(b1)}"
            f"\\( \\cdot t \\quad x_2=\\){_numerical_int(a2)}"
            f"\\( +\\){_numerical_int(b2)}"
            f"\\( \\cdot t \\quad x_3=t \\)"
        )

        einleitung = (
            "Das folgende LGS hat unendlich viele Lösungen. "
            "Setzen Sie $x_3 = t$ mit $t \\in \\mathbb{R}$ und "
            "bestimmen Sie die Lösung in der Form "
            "$x_1 = a_1 + b_1 \\cdot t$ und "
            "$x_2 = a_2 + b_2 \\cdot t$."
        )

        return Task(
            einleitung=einleitung,
            fragen=[frage],
            antworten=[antwort],
        )
