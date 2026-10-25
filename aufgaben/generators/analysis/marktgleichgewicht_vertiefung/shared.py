import math
import random
from collections.abc import Callable

from aufgaben.core.tolerances import nice_axis_max
from aufgaben.generators.analysis.marktgleichgewicht_grundlagen.shared import (
    _fmt_number,
    _num_tol,
    _signed,
)
from aufgaben.generators.analysis.shared_numbers import round_sig, uniform_sig


PriceFunction = Callable[[float], float]


def _align_equations(expressions: list[str]) -> str:
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


def _latex_supply_linear(slope: float, intercept: float) -> str:
    return f"p_A(x)={_fmt_number(slope, max_decimals=5)}x{_signed(intercept, max_decimals=5)}"


def _latex_demand_quadratic(a2: float, a1: float, a0: float) -> str:
    a2_text = _fmt_number(abs(a2), max_decimals=5)
    a1_text = _fmt_number(abs(a1), max_decimals=5)
    return (
        "p_N(x)="
        f"-{a2_text}x^2"
        f"-{a1_text}x"
        f"+{_fmt_number(a0, max_decimals=5)}"
    )


def _latex_supply_quadratic(a2: float, a1: float, a0: float) -> str:
    return (
        "p_A(x)="
        f"{_fmt_number(a2, max_decimals=5)}x^2"
        f"+{_fmt_number(a1, max_decimals=5)}x"
        f"+{_fmt_number(a0, max_decimals=5)}"
    )


def _latex_supply_exp(amplitude: float, rate: float, ceiling: float) -> str:
    return (
        "p_A(x)="
        f"-{_fmt_number(amplitude, max_decimals=5)}\\cdot e^{{-{_fmt_number(rate, max_decimals=5)}x}}"
        f"+{_fmt_number(ceiling, max_decimals=5)}"
    )


def _latex_demand_linear(slope_abs: float, intercept: float) -> str:
    return f"p_N(x)=-{_fmt_number(slope_abs, max_decimals=5)}x+{_fmt_number(intercept, max_decimals=5)}"


def _latex_demand_exp(amplitude: float, rate: float, floor: float) -> str:
    floor_sign = _signed(floor, max_decimals=5)
    return (
        "p_N(x)="
        f"{_fmt_number(amplitude, max_decimals=5)}\\cdot e^{{-{_fmt_number(rate, max_decimals=5)}x}}"
        f"{floor_sign}"
    )


def _demand_slope_abs_from_params(params: dict, x: float) -> float:
    spec_type = params.get("type")
    if spec_type == "linear":
        return abs(float(params["a"]))
    if spec_type == "quadratic":
        a = float(params["a"])
        b = float(params["b"])
        return abs(2.0 * a * x + b)

    amplitude = float(params["A"])
    rate = float(params["rate"])
    return abs(amplitude * rate * math.exp(-rate * x))


def _integrate_trapezoid(fn: PriceFunction, a: float, b: float, steps: int = 2000) -> float:
    """Numerische Integration (zusammengesetzte Simpsonregel; exakt fuer Polynome bis Grad 3).

    Der historische Name bleibt fuer bestehende Aufrufer erhalten.
    """
    if b <= a:
        return 0.0
    if steps % 2:
        steps += 1
    width = (b - a) / steps
    area = fn(a) + fn(b)
    for idx in range(1, steps):
        area += (4.0 if idx % 2 else 2.0) * fn(a + idx * width)
    return area * width / 3.0


