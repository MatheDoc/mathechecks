"""Gemeinsame Hilfsfunktionen für Generatoren zur Differentialrechnung ganzrationaler Funktionen."""

from __future__ import annotations

from dataclasses import dataclass
import math
import random

from aufgaben.core.latex import coeff_latex, const_latex, display_eq, fmt
from aufgaben.core.placeholders import numerical_analysis_calc
from aufgaben.core.tolerances import axis_tick_step


LEADING_VALUES = (-2.0, -1.0, -0.5, 0.5, 1.0, 2.0)
NONZERO_SMALL_VALUES = (-4.0, -3.0, -2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0)
CONTROLLED_CUBIC_LEADING_VALUES = (-1.0, -0.5, 0.5, 1.0)
GRAPH_COLORS = ("#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#8c564b")
GRAPH_LABELS = ("a", "b", "c", "d")
_WIDE_CENTER_VALUES = tuple(range(-6, 7))
_CONTROLLED_CUBIC_CENTER_VALUES = tuple(range(-5, 6))
_WIDE_DOMAIN_MIN = -9
_WIDE_DOMAIN_MAX = 9


def _visual_coeff(value: float) -> float:
    rounded = round(float(value), 6)
    return 0.0 if abs(rounded) < 1e-12 else rounded


@dataclass(frozen=True)
class PolynomialCase:
    coeffs: tuple[float, ...]

    def __post_init__(self) -> None:
        normalized = [float(value) for value in self.coeffs]
        while len(normalized) > 1 and abs(normalized[0]) < 1e-12:
            normalized.pop(0)
        if not normalized:
            normalized = [0.0]
        object.__setattr__(self, "coeffs", tuple(normalized))

    @property
    def degree(self) -> int:
        return len(self.coeffs) - 1

    def evaluate(self, x_value: float) -> float:
        result = 0.0
        for coefficient in self.coeffs:
            result = result * x_value + coefficient
        if abs(result) < 1e-12:
            result = 0.0
        return float(result)

    def derivative(self, order: int = 1) -> "PolynomialCase":
        if order < 0:
            raise ValueError("order must be >= 0")

        coeffs = list(self.coeffs)
        for _ in range(order):
            degree = len(coeffs) - 1
            if degree <= 0:
                coeffs = [0.0]
                break
            coeffs = [coeffs[index] * (degree - index) for index in range(degree)]
        return PolynomialCase(tuple(coeffs))

    def derivative_value(self, x_value: float, order: int = 1) -> float:
        return self.derivative(order=order).evaluate(x_value)

    def signature(self) -> tuple[float, ...]:
        return tuple(round(value, 6) for value in self.coeffs)


def align_equations(expressions: list[str]) -> str:
    lines: list[str] = []
    for expression in expressions:
        cleaned = expression.strip().rstrip(".")
        if "=" in cleaned:
            left, right = cleaned.split("=", 1)
            lines.append(f"{left}&={right}")
        else:
            lines.append(cleaned)
    joined = r" \\ ".join(lines)
    return f"$$ \\begin{{align*}} {joined} \\end{{align*}} $$"


def polynomial_latex(case: PolynomialCase | tuple[float, ...], name: str = "f", var: str = "x") -> str:
    poly = case if isinstance(case, PolynomialCase) else PolynomialCase(case)
    parts: list[str] = []
    degree = poly.degree

    for index, coefficient in enumerate(poly.coeffs):
        if abs(coefficient) < 1e-12:
            continue
        power = degree - index
        leading = not parts
        if power == 0:
            if leading:
                part = fmt(coefficient) if coefficient >= 0 else f"-{fmt(abs(coefficient))}"
            else:
                part = const_latex(coefficient)
        elif power == 1:
            part = coeff_latex(coefficient, var, leading=leading)
        else:
            part = coeff_latex(coefficient, f"{var}^{power}", leading=leading)
        parts.append(part)

    expression = "".join(parts) if parts else "0"
    return f"{name}({var})={expression}"


def factor_form_latex(scale: float, roots: tuple[float, ...], name: str = "f", var: str = "x") -> str:
    if abs(scale - 1.0) < 1e-12:
        scale_str = ""
    elif abs(scale + 1.0) < 1e-12:
        scale_str = "-"
    else:
        scale_str = fmt(scale)

    factors = "".join(_linear_factor(var, root) for root in roots)
    return f"{name}({var})={scale_str}{factors}"


