import random

from aufgaben.core.tolerances import axis_tick_step
from aufgaben.generators.analysis.shared_numbers import uniform_sig


def _fmt_number(value: float, max_decimals: int = 4) -> str:
    rounded = round(float(value), max_decimals)
    text = f"{rounded:.{max_decimals}f}".rstrip("0").rstrip(".")
    if text in {"-0", ""}:
        text = "0"
    return text.replace(".", ",")


def _signed(value: float, max_decimals: int = 4) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}{_fmt_number(abs(value), max_decimals=max_decimals)}"


def _num_tol(value: float, tolerance: float, decimals: int = 4) -> str:
    value_text = _fmt_number(round(value, decimals), max_decimals=decimals)
    tol_text = _fmt_number(round(tolerance, 2), max_decimals=2)
    return f"{{1:NUMERICAL:={value_text}:{tol_text}}}"


def _axis_tick_step(span: float) -> float:
    return axis_tick_step(span)


def _latex_supply(slope: float, intercept: float) -> str:
    return f"\\( p_A(x)={_fmt_number(slope, max_decimals=2)}x{_signed(intercept, max_decimals=1)} \\)"


def _latex_demand(slope_abs: float, intercept: float) -> str:
    return f"\\( p_N(x)=-{_fmt_number(slope_abs, max_decimals=2)}x{_signed(intercept, max_decimals=1)} \\)"


def _sample_linear_market_parameters(
    rng: random.Random,
) -> tuple[float, float, float, float, float, float, float]:
    while True:
        supply_slope = uniform_sig(rng, 0.1, 4.5)
        demand_slope = uniform_sig(rng, 0.2, 5.8)
        min_price = uniform_sig(rng, 1.0, 15.0)
        max_price = uniform_sig(rng, min_price + 4.0, 45.0)

        sat_quantity = max_price / demand_slope
        eq_quantity = (max_price - min_price) / (supply_slope + demand_slope)
        eq_price = supply_slope * eq_quantity + min_price

        if 1.0 <= eq_quantity <= 35.0 and 4.0 <= sat_quantity <= 60.0 and eq_price > 0:
            return (
                supply_slope,
                demand_slope,
                min_price,
                max_price,
                sat_quantity,
                eq_quantity,
                eq_price,
            )


def _kennzahlen_items(
    *,
    min_price: float,
    max_price: float,
    sat_quantity: float,
    eq_quantity: float,
    eq_price: float,
    tolerance: float | None = None,
    x_tolerance: float | None = None,
    y_tolerance: float | None = None,
) -> list[tuple[str, str]]:
    # Backward compatibility for older callers that pass a single tolerance value.
    if tolerance is not None:
        if x_tolerance is None:
            x_tolerance = tolerance
        if y_tolerance is None:
            y_tolerance = tolerance

    x_tol = 0.5 if x_tolerance is None else x_tolerance
    y_tol = 0.5 if y_tolerance is None else y_tolerance

    return [
        ("den Mindestangebotspreis.", _num_tol(min_price, y_tol)),
        ("den Höchstpreis.", _num_tol(max_price, y_tol)),
        ("die Sättigungsmenge.", _num_tol(sat_quantity, x_tol)),
        ("die Gleichgewichtsmenge.", _num_tol(eq_quantity, x_tol)),
        ("den Gleichgewichtspreis.", _num_tol(eq_price, y_tol)),
    ]


def _build_market_visual(
    *,
    supply_slope: float,
    demand_slope: float,
    min_price: float,
    max_price: float,
    sat_quantity: float,
    eq_quantity: float,
    eq_price: float,
) -> dict:
    max_x = max(10.0, sat_quantity * 1.12, eq_quantity * 1.35)
    max_y = max(max_price, eq_price) * 1.15

    return {
        "type": "plot",
        "spec": {
            "type": "market-curves",
            "params": {
                "supplySlope": supply_slope,
                "demandSlope": demand_slope,
                "minPrice": min_price,
                "maxPrice": max_price,
                "maxX": max_x,
            },
            "points": 220,
            "layout": {
                "title": "Angebots- und Nachfragefunktion",
                "xaxis": {"title": "Menge x", "range": [0, max_x]},
                "yaxis": {"title": "Preis p", "range": [0, max_y]},
            },
            "width": 900,
            "height": 520,
            "scale": 1,
        },
    }