def _solve_increasing(fn: PriceFunction, target: float, lo: float = 0.0, hi: float = 100.0) -> float | None:
    """Loest fn(x)=target fuer streng monoton steigendes fn auf [lo; inf) per Bisektion."""
    if fn(lo) > target:
        return None
    while fn(hi) < target:
        hi *= 2.0
        if hi > 1e7:
            return None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if fn(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _ueberschuss_item(
    rng: random.Random,
    *,
    supply_fn: PriceFunction,
    demand_fn: PriceFunction,
    min_price: float,
    max_price: float,
    eq_x: float,
    eq_p: float,
    supply_ceiling: float | None = None,
    min_share: float = 0.1,
) -> tuple[str, str] | None:
    """Teilfrage 'Art und Hoehe des Ueberschusses' bei festgelegtem ganzzahligem Preis.

    Preis < p_G  -> Nachfrageueberschuss x_N(P) - x_A(P) (P > Mindestangebotspreis)
    Preis > p_G  -> Angebotsueberschuss  x_A(P) - x_N(P) (P < Hoechstpreis, ggf. < Saettigungswert p_A)
    """
    neg_demand = lambda x: -demand_fn(x)

    def candidates(direction: str) -> list[tuple[int, float]]:
        result: list[tuple[int, float]] = []
        if direction == "nachfrage":
            lo = math.floor(min_price) + 1
            hi = math.ceil(eq_p) - 1
        else:
            lo = math.floor(eq_p) + 1
            hi = math.ceil(max_price) - 1
            if supply_ceiling is not None:
                hi = min(hi, math.ceil(supply_ceiling) - 1)
        for price in range(lo, hi + 1):
            if not (min_price < price < max_price):
                continue
            if supply_ceiling is not None and price >= supply_ceiling - 1e-9:
                continue
            x_a = _solve_increasing(supply_fn, float(price))
            x_n = _solve_increasing(neg_demand, -float(price))
            if x_a is None or x_n is None:
                continue
            diff = (x_n - x_a) if direction == "nachfrage" else (x_a - x_n)
            if diff >= min_share * eq_x and diff >= 0.5:
                result.append((price, diff))
        return result

    directions = ["nachfrage", "angebot"]
    rng.shuffle(directions)
    for direction in directions:
        options = candidates(direction)
        if not options:
            continue
        price, diff = rng.choice(options)
        if direction == "nachfrage":
            mc = "{1:MC:~Angebotsüberschuss~=Nachfrageüberschuss}"
        else:
            mc = "{1:MC:~=Angebotsüberschuss~Nachfrageüberschuss}"
        question = f"Art und Höhe des Überschusses, wenn der Preis auf {price} GE/ME festgelegt wird."
        answer = f"{mc} von {_num_tol(diff, tolerance=0.1)} ME"
        return question, answer
    return None


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
        slope = uniform_sig(rng, 0.12, 4.5)
        intercept = uniform_sig(rng, 1.0, 45.0)
        return (
            lambda x: slope * x + intercept,
            _latex_supply_linear(slope, intercept),
            (kind, slope, intercept),
            intercept,
            {"type": "linear", "a": slope, "b": intercept},
        )

    if kind == "quadratic":
        a2 = uniform_sig(rng, 0.003, 0.12)
        a1 = uniform_sig(rng, 0.05, 0.8)
        a0 = uniform_sig(rng, 1.0, 45.0)
        return (
            lambda x: a2 * (x ** 2) + a1 * x + a0,
            _latex_supply_quadratic(a2, a1, a0),
            (kind, a2, a1, a0),
            a0,
            {"type": "quadratic", "a": a2, "b": a1, "c": a0},
        )

    amplitude = uniform_sig(rng, 3.0, 80.0)
    rate = uniform_sig(rng, 0.02, 0.25)
    min_price = uniform_sig(rng, 1.0, 40.0)
    ceiling = round_sig(min_price + amplitude)
    # Tatsaechlicher Mindestangebotspreis aus den angezeigten Parametern.
    min_price = ceiling - amplitude
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
        slope_abs = uniform_sig(rng, 0.15, 5.0)
        intercept = uniform_sig(rng, min_price + 4.0, min_price + 250.0)
        return (
            lambda x: -slope_abs * x + intercept,
            lambda _x: -slope_abs,
            _latex_demand_linear(slope_abs, intercept),
            (kind, slope_abs, intercept),
            intercept,
            {"type": "linear", "a": -slope_abs, "b": intercept},
        )

    if kind == "quadratic":
        a2 = uniform_sig(rng, 0.005, 0.2)
        a1 = uniform_sig(rng, 0.01, 0.5)
        a0 = uniform_sig(rng, min_price + 4.0, min_price + 250.0)
        return (
            lambda x: -(a2 * (x ** 2)) - a1 * x + a0,
            lambda x: -2.0 * a2 * x - a1,
            _latex_demand_quadratic(a2, a1, a0),
            (kind, a2, a1, a0),
            a0,
            {"type": "quadratic", "a": -a2, "b": -a1, "c": a0},
        )

    amplitude = uniform_sig(rng, 4.0, 120.0)
    rate = uniform_sig(rng, 0.02, 0.22)
    floor = uniform_sig(rng, -15.0, -0.3)
    # Hoechstpreis exakt aus den angezeigten Parametern (keine Rundung).
    max_price = amplitude + floor
    if max_price <= min_price + 4.0:
        floor = round_sig(min_price + 4.5 - amplitude)
        max_price = amplitude + floor

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

        if max_price <= min_price + 2.0 or max_price > 950.0:
            continue

        sat_quantity = _find_root_in_interval(demand_fn, start=0.0, end=2000.0)
        if sat_quantity is None or not (3.0 <= sat_quantity <= 950.0):
            continue

        diff_fn = lambda x: supply_fn(x) - demand_fn(x)
        eq_upper = min(2000.0, max(15.0, sat_quantity * 1.05))
        eq_x = _find_root_in_interval(diff_fn, start=0.0, end=eq_upper)
        if eq_x is None or not (1.5 <= eq_x <= sat_quantity * 0.85):
            continue

        eq_p = supply_fn(eq_x)
        if not (min_price + 0.5 <= eq_p <= max_price - 0.5):
            continue

        if demand_derivative_fn(0.0) >= -0.01 or demand_derivative_fn(eq_x) >= -0.01:
            continue

        x2_fn = lambda x: demand_fn(x) + x * demand_derivative_fn(x) - eq_p
        x2 = _find_root_in_interval(x2_fn, start=0.0001, end=max(0.0002, eq_x - 0.0001))
        if x2 is None or not (0.5 <= x2 <= eq_x - 0.3):
            continue

        p2 = demand_fn(x2)
        if p2 <= eq_p + 0.5 or p2 > max_price - 0.3:
            continue

        # KR1/KR2 duerfen nicht zu klein sein – p2 muss deutlich
        # zwischen eq_p und max_price liegen (jeweils mind. 15% Abstand).
        price_range = max_price - eq_p
        if price_range <= 0 or (p2 - eq_p) < price_range * 0.15:
            continue
        if (max_price - p2) < price_range * 0.15:
            continue

        # Float-Artefakte (z. B. 4.1000000000000005) aus den Visual-Specs entfernen.
        supply_params = {k: (round(v, 10) if isinstance(v, float) else v) for k, v in supply_params.items()}
        demand_params = {k: (round(v, 10) if isinstance(v, float) else v) for k, v in demand_params.items()}

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


def _market_x_values(max_x: float, points: int = 280) -> list[float]:
    return [round(max_x * idx / (points - 1), 3) for idx in range(points)]


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
    revenue_tolerance: float | None = None,
) -> list[tuple[str, str]]:
    x_tol = 0.5 if x_tolerance is None else x_tolerance
    y_tol = 0.25 if y_tolerance is None else y_tolerance
    # Fehlerfortpflanzung fuer U = x_G * p_G: |dU| <= dx * p_G + dp * x_G
    revenue_tol = (
        x_tol * eq_price + y_tol * eq_quantity if revenue_tolerance is None else revenue_tolerance
    )

    return [
        ("den Mindestangebotspreis.", _num_tol(min_price, tolerance=y_tol)),
        ("den Höchstpreis.", _num_tol(max_price, tolerance=y_tol)),
        ("die Sättigungsmenge.", _num_tol(sat_quantity, tolerance=x_tol)),
        ("die Gleichgewichtsmenge.", _num_tol(eq_quantity, tolerance=x_tol)),
        ("den Gleichgewichtspreis.", _num_tol(eq_price, tolerance=y_tol)),
        ("den Umsatz im Marktgleichgewicht.", _num_tol(eq_quantity * eq_price, tolerance=revenue_tol)),
    ]
