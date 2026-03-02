import math
import random
from collections.abc import Callable

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.marktgleichgewicht_grundlagen.shared import _num_tol


PriceFunction = Callable[[float], float]


def _find_first_positive_root(
    fn: PriceFunction,
    *,
    start: float = 0.0,
    end: float = 120.0,
    steps: int = 1200,
    epsilon: float = 1e-7,
) -> float | None:
    previous_x = start
    previous_y = fn(previous_x)
    if abs(previous_y) < epsilon and previous_x > 0:
        return previous_x

    for idx in range(1, steps + 1):
        current_x = start + (end - start) * idx / steps
        current_y = fn(current_x)

        if abs(current_y) < epsilon and current_x > 0:
            return current_x

        if previous_y == 0:
            return previous_x if previous_x > 0 else None

        if previous_y * current_y < 0:
            left_x, right_x = previous_x, current_x
            left_y, right_y = previous_y, current_y
            for _ in range(60):
                mid_x = 0.5 * (left_x + right_x)
                mid_y = fn(mid_x)
                if abs(mid_y) < epsilon:
                    return mid_x
                if left_y * mid_y <= 0:
                    right_x, right_y = mid_x, mid_y
                else:
                    left_x, left_y = mid_x, mid_y
            return 0.5 * (left_x + right_x)

        previous_x, previous_y = current_x, current_y

    return None


def _fmt(value: float, decimals: int = 3) -> str:
    text = f"{round(value, decimals):.{decimals}f}".rstrip("0").rstrip(".")
    if text in {"-0", ""}:
        return "0"
    return text.replace(".", ",")


def _build_supply(rng: random.Random) -> tuple[PriceFunction, str, tuple[str, float, float, float]]:
    model = rng.choice(["linear", "quadratic", "exp"])

    if model == "linear":
        slope = round(rng.uniform(0.18, 2.1), 3)
        intercept = round(rng.uniform(1.2, 9.5), 2)
        return (
            lambda x: slope * x + intercept,
            f"\\( p_A(x)={_fmt(slope)}x+{_fmt(intercept, 2)} \\)",
            ("linear", slope, intercept, 0.0),
        )

    if model == "quadratic":
        a2 = round(rng.uniform(0.01, 0.08), 3)
        a1 = round(rng.uniform(0.01, 0.2), 3)
        a0 = round(rng.uniform(1.2, 8.5), 2)
        return (
            lambda x: a2 * (x ** 2) + a1 * x + a0,
            f"\\( p_A(x)={_fmt(a2)}x^2+{_fmt(a1)}x+{_fmt(a0, 2)} \\)",
            ("quadratic", a2, a1, a0),
        )

    amplitude = round(rng.uniform(5.0, 32.0), 2)
    rate = round(rng.uniform(0.04, 0.35), 3)
    shift = round(rng.uniform(1.0, 12.0), 2)
    ceiling = round(amplitude + shift, 2)
    return (
        lambda x: -amplitude * math.exp(-rate * x) + ceiling,
        f"\\( p_A(x)=-{_fmt(amplitude, 2)}\\cdot e^{{-{_fmt(rate)}x}}+{_fmt(ceiling, 2)} \\)",
        ("exp", amplitude, rate, ceiling),
    )


def _build_demand(rng: random.Random, min_price: float) -> tuple[PriceFunction, str, tuple[str, float, float, float]]:
    model = rng.choice(["linear", "quadratic", "exp"])

    if model == "linear":
        slope = round(rng.uniform(0.2, 2.4), 3)
        intercept = round(rng.uniform(min_price + 4.0, min_price + 32.0), 2)
        return (
            lambda x: -slope * x + intercept,
            f"\\( p_N(x)=-{_fmt(slope)}x+{_fmt(intercept, 2)} \\)",
            ("linear", slope, intercept, 0.0),
        )

    if model == "quadratic":
        a2 = round(rng.uniform(0.015, 0.14), 3)
        a1 = round(rng.uniform(0.0, 0.26), 3)
        a0 = round(rng.uniform(min_price + 4.0, min_price + 36.0), 2)
        return (
            lambda x: -(a2 * (x ** 2)) - a1 * x + a0,
            f"\\( p_N(x)=-{_fmt(a2)}x^2-{_fmt(a1)}x+{_fmt(a0, 2)} \\)",
            ("quadratic", a2, a1, a0),
        )

    amplitude = round(rng.uniform(6.0, 48.0), 2)
    rate = round(rng.uniform(0.03, 0.25), 3)
    floor = round(rng.uniform(-8.0, 2.0), 2)
    if amplitude + floor <= min_price + 4.0:
        floor = round(min_price + 5.0 - amplitude, 2)
    return (
        lambda x: amplitude * math.exp(-rate * x) + floor,
        f"\\( p_N(x)={_fmt(amplitude, 2)}\\cdot e^{{-{_fmt(rate)}x}}{_sign_term(floor)} \\)",
        ("exp", amplitude, rate, floor),
    )


def _sign_term(value: float) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}{_fmt(abs(value), 2)}"


class MarketEquilibriumKennzahlenRechnerischLQEGenerator(TaskGenerator):
    generator_key = "analysis.marktgleichgewicht_vertiefung.kennzahlen_rechnerisch_linearquadratischexp"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used_keys: set[tuple] = set()

        while len(tasks) < count:
            supply_fn, supply_latex, supply_key = _build_supply(rng)
            min_price = supply_fn(0.0)
            if min_price <= 0:
                continue

            demand_fn, demand_latex, demand_key = _build_demand(rng, min_price)
            max_price = demand_fn(0.0)
            if max_price <= min_price + 1.0:
                continue

            sat_quantity = _find_first_positive_root(demand_fn, end=140.0)
            if sat_quantity is None or not (4.0 <= sat_quantity <= 70.0):
                continue

            eq_quantity = _find_first_positive_root(
                lambda x: supply_fn(x) - demand_fn(x),
                end=min(140.0, max(20.0, sat_quantity * 1.15)),
            )
            if eq_quantity is None or not (0.8 <= eq_quantity <= sat_quantity * 0.97):
                continue

            eq_price = supply_fn(eq_quantity)
            if not (min_price + 0.15 <= eq_price <= max_price - 0.15):
                continue

            uniqueness_key = (
                supply_key,
                demand_key,
                round(sat_quantity, 4),
                round(eq_quantity, 4),
            )
            if uniqueness_key in used_keys:
                continue
            used_keys.add(uniqueness_key)

            tasks.append(
                Task(
                    einleitung=(
                        "Gegeben sind die Angebotsfunktion <br/></p>"
                        f"{supply_latex}"
                        "<br/></p> und die Nachfragefunktion <br/></p>"
                        f"{demand_latex}"
                        ".</p> <p>Bestimmen Sie (auf 2 NKS gerundet)"
                    ),
                    fragen=[
                        "den Mindestangebotspreis.",
                        "den Höchstpreis.",
                        "die Sättigungsmenge.",
                        "die Gleichgewichtsmenge.",
                        "den Gleichgewichtspreis.",
                    ],
                    antworten=[
                        _num_tol(min_price, tolerance=0.1),
                        _num_tol(max_price, tolerance=0.1),
                        _num_tol(sat_quantity, tolerance=0.1),
                        _num_tol(eq_quantity, tolerance=0.1),
                        _num_tol(eq_price, tolerance=0.1),
                    ],
                )
            )

        return tasks
