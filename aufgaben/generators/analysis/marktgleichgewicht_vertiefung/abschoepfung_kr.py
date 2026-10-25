"""Abschöpfung der Konsumentenrente durch einen Teilmarkt.

Teilfrage 1: abgeschöpfter Betrag bei vorgegebenem (ganzzahligem) Teilmarktpreis P.
Teilfrage 2: Teilmarktmenge x_2 und -preis p_2 für maximale Abschöpfung,
             d. h. Maximum von A(x) = x * (p_N(x) - p_G) auf (0; x_G).

Die Funktionsparameter werden auf 2 signifikante Stellen gerundet; alle
Kennzahlen (x_G, p_G, x_P, x_2, p_2) werden anschließend aus den GERUNDETEN
(= angezeigten) Parametern neu berechnet.
"""

import math
import random

from aufgaben.core.models import Task
from aufgaben.core.tolerances import nice_axis_max
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.marktgleichgewicht_grundlagen.shared import _fmt_number
from aufgaben.generators.analysis.marktgleichgewicht_vertiefung.shared import (
    _align_equations,
    _demand_slope_abs_from_params,
    _find_root_in_interval,
    _integrate_trapezoid,
    _num_tol,
    _sample_market_params,
)
from aufgaben.generators.analysis.shared_numbers import round_sig


def _fmt_sig(value: float) -> str:
    return _fmt_number(round_sig(value, digits=2), max_decimals=6)


def _signed_sig(value: float) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}{_fmt_sig(abs(value))}"


def _round_params_sig(params: dict) -> dict:
    rounded: dict = {"type": params["type"]}
    for key, value in params.items():
        if key == "type":
            continue
        rounded[key] = round_sig(float(value), digits=2)
    return rounded


def _build_supply_from_params(params: dict):
    spec_type = params["type"]
    if spec_type == "linear":
        a, b = float(params["a"]), float(params["b"])
        return lambda x: a * x + b, f"p_A(x)={_fmt_sig(a)}x{_signed_sig(b)}"

    if spec_type == "quadratic":
        a, b, c = float(params["a"]), float(params["b"]), float(params["c"])
        return (
            lambda x: a * (x ** 2) + b * x + c,
            f"p_A(x)={_fmt_sig(a)}x^2{_signed_sig(b)}x{_signed_sig(c)}",
        )

    a, rate, c = float(params["A"]), float(params["rate"]), float(params["c"])
    return (
        lambda x: a * math.exp(-rate * x) + c,
        f"p_A(x)={_fmt_sig(a)}\\cdot e^{{-{_fmt_sig(rate)}x}}{_signed_sig(c)}",
    )


def _build_demand_from_params(params: dict):
    """Liefert (p_N, p_N', p_N'', LaTeX, Höchstpreis) aus den gerundeten Parametern."""
    spec_type = params["type"]
    if spec_type == "linear":
        a, b = float(params["a"]), float(params["b"])
        return (
            lambda x: a * x + b,
            lambda _x: a,
            lambda _x: 0.0,
            f"p_N(x)={_fmt_sig(a)}x{_signed_sig(b)}",
            b,
        )

    if spec_type == "quadratic":
        a, b, c = float(params["a"]), float(params["b"]), float(params["c"])
        return (
            lambda x: a * (x ** 2) + b * x + c,
            lambda x: 2.0 * a * x + b,
            lambda _x: 2.0 * a,
            f"p_N(x)={_fmt_sig(a)}x^2{_signed_sig(b)}x{_signed_sig(c)}",
            c,
        )

    a, rate, c = float(params["A"]), float(params["rate"]), float(params["c"])
    return (
        lambda x: a * math.exp(-rate * x) + c,
        lambda x: -a * rate * math.exp(-rate * x),
        lambda x: a * rate * rate * math.exp(-rate * x),
        f"p_N(x)={_fmt_sig(a)}\\cdot e^{{-{_fmt_sig(rate)}x}}{_signed_sig(c)}",
        a + c,
    )


