import random
import math

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.shared_numbers import uniform_sig


def _fmt_number(value: float, decimals: int = 2) -> str:
    return f"{value:.{decimals}f}"


def _lineare_regression(x_values: list[float], y_values: list[float]) -> tuple[float, float]:
    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(y_values) / len(y_values)
    var_x = sum((x - x_mean) ** 2 for x in x_values)
    cov_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    m = cov_xy / var_x
    b = y_mean - m * x_mean
    return m, b


def _r2(y_true: list[float], y_pred: list[float]) -> float:
    y_mean = sum(y_true) / len(y_true)
    ss_res = sum((actual - pred) ** 2 for actual, pred in zip(y_true, y_pred))
    ss_tot = sum((actual - y_mean) ** 2 for actual in y_true)
    if ss_tot == 0:
        return 0.0
    return 1 - (ss_res / ss_tot)


def _solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    n = len(matrix)
    a = [row[:] + [vector[index]] for index, row in enumerate(matrix)]

    for pivot_index in range(n):
        pivot_row = max(range(pivot_index, n), key=lambda row: abs(a[row][pivot_index]))
        if abs(a[pivot_row][pivot_index]) < 1e-12:
            raise ValueError("Singuläres Gleichungssystem.")
        a[pivot_index], a[pivot_row] = a[pivot_row], a[pivot_index]

        pivot = a[pivot_index][pivot_index]
        for col in range(pivot_index, n + 1):
            a[pivot_index][col] /= pivot

        for row in range(n):
            if row == pivot_index:
                continue
            factor = a[row][pivot_index]
            for col in range(pivot_index, n + 1):
                a[row][col] -= factor * a[pivot_index][col]

    return [a[row][n] for row in range(n)]


def _polyfit(x_values: list[float], y_values: list[float], degree: int) -> list[float]:
    size = degree + 1
    sums = [sum(x ** power for x in x_values) for power in range(2 * degree + 1)]
    matrix = [[sums[row + col] for col in range(size)] for row in range(size)]
    vector = [sum(y * (x ** row) for x, y in zip(x_values, y_values)) for row in range(size)]
    coeffs_low_to_high = _solve_linear_system(matrix, vector)
    return list(reversed(coeffs_low_to_high))


def _predict_poly(coeffs: list[float], x_values: list[float]) -> list[float]:
    degree = len(coeffs) - 1
    predictions: list[float] = []
    for x in x_values:
        value = 0.0
        for index, coeff in enumerate(coeffs):
            power = degree - index
            value += coeff * (x ** power)
        predictions.append(value)
    return predictions


def _fit_exponential(x_values: list[float], y_values: list[float]) -> tuple[float, float]:
    log_y = [math.log(max(y, 1e-8)) for y in y_values]
    b, log_a = _lineare_regression(x_values, log_y)
    a = math.exp(log_a)
    return a, b


def _numerical_placeholder(value: float, tolerance: float, decimals: int) -> str:
    value_str = f"{value:.{decimals}f}"
    tol_str = f"{tolerance:.{decimals}f}"
    return f"{{1:NUMERICAL:={value_str}:{tol_str}}}"


def _antwort_regression(coeffs: list[float], art: str) -> str:
    if art == "linear":
        return (
            f"$ y = ${_numerical_placeholder(coeffs[0], 0.01, 2)}"
            f"$ x + ${_numerical_placeholder(coeffs[1], 0.01, 2)}"
        )
    if art == "quadratisch":
        return (
            f"$ y = ${_numerical_placeholder(coeffs[0], 0.01, 2)}"
            f"$ x^2 + ${_numerical_placeholder(coeffs[1], 0.01, 2)}"
            f"$ x + ${_numerical_placeholder(coeffs[2], 0.01, 2)}"
        )
    if art == "kubisch":
        return (
            f"$ y = ${_numerical_placeholder(coeffs[0], 0.01, 2)}"
            f"$ x^3 + ${_numerical_placeholder(coeffs[1], 0.01, 2)}"
            f"$ x^2 + ${_numerical_placeholder(coeffs[2], 0.01, 2)}"
            f"$ x + ${_numerical_placeholder(coeffs[3], 0.01, 2)}"
        )
    return (
        f"$ y = ${_numerical_placeholder(coeffs[0], 0.01, 2)}"
        f"$ \\cdot exp( ${_numerical_placeholder(coeffs[1], 0.01, 2)}$ x) $"
    )


