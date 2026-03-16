import random

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
                used_params.add(key)
                break

            max_x = max(12.0, sat_quantity * 1.1)
            max_y = round(max(max_price, eq_p) * 1.12, 3)

            items = _kennzahlen_items_allgemein(
                min_price=min_price,
                max_price=max_price,
                sat_quantity=sat_quantity,
                eq_quantity=eq_x,
                eq_price=eq_p,
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
