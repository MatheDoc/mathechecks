"""Generator 07 – Schnittpunkte (Parabel–Gerade und Parabel–Parabel)."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.quadratische_funktionen.shared import (
    A_VALUES_INT,
    display_eq,
    fmt,
    nf_latex,
)
from aufgaben.generators.analysis.lineare_funktionen.shared import (
    linear_latex,
)


class SchnittpunkteQuadGenerator(TaskGenerator):
    """Parabel–Gerade und Parabel–Parabel Schnittpunkte."""

    generator_key = "analysis.quadratische_funktionen.schnittpunkte_quad"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        # Ca. 50/50 Parabel-Gerade / Parabel-Parabel
        while len(tasks) < count:
            variant = rng.choice(["pg", "pp"])

            if variant == "pg":
                task = self._parabel_gerade(rng)
            else:
                task = self._parabel_parabel(rng)

            if task is not None:
                tasks.append(task)

        return tasks

    def _parabel_gerade(self, rng: random.Random) -> Task | None:
        """f(x)=ax²+bx+c, g(x)=mx+n, 2 ganzzahlige Schnittpunkte."""
        for _ in range(50):
            a = rng.choice(A_VALUES_INT)
            # 2 ganzzahlige Schnittstellen xs1, xs2
            xs1 = rng.randint(-5, 5)
            xs2 = rng.randint(-5, 5)
            if xs1 == xs2:
                continue

            # Gerade durch diese Punkte auf der Parabel
            m_g = rng.randint(-3, 3)
            n_g_val = rng.randint(-6, 6)

            # f(x) - g(x) = ax² + (b-m)x + (c-n) muss NS bei xs1, xs2 haben
            # Also: ax² + (b-m)x + (c-n) = a(x-xs1)(x-xs2)
            # b - m = -a(xs1+xs2)  →  b = m - a(xs1+xs2)
            # c - n = a·xs1·xs2   →  c = n + a·xs1·xs2
            b_f = m_g - a * (xs1 + xs2)
            c_f = n_g_val + a * xs1 * xs2

            if abs(b_f) > 16 or abs(c_f) > 25:
                continue

            # y-Koordinaten
            y1 = m_g * xs1 + n_g_val
            y2 = m_g * xs2 + n_g_val

            eq_f = nf_latex(float(a), float(b_f), float(c_f), name="f")
            eq_g = linear_latex(float(m_g), float(n_g_val), name="g")

            x_lo, x_hi = sorted([xs1, xs2])
            y_lo = y1 if xs1 <= xs2 else y2
            y_hi = y2 if xs1 <= xs2 else y1

            return Task(
                einleitung=(
                    f"Bestimmen Sie die Schnittpunkte von $ f $ und $ g $."
                    f"{display_eq(eq_f)}"
                    f"{display_eq(eq_g)}"
                    f"Geben Sie die Schnittpunkte nach aufsteigender "
                    f"$ x $-Koordinate geordnet an."
                ),
                fragen=[
                    "Schnittpunkt $ S_1 $",
                    "Schnittpunkt $ S_2 $",
                ],
                antworten=[
                    f"$ x = ${numerical_analysis_calc(x_lo)}$ y = ${numerical_analysis_calc(y_lo)}",
                    f"$ x = ${numerical_analysis_calc(x_hi)}$ y = ${numerical_analysis_calc(y_hi)}",
                ],
            )
        return None

    def _parabel_parabel(self, rng: random.Random) -> Task | None:
        """f(x)=a₁x²+b₁x+c₁, g(x)=a₂x²+b₂x+c₂, 2 ganzzahlige SP."""
        for _ in range(50):
            a1 = rng.choice(A_VALUES_INT)
            a2 = rng.choice(A_VALUES_INT)
            if a1 == a2:
                continue

            xs1 = rng.randint(-4, 4)
            xs2 = rng.randint(-4, 4)
            if xs1 == xs2:
                continue

            # f(x)-g(x) = (a1-a2)x² + (b1-b2)x + (c1-c2)
            # = (a1-a2)(x-xs1)(x-xs2)
            da = a1 - a2
            db = -da * (xs1 + xs2)
            dc = da * xs1 * xs2

            b2 = rng.randint(-4, 4)
            c2 = rng.randint(-6, 6)
            b1 = b2 + db
            c1 = c2 + dc

            if abs(b1) > 16 or abs(c1) > 25 or abs(b2) > 16 or abs(c2) > 25:
                continue

            y1 = a1 * xs1**2 + b1 * xs1 + c1
            y2 = a1 * xs2**2 + b1 * xs2 + c1

            eq_f = nf_latex(float(a1), float(b1), float(c1), name="f")
            eq_g = nf_latex(float(a2), float(b2), float(c2), name="g")

            x_lo, x_hi = sorted([xs1, xs2])
            y_lo = y1 if xs1 <= xs2 else y2
            y_hi = y2 if xs1 <= xs2 else y1

            return Task(
                einleitung=(
                    f"Bestimmen Sie die Schnittpunkte von $ f $ und $ g $."
                    f"{display_eq(eq_f)}"
                    f"{display_eq(eq_g)}"
                    f"Geben Sie die Schnittpunkte nach aufsteigender "
                    f"$ x $-Koordinate geordnet an."
                ),
                fragen=[
                    "Schnittpunkt $ S_1 $",
                    "Schnittpunkt $ S_2 $",
                ],
                antworten=[
                    f"$ x = ${numerical_analysis_calc(x_lo)}$ y = ${numerical_analysis_calc(y_lo)}",
                    f"$ x = ${numerical_analysis_calc(x_hi)}$ y = ${numerical_analysis_calc(y_hi)}",
                ],
            )
        return None
