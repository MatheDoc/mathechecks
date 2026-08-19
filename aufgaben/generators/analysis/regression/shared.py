"""Gemeinsame Hilfsfunktionen für die Regressions-Generatoren.

Kernidee der "schönen Zahlen": Die Datenpunkte entstehen aus einem wahren
Polynom mit glatten Koeffizienten plus Abweichungen e_i, die orthogonal zu
allen Monomen bis zum Modellgrad sind (Summe e_i = 0, Summe x_i^k * e_i = 0).
Dann liefert die Regression exakt die wahren Koeffizienten zurück.
"""

import math
import random

from aufgaben.core.placeholders import numerical_analysis_calc


def fmt_number(value: float, max_decimals: int = 2) -> str:
    """Deutsche Zahldarstellung ohne überflüssige Nullen (Komma statt Punkt)."""
    rounded = round(float(value), max_decimals)
    text = f"{rounded:.{max_decimals}f}".rstrip("0").rstrip(".")
    if text in {"-0", ""}:
        text = "0"
    return text.replace(".", ",")


def make_table(
    x_values: list[float],
    y_values: list[float],
    x_label: str = "$ x $",
    y_label: str = "$ y $",
    max_decimals: int = 2,
) -> str:
    header = f"    <tr><td>{x_label}</td>" + "".join(
        f"<td>$ {fmt_number(x, max_decimals)} $</td>" for x in x_values
    ) + "</tr>"
    row = f"    <tr><td>{y_label}</td>" + "".join(
        f"<td>$ {fmt_number(y, max_decimals)} $</td>" for y in y_values
    ) + "</tr>"
    return f"<table class=\"TabelleEinleitung\">\n{header}\n{row}\n</table>"


def linear_stats(
    x_values: list[float], y_values: list[float]
) -> tuple[float, float, float, float, float, float]:
    """Liefert (x_mean, y_mean, s_xx, s_xy, m, b) der linearen Regression."""
    n = len(x_values)
    x_mean = sum(x_values) / n
    y_mean = sum(y_values) / n
    s_xx = sum((x - x_mean) ** 2 for x in x_values)
    s_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    m = s_xy / s_xx
    b = y_mean - m * x_mean
    return x_mean, y_mean, s_xx, s_xy, m, b


def solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
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


def power_sums(x_values: list[float], y_values: list[float], degree: int) -> tuple[list[float], list[float]]:
    """Summen für die Normalengleichungen: (Σx^0..Σx^(2d), Σy..Σx^d·y)."""
    x_pow = [sum(x ** power for x in x_values) for power in range(2 * degree + 1)]
    xy = [sum((x ** power) * y for x, y in zip(x_values, y_values)) for power in range(degree + 1)]
    return x_pow, xy


def polyfit(x_values: list[float], y_values: list[float], degree: int) -> list[float]:
    """Kleinste-Quadrate-Polynom über Normalengleichungen; Koeffizienten a_0..a_d."""
    size = degree + 1
    x_pow, xy = power_sums(x_values, y_values, degree)
    matrix = [[x_pow[row + col] for col in range(size)] for row in range(size)]
    return solve_linear_system(matrix, xy)


def poly_eval(coeffs_low_to_high: list[float], x: float) -> float:
    return sum(coeff * (x ** power) for power, coeff in enumerate(coeffs_low_to_high))


def fd_deviations(
    rng: random.Random,
    n: int,
    degree: int,
    scale_choices: list[float],
) -> list[float]:
    """Abweichungsvektor orthogonal zu allen Monomen bis `degree`.

    Voraussetzung: x-Werte bilden eine arithmetische Folge. Dann annulliert
    die (degree+1)-te finite Differenz jedes Polynom vom Grad <= degree.
    Es werden 1-2 verschobene, skalierte Differenzmuster überlagert.

    Sonderfall n == degree+1 (Minimalanzahl): Die Regression ist eine exakte
    Interpolation, es gibt keinen orthogonalen Abweichungsraum -> Nullvektor.
    Bei n == degree+2 existiert genau eine Abweichungsrichtung (das
    Differenzmuster ohne Verschiebung, z. B. (-1, 3, -3, 1) für degree=2).
    """
    order = degree + 1
    pattern = [((-1) ** j) * math.comb(order, j) for j in range(order + 1)]
    max_shift = n - len(pattern)
    if max_shift < 0:
        if n == degree + 1:
            return [0.0] * n
        raise ValueError("Zu wenige Datenpunkte für orthogonale Abweichungen.")

    while True:
        deviations = [0.0] * n
        copies = 1 if max_shift == 0 else rng.choice([1, 2])
        shifts = (
            [0] * copies
            if max_shift == 0
            else rng.sample(range(max_shift + 1), min(copies, max_shift + 1))
        )
        for shift in shifts:
            sign = rng.choice([-1, 1])
            scale = sign * rng.choice(scale_choices)
            for j, value in enumerate(pattern):
                deviations[shift + j] += scale * value
        if any(abs(d) > 1e-9 for d in deviations):
            return [round(d, 2) for d in deviations]


