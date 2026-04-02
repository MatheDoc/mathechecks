import random

from aufgaben.core.tolerances import graph_read_tolerance_from_span, nice_axis_max
from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.marktgleichgewicht_vertiefung.shared import (
    _kennzahlen_items_allgemein,
    _sample_market_params,
)


class MarketEquilibriumKennzahlenGraphischAllgemeinGenerator(TaskGenerator):
    generator_key = "analysis.marktgleichgewicht_vertiefung.kennzahlen_graphisch_allgemein"

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
                    min_price,
                    max_price,
                    sat_quantity,
                    eq_x,
                    eq_p,
                    _x2,
                    _p2,
                    supply_params,
                    demand_params,
                ) = _sample_market_params(rng)
                key = market_key
                if key in used_params:
                    continue
                # Gleichgewichtspreis soll bei mind. 20% der Y-Achse liegen
                if eq_p < max_price * 0.2:
                    continue
                used_params.add(key)
                break

            max_x = nice_axis_max(sat_quantity * 1.08)
            max_y = nice_axis_max(max_price * 1.08)
            tolerance_x = graph_read_tolerance_from_span(max_x)
            tolerance_y = graph_read_tolerance_from_span(max_y)

            items = _kennzahlen_items_allgemein(
                min_price=min_price,
                max_price=max_price,
                sat_quantity=sat_quantity,
                eq_quantity=eq_x,
                eq_price=eq_p,
                x_tolerance=tolerance_x,
                y_tolerance=tolerance_y,
            )

            tasks.append(
                Task(
                    einleitung="Das Diagramm zeigt die Graphen der Angebots- und Nachfragefunktion. Bestimmen Sie",
                    fragen=[question for question, _ in items],
                    antworten=[answer for _, answer in items],
                    visual={
                        "type": "plot",
                        "spec": {
                            "type": "market-equilibrium",
                            "params": {
                                "supply": supply_params,
                                "demand": demand_params,
                                "eqX": round(eq_x, 4),
                                "eqP": round(eq_p, 4),
                                "satX": round(sat_quantity, 4),
                                "maxX": round(max_x, 3),
                                "maxY": max_y,
                            },
                            "layout": {
                                "title": "Angebots- und Nachfragefunktion",
                                "xaxis": {"title": "Menge x", "range": [0, round(max_x, 3)]},
                                "yaxis": {"title": "Preis p", "range": [0, max_y]},
                            },
                            "width": 900,
                            "height": 520,
                            "scale": 1,
                        },
                    },
                )
            )

        return tasks
