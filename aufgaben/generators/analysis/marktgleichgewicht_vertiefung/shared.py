import math
import random
from collections.abc import Callable

from aufgaben.core.tolerances import axis_tick_step
from aufgaben.generators.analysis.marktgleichgewicht_grundlagen.shared import (
    _fmt_number,
    _num_tol,
    _signed,
)
from aufgaben.generators.analysis.shared_numbers import round_sig, uniform_sig


PriceFunction = Callable[[float], float]


def _axis_tick_step(span: float) -> float:
    return axis_tick_step(span)


def _latex_supply_linear(slope: float, intercept: float) -> str:
    return f"\\( p_A(x)={_fmt_number(slope, max_decimals=3)}x{_signed(intercept, max_decimals=2)} \\)"


def _latex_demand_quadratic(a2: float, a1: float, a0: float) -> str:
    a2_text = _fmt_number(abs(a2), max_decimals=3)
    a1_text = _fmt_number(abs(a1), max_decimals=3)
    return (
        "\\( p_N(x)="
        f"-{a2_text}x^2"
        f"-{a1_text}x"
        f"+{_fmt_number(a0, max_decimals=2)} \\)"
    )


def _latex_supply_quadratic(a2: float, a1: float, a0: float) -> str:
    return (
        "\\( p_A(x)="
        f"{_fmt_number(a2, max_decimals=3)}x^2"
        f"+{_fmt_number(a1, max_decimals=3)}x"
        f"+{_fmt_number(a0, max_decimals=2)} \\)"
    )


def _latex_supply_exp(amplitude: float, rate: float, ceiling: float) -> str:
    return (
        "\\( p_A(x)="
        f"-{_fmt_number(amplitude, max_decimals=2)}\\cdot e^{{-{_fmt_number(rate, max_decimals=3)}x}}"
        f"+{_fmt_number(ceiling, max_decimals=2)} \\)"
    )


def _latex_demand_linear(slope_abs: float, intercept: float) -> str:
    return f"\\( p_N(x)=-{_fmt_number(slope_abs, max_decimals=3)}x+{_fmt_number(intercept, max_decimals=2)} \\)"


def _latex_demand_exp(amplitude: float, rate: float, floor: float) -> str:
    floor_sign = _signed(floor, max_decimals=2)
    return (
        "\\( p_N(x)="
        f"{_fmt_number(amplitude, max_decimals=2)}\\cdot e^{{-{_fmt_number(rate, max_decimals=3)}x}}"
        f"{floor_sign} \\)"
    )


def _integrate_trapezoid(fn: PriceFunction, a: float, b: float, steps: int = 900) -> float:
    if b <= a:
        return 0.0
    width = (b - a) / steps
    area = 0.5 * (fn(a) + fn(b))
    for idx in range(1, steps):
        area += fn(a + idx * width)
    return area * width


def _find_root_in_interval(
    fn: PriceFunction,
    *,
    start: float,
    end: float,
    steps: int = 1600,
    epsilon: float = 1e-7,
) -> float | None:
    if end <= start:
        return None

    previous_x = start
    previous_y = fn(previous_x)
    if abs(previous_y) <= epsilon:
        return previous_x

    for idx in range(1, steps + 1):
        current_x = start + (end - start) * idx / steps
        current_y = fn(current_x)

        if abs(current_y) <= epsilon:
            return current_x

        if previous_y * current_y < 0:
            left_x, right_x = previous_x, current_x
            left_y, right_y = previous_y, current_y
            for _ in range(70):
                mid_x = 0.5 * (left_x + right_x)
                mid_y = fn(mid_x)
                if abs(mid_y) <= epsilon:
                    return mid_x
                if left_y * mid_y <= 0:
                    right_x, right_y = mid_x, mid_y
                else:
                    left_x, left_y = mid_x, mid_y
            return 0.5 * (left_x + right_x)

        previous_x, previous_y = current_x, current_y

    return None