def triple_deviations(
    rng: random.Random,
    x_values: list[float],
    max_abs: float = 3.0,
    max_tries: int = 200,
) -> list[float]:
    """Abweichungen mit Σe=0 und Σx·e=0 für beliebige (auch ungleich verteilte) x.

    Konstruktion über Index-Tripel (i,j,k): e = λ·(x_j−x_k, x_k−x_i, x_i−x_j).
    Beide Orthogonalitätsbedingungen sind dann exakt erfüllt.
    """
    n = len(x_values)
    for _ in range(max_tries):
        deviations = [0.0] * n
        copies = rng.choice([1, 2])
        for _ in range(copies):
            i, j, k = sorted(rng.sample(range(n), 3))
            lam = rng.choice([-1.0, -0.5, 0.5, 1.0])
            deviations[i] += lam * (x_values[j] - x_values[k])
            deviations[j] += lam * (x_values[k] - x_values[i])
            deviations[k] += lam * (x_values[i] - x_values[j])
        if all(abs(d) <= max_abs for d in deviations) and any(abs(d) > 1e-9 for d in deviations):
            return [round(d, 2) for d in deviations]
    raise ValueError("Keine passenden Abweichungen gefunden.")


def r_squared(
    x_values: list[float],
    y_values: list[float],
    coeffs_low_to_high: list[float],
) -> float:
    """Bestimmtheitsmaß R² = 1 − SSE/SST des Polynomfits; 0.0 falls SST = 0."""
    n = len(y_values)
    y_mean = sum(y_values) / n
    sst = sum((y - y_mean) ** 2 for y in y_values)
    if sst < 1e-12:
        return 0.0
    sse = sum(
        (y - poly_eval(coeffs_low_to_high, x)) ** 2
        for x, y in zip(x_values, y_values)
    )
    return 1.0 - sse / sst


def model_plausible(
    x_values: list[float],
    y_values: list[float],
    coeffs_low_to_high: list[float],
    min_r2: float = 0.95,
) -> bool:
    """Annahmefilter: Die Punktwolke muss optisch zum Modellgrad passen.

    Kriterien:
    - SST > 0 (y-Werte nicht alle gleich),
    - Bestimmtheitsmaß R² = 1 − SSE/SST >= min_r2 (bei exakter
      Interpolation trivialerweise 1),
    - Formtreue (Grad >= 2): Die Spannweite des Leitterms a_d·x^d über den
      Datenpunkten beträgt mindestens die Hälfte der Spannweite des
      restlichen Polynomanteils. So ist die Krümmung (quadratisch) bzw. der
      kubische Verlauf im Datenbereich sichtbar und die Punkte wirken nicht
      wie eine Gerade bzw. Parabel niedrigeren Grades.
    """
    n = len(y_values)
    y_mean = sum(y_values) / n
    if sum((y - y_mean) ** 2 for y in y_values) < 1e-9:
        return False
    if r_squared(x_values, y_values, coeffs_low_to_high) < min_r2:
        return False
    degree = len(coeffs_low_to_high) - 1
    if degree >= 2:
        lead = [coeffs_low_to_high[degree] * (x ** degree) for x in x_values]
        rest = [poly_eval(coeffs_low_to_high[:degree], x) for x in x_values]
        lead_span = max(lead) - min(lead)
        rest_span = max(rest) - min(rest)
        if lead_span < 0.5 * rest_span:
            return False
    return True


def poly_function_answer(
    coeffs_low_to_high: list[float],
    var: str = "x",
    func_name: str = "f",
) -> str:
    """Antwortstring mit einem NUMERICAL-Feld je Koeffizient (höchster Grad zuerst)."""
    degree = len(coeffs_low_to_high) - 1
    parts: list[str] = [f"$ {func_name}({var}) = $"]
    for index in range(degree, -1, -1):
        coeff = coeffs_low_to_high[index]
        parts.append(numerical_analysis_calc(coeff))
        if index >= 2:
            parts.append(f"$ \\,{var}^{index} + $")
        elif index == 1:
            parts.append(f"$ \\,{var} + $")
    return "".join(parts)


def assert_fit_matches(
    x_values: list[float],
    y_values: list[float],
    coeffs_low_to_high: list[float],
) -> None:
    """Sicherung: Regression liefert exakt die konstruierten Koeffizienten."""
    fitted = polyfit(x_values, y_values, len(coeffs_low_to_high) - 1)
    for expected, actual in zip(coeffs_low_to_high, fitted):
        if abs(expected - actual) > 1e-6:
            raise ValueError(
                f"Regressionskoeffizienten weichen ab: erwartet {coeffs_low_to_high}, erhalten {fitted}"
            )
