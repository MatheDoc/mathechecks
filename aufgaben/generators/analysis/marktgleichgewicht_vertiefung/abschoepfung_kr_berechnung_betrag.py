import math
import random

from aufgaben.core.models import Task
from aufgaben.core.tolerances import nice_axis_max
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.marktgleichgewicht_grundlagen.shared import _fmt_number
from aufgaben.generators.analysis.marktgleichgewicht_vertiefung.shared import (
    _align_equations,
    _find_root_in_interval,
    _num_tol,
    _sample_market_params,
)


def _round_sig(value: float, digits: int = 2) -> float:
    if value == 0:
        return 0.0
    exponent = math.floor(math.log10(abs(value)))
    factor = 10 ** (digits - 1 - exponent)
    rounded = round(value * factor) / factor
    if abs(rounded) < 1e-12:
        return 0.0
    return rounded


def _fmt_sig(value: float) -> str:
    return _fmt_number(_round_sig(value, digits=2), max_decimals=6)


def _signed_sig(value: float) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}{_fmt_sig(abs(value))}"


def _round_params_sig(params: dict) -> dict:
    rounded: dict = {"type": params["type"]}
    for key, value in params.items():
        if key == "type":
            continue
        rounded[key] = _round_sig(float(value), digits=2)
    return rounded


def _build_supply_from_params(params: dict) -> tuple[callable, str]:
    spec_type = params["type"]
    if spec_type == "linear":
        a, b = float(params["a"]), float(params["b"])
        return lambda x: a * x + b, f"p_A(x)={_fmt_sig(a)}x{_signed_sig(b)}"

    if spec_type == "quadratic":
        a, b, c = float(params["a"]), float(params["b"]), float(params["c"])
        return (
            lambda x: a * (x ** 2) + b * x + c,
            f"p_A(x)={_fmt_sig(a)}x^2+{_fmt_sig(b)}x+{_fmt_sig(c)}",
        )

    a, rate, c = float(params["A"]), float(params["rate"]), float(params["c"])
    return (
        lambda x: a * math.exp(-rate * x) + c,
        f"p_A(x)={_fmt_sig(a)}\\cdot e^{{-{_fmt_sig(rate)}x}}+{_fmt_sig(c)}",
    )


def _build_demand_from_params(params: dict) -> tuple[callable, str, float]:
    spec_type = params["type"]
    if spec_type == "linear":
        a, b = float(params["a"]), float(params["b"])
        demand_fn = lambda x: a * x + b
        return demand_fn, f"p_N(x)={_fmt_sig(a)}x{_signed_sig(b)}", b

    if spec_type == "quadratic":
        a, b, c = float(params["a"]), float(params["b"]), float(params["c"])
        demand_fn = lambda x: a * (x ** 2) + b * x + c
        return (
            demand_fn,
            f"p_N(x)={_fmt_sig(a)}x^2{_signed_sig(b)}x{_signed_sig(c)}",
            c,
        )

    a, rate, c = float(params["A"]), float(params["rate"]), float(params["c"])
    demand_fn = lambda x: a * math.exp(-rate * x) + c
    return (
        demand_fn,
        f"p_N(x)={_fmt_sig(a)}\\cdot e^{{-{_fmt_sig(rate)}x}}{_signed_sig(c)}",
        a + c,
    )


class MarketEquilibriumAbschoepfungKRBerechnungBetragGenerator(TaskGenerator):
    generator_key = "analysis.marktgleichgewicht_vertiefung.abschoepfung_kr_berechnung_betrag"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used_params: set[tuple] = set()

        for _ in range(count):
            while True:
                (
                    _supply_fn,
                    _demand_fn,
                    _demand_derivative_fn,
                    _supply_latex,
                    _demand_latex,
                    market_key,
                    _min_price,
                    _max_price,
                    _sat_quantity,
                    _eq_x,
                    _eq_p,
                    _x2,
                    _p2,
                    supply_params,
                    demand_params,
                ) = _sample_market_params(rng)

                if market_key in used_params:
                    continue

                supply_params = _round_params_sig(supply_params)
                demand_params = _round_params_sig(demand_params)
                supply_fn, supply_latex = _build_supply_from_params(supply_params)
                demand_fn, demand_latex, max_price = _build_demand_from_params(demand_params)

                sat_quantity = _find_root_in_interval(demand_fn, start=0.0, end=2000.0)
                if sat_quantity is None or sat_quantity <= 1.5:
                    continue

                eq_x = _find_root_in_interval(
                    lambda x: supply_fn(x) - demand_fn(x),
                    start=0.0,
                    end=min(2000.0, max(18.0, sat_quantity * 1.05)),
                )
                if eq_x is None or eq_x <= 0.5:
                    continue

                eq_p = supply_fn(eq_x)
                if not (0.2 < eq_p < max_price - 0.2):
                    continue

                # betrag muss deutlich ueber eq_p UND deutlich unter max_price liegen
                preis_spanne = max_price - eq_p
                min_abstand = max(1.0, preis_spanne * 0.2)
                preis_untergrenze = math.ceil(eq_p + min_abstand)
                preis_obergrenze = math.floor(max_price - min_abstand)
                if preis_untergrenze > preis_obergrenze:
                    continue

                betrag = float(rng.randint(preis_untergrenze, preis_obergrenze))

                if not (eq_p + min_abstand <= betrag <= max_price - min_abstand):
                    continue

                nachfragemenge = _find_root_in_interval(
                    lambda x: demand_fn(x) - betrag,
                    start=0.0,
                    end=min(2000.0, max(18.0, sat_quantity * 1.05)),
                )
                if nachfragemenge is None or not (0.2 <= nachfragemenge < eq_x - 0.05):
                    continue

                abschoepfung = (betrag - eq_p) * nachfragemenge
                if abschoepfung <= 0:
                    continue

                used_params.add(market_key)
                break

            max_x = nice_axis_max(eq_x * 1.25)
            max_y = nice_axis_max(max(max_price, betrag) * 1.1)

            tasks.append(
                Task(
                    einleitung=(
                        "Gegeben sind die Angebots- und Nachfragefunktion:"
                        f"{_align_equations([supply_latex, demand_latex])}"
                        "Durch einen Teilmarkt soll ein Teil der Konsumentenrente abgeschöpft werden. "
                        f"Dazu wird auf dem Teilmarkt ein Preis von {_fmt_number(betrag, max_decimals=0)} GE festgelegt."
                    ),
                    fragen=[
                        "Bestimmen Sie (auf 2 NKS gerundet) den abgeschöpften Teil der Konsumentenrente.",
                    ],
                    antworten=[
                        _num_tol(abschoepfung, tolerance=0.1),
                    ],
                    visual={
                        "type": "plot",
                        "spec": {
                            "type": "market-abschoepfung",
                            "params": {
                                "supply": supply_params,
                                "demand": demand_params,
                                "eqX": round(eq_x, 4),
                                "eqP": round(eq_p, 4),
                                "x2": round(nachfragemenge, 4),
                                "p2": round(betrag, 4),
                                "maxX": max_x,
                                "maxY": max_y,
                            },
                            "layout": {
                                "title": "Preisdifferenzierung",
                                "xaxis": {"title": "Menge x"},
                                "yaxis": {"title": "Preis p"},
                            },
                            "width": 900,
                            "height": 520,
                            "scale": 1,
                        },
                    },
                )
            )

        return tasks