def _make_table(x_values: list[float], y_values: list[float]) -> str:
    header = "    <tr><td>$ x $</td>" + "".join(
        f"<td>$ {_fmt_number(x, 2)} $</td>" for x in x_values
    ) + "</tr>"
    row = "    <tr><td>$ y $</td>" + "".join(
        f"<td>$ {_fmt_number(y, 2)} $</td>" for y in y_values
    ) + "</tr>"
    return f"<table class=\"TabelleEinleitung\">\n{header}\n{row}\n</table>"


class LinearRegressionGenerator(TaskGenerator):
    """Erzeugt Regressionsaufgaben (linear, quadratisch, kubisch, exponentiell)."""
    generator_key = "analysis.regression"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        typen = ["linear", "quadratisch", "kubisch", "exponentiell"]
        basis = count // len(typen)
        rest = count % len(typen)
        verteilung = {typ: basis for typ in typen}
        for index in range(rest):
            verteilung[typen[index]] += 1

        for art in typen:
            for _ in range(verteilung[art]):
                x_values = sorted(rng.sample(range(1, 21), 5))

                if art == "linear":
                    y_values = [
                        2.0 * x + 3.0 + uniform_sig(rng, -3.0, 3.0)
                        for x in x_values
                    ]
                    coeffs = list(_polyfit(x_values, y_values, degree=1))
                    y_pred = _predict_poly(coeffs, x_values)
                    r2 = _r2(y_values, y_pred)
                    frage_funktion = "Bestimmen Sie die lineare Regressionsfunktion."

                elif art == "quadratisch":
                    y_values = [
                        1.0 * (x ** 2) - 2.0 * x + 5.0 + uniform_sig(rng, -5.0, 5.0)
                        for x in x_values
                    ]
                    coeffs = list(_polyfit(x_values, y_values, degree=2))
                    y_pred = _predict_poly(coeffs, x_values)
                    r2 = _r2(y_values, y_pred)
                    frage_funktion = "Bestimmen Sie die quadratische Regressionsfunktion."

                elif art == "kubisch":
                    y_values = [
                        -0.5 * (x ** 3) + 2.0 * (x ** 2) - x + 4.0 + uniform_sig(rng, -7.0, 7.0)
                        for x in x_values
                    ]
                    coeffs = list(_polyfit(x_values, y_values, degree=3))
                    y_pred = _predict_poly(coeffs, x_values)
                    r2 = _r2(y_values, y_pred)
                    frage_funktion = "Bestimmen Sie die kubische Regressionsfunktion."

                else:
                    b_true = uniform_sig(rng, 0.08, 0.35)
                    log_a_true = uniform_sig(rng, 0.8, 2.0)
                    log_y = [
                        log_a_true + b_true * x + uniform_sig(rng, -0.2, 0.2)
                        for x in x_values
                    ]
                    y_values = [math.exp(value) for value in log_y]
                    a_fit, b_fit = _fit_exponential(x_values, y_values)
                    coeffs = [a_fit, b_fit]
                    log_y_pred = [math.log(a_fit) + b_fit * x for x in x_values]
                    r2 = _r2(log_y, log_y_pred)
                    frage_funktion = "Bestimmen Sie die exponentielle Regressionsfunktion."

                table = _make_table(x_values, y_values)
                antwort_funktion = _antwort_regression(coeffs, art=art)

                tasks.append(
                    Task(
                        einleitung=f"Gegeben sind die folgenden Wertepaare:{table}",
                        fragen=[
                            frage_funktion,
                            "Bestimmen Sie das Bestimmtheitsmaß $ R^2 $.",
                        ],
                        antworten=[
                            antwort_funktion,
                            f"$ R^2 = ${_numerical_placeholder(r2, 0.001, 3)}",
                        ],
                    )
                )

        return tasks