def polynomial_input_answer(case: PolynomialCase | tuple[float, ...], name: str = "f'", var: str = "x") -> str:
    poly = case if isinstance(case, PolynomialCase) else PolynomialCase(case)
    pieces: list[str] = []
    degree = poly.degree

    for index, coefficient in enumerate(poly.coeffs):
        placeholder = numerical_analysis_calc(float(coefficient))
        power = degree - index
        if power >= 2:
            pieces.append(f"{placeholder}$ {var}^{power} $")
        elif power == 1:
            pieces.append(f"{placeholder}$ {var} $")
        else:
            pieces.append(f"{placeholder}")

    if not pieces:
        pieces = [numerical_analysis_calc(0.0)]

    return f"$ {name}({var})= $" + " + ".join(pieces)


def coefficient_answer(labels: list[str], values: list[float]) -> str:
    if len(labels) != len(values):
        raise ValueError("labels and values must have the same length")
    return ", ".join(
        f"${label}=${numerical_analysis_calc(float(value))}" for label, value in zip(labels, values)
    )


def point_answer(x_value: float, y_value: float) -> str:
    return ", ".join(
        [
            f"$x=${numerical_analysis_calc(float(x_value))}",
            f"$y=${numerical_analysis_calc(float(y_value))}",
        ]
    )


def integrate_polynomial(
    case: PolynomialCase | tuple[float, ...],
    constant: float = 0.0,
) -> PolynomialCase:
    poly = case if isinstance(case, PolynomialCase) else PolynomialCase(case)
    degree = poly.degree
    integrated: list[float] = []

    for index, coefficient in enumerate(poly.coeffs):
        power = degree - index + 1
        integrated.append(float(coefficient / power))

    integrated.append(float(constant))
    return PolynomialCase(tuple(integrated))


def build_plotly_visual_from_cases(
    cases: list[PolynomialCase],
    *,
    names: list[str] | tuple[str, ...],
    x_range: tuple[float, float] = (-3.0, 3.0),
    y_range: tuple[float, float] | None = None,
    title: str = "",
    x_axis: str = "x",
    y_axis: str = "y",
    showlegend: bool = True,
) -> dict:
    if len(cases) != len(names):
        raise ValueError("cases and names must have the same length")
    if not cases:
        raise ValueError("at least one case is required")

    x_min, x_max = x_range
    x_values = [round(x_min + (x_max - x_min) * index / 240.0, 4) for index in range(241)]

    y_min = float("inf")
    y_max = float("-inf")
    curves: list[dict] = []

    for index, (case, name) in enumerate(zip(cases, names)):
        y_values = [round(case.evaluate(x_value), 6) for x_value in x_values]
        y_min = min(y_min, min(y_values))
        y_max = max(y_max, max(y_values))
        curves.append(
            {
                "coefficients": [_visual_coeff(value) for value in case.coeffs],
                "mode": "lines",
                "name": name,
                "line": {"color": GRAPH_COLORS[index % len(GRAPH_COLORS)], "width": 2.5},
            }
        )

    if y_range is None:
        span = max(1.0, y_max - y_min)
        y_pad = max(0.75, 0.12 * span)
        y_step = axis_tick_step(span + 2.0 * y_pad)
        y_low = y_step * math.floor((y_min - y_pad) / y_step)
        y_high = y_step * math.ceil((y_max + y_pad) / y_step)
    else:
        y_low, y_high = y_range
        y_step = axis_tick_step(max(1.0, y_high - y_low))
    x_step = 1.0 if (x_max - x_min) <= 8.0 else axis_tick_step(x_max - x_min)

    return {
        "type": "plot",
        "spec": {
            "type": "polynomial-curves",
            "curves": curves,
            "points": len(x_values),
            "layout": {
                "title": title,
                "showlegend": showlegend,
                "xaxis": {
                    "title": x_axis,
                    "range": [x_min, x_max],
                    "dtick": round(x_step, 4),
                    "zeroline": True,
                },
                "yaxis": {
                    "title": y_axis,
                    "range": [round(y_low, 4), round(y_high, 4)],
                    "dtick": round(y_step, 4),
                    "zeroline": True,
                },
            },
        },
    }


