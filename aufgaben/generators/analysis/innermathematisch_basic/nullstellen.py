import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc
from aufgaben.generators.base import TaskGenerator


def _linear_function_latex(a: int, b: int) -> str:
    if b < 0:
        return f"$ f(x)={a}x{b} $"
    return f"$ f(x)={a}x+{b} $"


def _signed_term(value: int, variable: str) -> str:
    if value == 0:
        return ""
    sign = "+" if value > 0 else "-"
    abs_value = abs(value)
    if abs_value == 1:
        return f"{sign}{variable}"
    return f"{sign}{abs_value}{variable}"


def _quadratic_function_latex(a: int, b: int, c: int) -> str:
    b_term = _signed_term(b, "x")
    if c > 0:
        c_term = f"+{c}"
    elif c < 0:
        c_term = str(c)
    else:
        c_term = ""
    return f"$ f(x)={a}x^2{b_term}{c_term} $"


class LinearNullstelleGenerator(TaskGenerator):
    """Erzeugt Aufgaben zur Nullstellenberechnung linearer Funktionen."""
    generator_key = "analysis.nullstellen.linear"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used_params: set[tuple[int, int]] = set()

        while len(tasks) < count:
            x0 = rng.randint(-12, 12)
            if x0 == 0:
                continue
            a = rng.choice([-1, 1]) * rng.randint(1, 8)
            b = -a * x0
            params = (a, b)
            if params in used_params:
                continue
            used_params.add(params)

            tasks.append(
                Task(
                    einleitung=f"Gegeben: {_linear_function_latex(a, b)}",
                    fragen=["Bestimmen Sie die Nullstelle der Funktion $ f $."],
                    antworten=[f"$x=${numerical_analysis_calc(x0)}"],
                )
            )

        return tasks


class QuadraticNullstelleGenerator(TaskGenerator):
    """Erzeugt Aufgaben zur Nullstellenberechnung quadratischer Funktionen."""
    generator_key = "analysis.nullstellen.quadratisch"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used_params: set[tuple[int, int, int]] = set()

        while len(tasks) < count:
            x1 = rng.randint(-10, 10)
            x2 = rng.randint(-10, 10)
            if x1 == x2:
                continue

            a = rng.choice([-1, 1]) * rng.randint(1, 4)
            b = -a * (x1 + x2)
            c = a * x1 * x2
            params = (a, b, c)
            if params in used_params:
                continue
            used_params.add(params)

            x_low = min(x1, x2)
            x_high = max(x1, x2)

            tasks.append(
                Task(
                    einleitung=f"Gegeben: {_quadratic_function_latex(a, b, c)}",
                    fragen=[
                        "Bestimmen Sie die Nullstellen der Funktion $ f $ und geben Sie sie in aufsteigender Reihenfolge an."
                    ],
                    antworten=[
                        "$x_1=$"
                        f"{numerical_analysis_calc(x_low)}"
                        "$,\\;x_2=$"
                        f"{numerical_analysis_calc(x_high)}"
                    ],
                )
            )

        return tasks