def _build_supply_function(rng: random.Random) -> tuple[PriceFunction, str, tuple, float, dict]:
    kind = rng.choice(["linear", "quadratic", "exp"])

    if kind == "linear":
        slope = uniform_sig(rng, 0.22, 2.3)
        intercept = uniform_sig(rng, 1.2, 9.8)
        return (
            lambda x: slope * x + intercept,
            _latex_supply_linear(slope, intercept),
            (kind, slope, intercept),
            intercept,
            {"type": "linear", "a": slope, "b": intercept},
        )

    if kind == "quadratic":
        a2 = uniform_sig(rng, 0.004, 0.065)
        a1 = uniform_sig(rng, 0.05, 0.34)
        a0 = uniform_sig(rng, 1.0, 9.2)
        return (
            lambda x: a2 * (x ** 2) + a1 * x + a0,
            _latex_supply_quadratic(a2, a1, a0),
            (kind, a2, a1, a0),
            a0,
            {"type": "quadratic", "a": a2, "b": a1, "c": a0},
        )

    amplitude = uniform_sig(rng, 4.2, 22.0)
    rate = uniform_sig(rng, 0.04, 0.32)
    min_price = uniform_sig(rng, 1.0, 9.0)
    ceiling = round_sig(min_price + amplitude)
    return (
        lambda x: -amplitude * math.exp(-rate * x) + ceiling,
        _latex_supply_exp(amplitude, rate, ceiling),
        (kind, amplitude, rate, ceiling),
        min_price,
        {"type": "exp", "A": -amplitude, "rate": rate, "c": ceiling},
    )


def _build_demand_function(
    rng: random.Random,
    *,
    min_price: float,
) -> tuple[PriceFunction, PriceFunction, str, tuple, float, dict]:
    kind = rng.choice(["linear", "quadratic", "exp"])

    if kind == "linear":
        slope_abs = uniform_sig(rng, 0.2, 2.5)
        intercept = uniform_sig(rng, min_price + 4.0, min_price + 34.0)
        return (
            lambda x: -slope_abs * x + intercept,
            lambda _x: -slope_abs,
            _latex_demand_linear(slope_abs, intercept),
            (kind, slope_abs, intercept),
            intercept,
            {"type": "linear", "a": -slope_abs, "b": intercept},
        )

    if kind == "quadratic":
        a2 = uniform_sig(rng, 0.015, 0.14)
        a1 = uniform_sig(rng, 0.01, 0.28)
        a0 = uniform_sig(rng, min_price + 4.0, min_price + 36.0)
        return (
            lambda x: -(a2 * (x ** 2)) - a1 * x + a0,
            lambda x: -2.0 * a2 * x - a1,
            _latex_demand_quadratic(a2, a1, a0),
            (kind, a2, a1, a0),
            a0,
            {"type": "quadratic", "a": -a2, "b": -a1, "c": a0},
        )

    amplitude = uniform_sig(rng, 6.0, 42.0)
    rate = uniform_sig(rng, 0.03, 0.24)
    floor = uniform_sig(rng, -9.0, -0.3)
    max_price = round_sig(amplitude + floor)
    if max_price <= min_price + 4.0:
        floor = round_sig(min_price + 4.5 - amplitude)
        max_price = round_sig(amplitude + floor)

    return (
        lambda x: amplitude * math.exp(-rate * x) + floor,
        lambda x: -amplitude * rate * math.exp(-rate * x),
        _latex_demand_exp(amplitude, rate, floor),
        (kind, amplitude, rate, floor),
        max_price,
        {"type": "exp", "A": amplitude, "rate": rate, "c": floor},
    )