def sample_constant_case(rng: random.Random) -> PolynomialCase:
    return PolynomialCase((float(rng.choice(NONZERO_SMALL_VALUES)),))


def sample_normal_polynomial(rng: random.Random, degree: int, *, value_bound: float = 48.0) -> PolynomialCase:
    if degree < 1:
        raise ValueError("degree must be >= 1")

    x_values = range(-2, 3) if degree >= 4 else range(-3, 4)
    for _ in range(700):
        coefficients = [rng.choice(LEADING_VALUES)]
        while len(coefficients) < degree:
            coefficients.append(rng.choice(NONZERO_SMALL_VALUES))
        coefficients.append(float(rng.randint(-5, 5)))
        case = PolynomialCase(tuple(coefficients))
        if max(abs(case.evaluate(x_value)) for x_value in x_values) <= value_bound:
            return case
    raise ValueError(f"Konnte kein geeignetes Polynom vom Grad {degree} erzeugen.")


def sample_centered_quadratic(rng: random.Random) -> tuple[PolynomialCase, float, float]:
    for _ in range(300):
        a_value = rng.choice(LEADING_VALUES)
        center = float(rng.choice(_WIDE_CENTER_VALUES))
        distance = float(rng.choice((1, 2, 3, 4)))
        b_value = -2.0 * a_value * center
        c_value = a_value * (center * center - distance * distance)
        case = PolynomialCase((a_value, b_value, c_value))
        if max(abs(case.evaluate(center + offset)) for offset in range(-4, 5)) <= 24.0:
            return case, center, distance
    raise ValueError("Konnte keine geeignete zentrierte quadratische Funktion erzeugen.")


def sample_product_quadratic(rng: random.Random) -> tuple[float, float, float, PolynomialCase]:
    for _ in range(300):
        case, center, distance = sample_centered_quadratic(rng)
        if abs(center) < 1e-12:
            continue
        root_left = center - distance
        root_right = center + distance
        return case.coeffs[0], root_left, root_right, case
    raise ValueError("Konnte keine geeignete Produktform erzeugen.")


def sample_normal_cubic(rng: random.Random) -> PolynomialCase:
    return sample_normal_polynomial(rng, degree=3, value_bound=42.0)


def sample_simple_product_case(rng: random.Random, *, name: str = "p") -> tuple[str, PolynomialCase]:
    for _ in range(400):
        scale = rng.choice(LEADING_VALUES)
        other_root = float(rng.choice([value for value in range(-5, 6) if value != 0]))
        case = PolynomialCase(scale_polynomial(multiply_polynomials((1.0, 0.0), (1.0, -other_root)), scale))
        if max(abs(case.evaluate(x_value)) for x_value in range(-3, 4)) <= 30.0:
            return factor_form_latex(scale, (0.0, other_root), name=name), case
    raise ValueError("Konnte keine einfache Produktform erzeugen.")


def sample_expansion_product_case(rng: random.Random, *, name: str = "q") -> tuple[str, PolynomialCase]:
    for _ in range(500):
        scale = rng.choice((-2.0, -1.0, 1.0, 2.0))
        a_value = float(rng.choice((1, 2, 3)))
        b_value = float(rng.choice((-3, -2, -1, 1, 2, 3)))
        c_candidates = [value for value in (-2, -1, 1, 2, 3, 4) if value != a_value]
        c_value = float(rng.choice(c_candidates))

        factor_left = (1.0, 0.0, -a_value)
        factor_right = (1.0, b_value, c_value)
        case = PolynomialCase(scale_polynomial(multiply_polynomials(factor_left, factor_right), scale))
        derivative = case.derivative(1)
        if max(abs(case.evaluate(x_value)) for x_value in range(-2, 3)) > 40.0:
            continue
        if any(abs(value) < 1e-12 for value in derivative.coeffs):
            continue
        expression = (
            f"{name}(x)={_scale_prefix(scale)}"
            f"(x^2-{fmt(a_value)})(x^2{_signed_mid_term(b_value)}x{_signed_const_term(c_value)})"
        )
        return expression, case
    raise ValueError("Konnte keine geeignete Produktform mit höheren Exponenten erzeugen.")