class MarketEquilibriumAbschoepfungKRGenerator(TaskGenerator):
    generator_key = "analysis.marktgleichgewicht_vertiefung.abschoepfung_kr"
    _min_demand_slope_abs = 0.45
    _max_eq_quantity_for_plot = 65.0

    def _sample(self, rng: random.Random, used: set[tuple]) -> dict:
        while True:
            sample = _sample_market_params(rng)
            market_key = sample[5]
            supply_params, demand_params = sample[13], sample[14]
            if market_key in used:
                continue

            supply_params = _round_params_sig(supply_params)
            demand_params = _round_params_sig(demand_params)
            supply_fn, supply_latex = _build_supply_from_params(supply_params)
            demand_fn, d1, d2, demand_latex, max_price = _build_demand_from_params(demand_params)

            if supply_fn(0.0) <= 0.0 or d1(0.0) >= 0.0:
                continue

            sat_quantity = _find_root_in_interval(demand_fn, start=0.0, end=2000.0)
            if sat_quantity is None or sat_quantity <= 1.5:
                continue

            eq_x = _find_root_in_interval(
                lambda x: supply_fn(x) - demand_fn(x),
                start=0.0,
                end=min(2000.0, max(18.0, sat_quantity * 1.05)),
            )
            if eq_x is None or not (2.0 <= eq_x <= self._max_eq_quantity_for_plot):
                continue
            eq_p = supply_fn(eq_x)
            if not (0.2 < eq_p < max_price - 0.2):
                continue

            spanne = max_price - eq_p
            if spanne < 10.0:  # genug Platz für ganzzahlige Preise abseits von p_2
                continue

            # Optimale Abschöpfung: A(x) = x*(p_N(x)-p_G), A'(x) = p_N + x p_N' - p_G
            a_fn = lambda x: x * (demand_fn(x) - eq_p)
            a1_fn = lambda x: demand_fn(x) + x * d1(x) - eq_p
            a2_fn = lambda x: 2.0 * d1(x) + x * d2(x)
            x2 = _find_root_in_interval(a1_fn, start=1e-6, end=eq_x - 1e-6, steps=4000, epsilon=1e-12)
            if x2 is None or a2_fn(x2) >= 0.0:
                continue
            grid_max = max(a_fn(eq_x * k / 2000.0) for k in range(1, 2000))
            if a_fn(x2) < grid_max - 1e-6:
                continue  # kein globales Maximum auf (0; x_G)
            p2 = demand_fn(x2)
            if not (0.15 * eq_x <= x2 <= 0.85 * eq_x):
                continue

            # vorgegebener Teilmarktpreis P (ganzzahlig), deutlich von p_G, p_max und p_2 entfernt
            min_gap = max(1.0, 0.15 * spanne)
            candidates = [
                price
                for price in range(math.ceil(eq_p + min_gap), math.floor(max_price - min_gap) + 1)
                if abs(price - p2) >= min_gap
            ]
            if not candidates:
                continue
            price = float(rng.choice(candidates))

            x_p = _find_root_in_interval(lambda x: demand_fn(x) - price, start=0.0, end=eq_x, steps=4000, epsilon=1e-12)
            if x_p is None or not (0.15 * eq_x <= x_p <= 0.85 * eq_x):
                continue

            # KR1 und KR2 sollen in der Grafik deutlich sichtbar sein
            kr_total = _integrate_trapezoid(demand_fn, 0.0, eq_x) - eq_x * eq_p
            kr2 = _integrate_trapezoid(demand_fn, 0.0, x_p) - x_p * price
            kr1 = _integrate_trapezoid(demand_fn, x_p, eq_x) - (eq_x - x_p) * eq_p
            if min(kr1, kr2) < 0.12 * kr_total:
                continue

            if min(
                _demand_slope_abs_from_params(demand_params, eq_x),
                _demand_slope_abs_from_params(demand_params, x_p),
                _demand_slope_abs_from_params(demand_params, x2),
            ) < self._min_demand_slope_abs:
                continue

            abschoepfung = (price - eq_p) * x_p
            if abschoepfung <= 1.0:
                continue

            used.add(market_key)
            return {
                "supply_params": supply_params,
                "demand_params": demand_params,
                "supply_latex": supply_latex,
                "demand_latex": demand_latex,
                "max_price": max_price,
                "eq_x": eq_x,
                "eq_p": eq_p,
                "price": price,
                "x_p": x_p,
                "abschoepfung": abschoepfung,
                "x2": x2,
                "p2": p2,
            }

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple] = set()

        for _ in range(count):
            s = self._sample(rng, used)
            price_text = str(int(round(s["price"])))  # _fmt_number(.., 0) würde 70 -> "7" kürzen
            max_x = nice_axis_max(s["eq_x"] * 1.25)
            max_y = nice_axis_max(s["max_price"] * 1.1)
            # Rechnen mit auf 2 NKS gerundeten x_P und p_G (je ±0,005) soll akzeptiert werden.
            abschoepfung_tol = math.ceil(
                max(0.1, 0.005 * (s["x_p"] + (s["price"] - s["eq_p"])) + 0.01) * 100 - 1e-9
            ) / 100

            tasks.append(
                Task(
                    einleitung=(
                        "Gegeben sind die Angebots- und Nachfragefunktion ($ x $ in ME, $ p $ in GE/ME):"
                        f"{_align_equations([s['supply_latex'], s['demand_latex']])}"
                        "Durch einen Teilmarkt soll ein Teil der Konsumentenrente abgeschöpft werden. "
                        "Auf dem ersten Teilmarkt gilt der Gleichgewichtspreis $ p_G $. "
                        "Bestimmen Sie (auf 2 NKS gerundet)"
                    ),
                    fragen=[
                        "den abgeschöpften Teil der Konsumentenrente, wenn auf dem Teilmarkt "
                        f"ein Preis von {price_text} GE/ME verlangt wird.",
                        "die Teilmarktmenge $ x_2 $ und den Teilmarktpreis $ p_2 $, "
                        "bei denen die Konsumentenrente maximal abgeschöpft wird.",
                    ],
                    antworten=[
                        _num_tol(s["abschoepfung"], tolerance=abschoepfung_tol),
                        f"$x_2=$ {_num_tol(s['x2'], tolerance=0.1)} ME, "
                        f"$p_2=$ {_num_tol(s['p2'], tolerance=0.1)} GE/ME",
                    ],
                    visual={
                        "type": "plot",
                        "spec": {
                            "type": "market-abschoepfung",
                            "params": {
                                "supply": s["supply_params"],
                                "demand": s["demand_params"],
                                "eqX": round(s["eq_x"], 4),
                                "eqP": round(s["eq_p"], 4),
                                "xP": round(s["x_p"], 4),
                                "price": s["price"],
                                "maxX": max_x,
                                "maxY": max_y,
                            },
                            "layout": {
                                "title": f"Abschöpfung durch einen Teilmarkt mit dem Preis {price_text} GE/ME",
                                "xaxis": {"title": "Menge x in ME"},
                                "yaxis": {"title": "Preis p in GE/ME"},
                            },
                            "width": 900,
                            "height": 520,
                            "scale": 1,
                        },
                    },
                )
            )

        return tasks