def _sample_market_params(
    rng: random.Random,
) -> tuple[
    PriceFunction,
    PriceFunction,
    PriceFunction,
    str,
    str,
    tuple,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
]:
    while True:
        supply_fn, supply_latex, supply_key, min_price, supply_params = _build_supply_function(rng)
        demand_fn, demand_derivative_fn, demand_latex, demand_key, max_price, demand_params = _build_demand_function(
            rng,
            min_price=min_price,
        )

        if max_price <= min_price + 0.9:
            continue

        sat_quantity = _find_root_in_interval(demand_fn, start=0.0, end=120.0)
        if sat_quantity is None or not (3.5 <= sat_quantity <= 70.0):
            continue

        diff_fn = lambda x: supply_fn(x) - demand_fn(x)
        eq_upper = min(120.0, max(18.0, sat_quantity * 1.05))
        eq_x = _find_root_in_interval(diff_fn, start=0.0, end=eq_upper)
        if eq_x is None or not (0.9 <= eq_x <= sat_quantity * 0.95):
            continue

        eq_p = supply_fn(eq_x)
        if not (min_price + 0.1 <= eq_p <= max_price - 0.1):
            continue

        if demand_derivative_fn(0.0) >= -0.01 or demand_derivative_fn(eq_x) >= -0.01:
            continue

        x2_fn = lambda x: demand_fn(x) + x * demand_derivative_fn(x) - eq_p
        x2 = _find_root_in_interval(x2_fn, start=0.0001, end=max(0.0002, eq_x - 0.0001))
        if x2 is None or not (0.3 <= x2 <= eq_x - 0.2):
            continue

        p2 = demand_fn(x2)
        if p2 <= eq_p + 0.2:
            continue

        return (
            supply_fn,
            demand_fn,
            demand_derivative_fn,
            supply_latex,
            demand_latex,
            (supply_key, demand_key),
            min_price,
            max_price,
            sat_quantity,
            eq_x,
            eq_p,
            x2,
            p2,
            supply_params,
            demand_params,
        )

    disc = b * b - 4 * a * c
    if disc < 0:
        return None
    sqrt_disc = math.sqrt(disc)
    roots = [(-b + sqrt_disc) / (2 * a), (-b - sqrt_disc) / (2 * a)]
    positive_roots = [root for root in roots if root > 0]
    if not positive_roots:
        return None
    return min(positive_roots)


def _market_x_values(max_x: float, points: int = 280) -> list[float]:
    return [round(max_x * idx / (points - 1), 3) for idx in range(points)]


def _demand_value(demand_fn: PriceFunction, x: float) -> float:
    return demand_fn(x)


def _supply_value(supply_fn: PriceFunction, x: float) -> float:
    return supply_fn(x)


def _consumer_surplus(demand_fn: PriceFunction, eq_x: float, eq_p: float) -> float:
    return _integrate_trapezoid(demand_fn, 0.0, eq_x) - eq_p * eq_x


def _producer_surplus(supply_fn: PriceFunction, eq_x: float, eq_p: float) -> float:
    return eq_p * eq_x - _integrate_trapezoid(supply_fn, 0.0, eq_x)


def _kennzahlen_items_allgemein(
    *,
    min_price: float,
    max_price: float,
    sat_quantity: float,
    eq_quantity: float,
    eq_price: float,
    x_tolerance: float | None = None,
    y_tolerance: float | None = None,
) -> list[tuple[str, str]]:
    x_tol = 0.5 if x_tolerance is None else x_tolerance
    y_tol = 0.25 if y_tolerance is None else y_tolerance

    return [
        ("den Mindestangebotspreis.", _num_tol(min_price, tolerance=y_tol)),
        ("den Höchstpreis.", _num_tol(max_price, tolerance=y_tol)),
        ("die Sättigungsmenge.", _num_tol(sat_quantity, tolerance=x_tol)),
        ("die Gleichgewichtsmenge.", _num_tol(eq_quantity, tolerance=x_tol)),
        ("den Gleichgewichtspreis.", _num_tol(eq_price, tolerance=y_tol)),
    ]