def sample_monotone_cubic(rng: random.Random) -> tuple[PolynomialCase, float, float]:
    for _ in range(500):
        sign = rng.choice((-1.0, 1.0))
        a_value = sign * rng.choice((1.0, 2.0))
        h_value = float(rng.choice(_WIDE_CENTER_VALUES))
        min_slope = sign * rng.choice((1.0, 2.0, 3.0, 4.0))
        y_shift = float(rng.randint(-4, 4))

        a3 = a_value
        a2 = -3.0 * a_value * h_value
        a1 = 3.0 * a_value * h_value * h_value + min_slope
        a0 = y_shift - a_value * (h_value ** 3) - min_slope * h_value
        case = PolynomialCase((a3, a2, a1, a0))

        local_window = _integer_window(h_value, radius=3)
        if max(abs(case.evaluate(x_value)) for x_value in local_window) <= 45.0:
            return case, h_value, min_slope
    raise ValueError("Konnte keine geeignete monotone kubische Funktion erzeugen.")


def sample_controlled_cubic(
    rng: random.Random,
    preferred_a3: float | None = None,
) -> tuple[PolynomialCase, int, int, int]:
    r"""Kubische Funktion mit kontrollierbarer quadratischer Ableitung.

    Konstruktion über
    $f'(x)=q\cdot((x-h)^2-d^2)+s$,
    damit Gleichungen der Form $f'(x)=m$ gezielt mit zwei ganzzahligen Lösungen
    $x=h\pm e$ erzeugt werden können.
    """

    a3_candidates = (preferred_a3,) if preferred_a3 is not None else CONTROLLED_CUBIC_LEADING_VALUES

    for _ in range(700):
        a3 = rng.choice(a3_candidates)
        q_scale = 3.0 * a3
        center = rng.choice(_CONTROLLED_CUBIC_CENTER_VALUES)
        root_distance = rng.choice((1, 2, 3))
        slope_shift = rng.choice((-4, -3, -2, -1, 1, 2, 3, 4))
        y_shift = float(rng.randint(-5, 5))

        a2 = -q_scale * center
        a1 = q_scale * (center * center - root_distance * root_distance) + slope_shift
        case = PolynomialCase((a3, a2, a1, y_shift))

        if abs(a2) < 1e-12:
            continue
        if max(abs(case.evaluate(x_value)) for x_value in _integer_window(center, radius=3)) > 38.0:
            continue

        return case, int(center), int(root_distance), int(slope_shift)

    raise ValueError("Konnte keine geeignete kontrollierte kubische Funktion erzeugen.")


def multiply_polynomials(*factors: tuple[float, ...]) -> tuple[float, ...]:
    result = [1.0]
    for factor in factors:
        current = list(factor)
        new_result = [0.0] * (len(result) + len(current) - 1)
        for index_result, coeff_result in enumerate(result):
            for index_factor, coeff_factor in enumerate(current):
                new_result[index_result + index_factor] += coeff_result * coeff_factor
        result = new_result
    return tuple(0.0 if abs(value) < 1e-12 else float(value) for value in result)


def _integer_window(center: float, *, radius: int) -> tuple[int, ...]:
    left = max(_WIDE_DOMAIN_MIN, int(math.floor(center)) - radius)
    right = min(_WIDE_DOMAIN_MAX, int(math.ceil(center)) + radius)
    return tuple(range(left, right + 1))


def scale_polynomial(coeffs: tuple[float, ...], scale: float) -> tuple[float, ...]:
    return tuple(0.0 if abs(scale * value) < 1e-12 else float(scale * value) for value in coeffs)


def _linear_factor(var: str, root: float) -> str:
    if abs(root) < 1e-12:
        return var
    if root > 0:
        return f"({var}-{fmt(root)})"
    return f"({var}+{fmt(abs(root))})"


def _scale_prefix(scale: float) -> str:
    if abs(scale - 1.0) < 1e-12:
        return ""
    if abs(scale + 1.0) < 1e-12:
        return "-"
    return fmt(scale)


def _signed_mid_term(value: float) -> str:
    if abs(value - 1.0) < 1e-12:
        return "+"
    if abs(value + 1.0) < 1e-12:
        return "-"
    return f"+{fmt(value)}" if value >= 0 else f"-{fmt(abs(value))}"


def _signed_const_term(value: float) -> str:
    return f"+{fmt(value)}" if value >= 0 else f"-{fmt(abs(value))}"