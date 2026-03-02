import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.marktgleichgewicht_grundlagen.shared import (
    _build_market_visual,
    _kennzahlen_items,
    _sample_linear_market_parameters,
)


class MarketEquilibriumKennzahlenGraphischLinearGenerator(TaskGenerator):
    generator_key = "analysis.marktgleichgewicht_grundlagen.kennzahlen_graphisch_linear"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used_params: set[tuple[float, float, float, float]] = set()

        for _ in range(count):
            while True:
                (
                    supply_slope,
                    demand_slope,
                    min_price,
                    max_price,
                    sat_quantity,
                    eq_quantity,
                    eq_price,
                ) = _sample_linear_market_parameters(rng)

                key = (supply_slope, demand_slope, min_price, max_price)
                if key in used_params:
                    continue
                used_params.add(key)
                break

            visual = _build_market_visual(
                supply_slope=supply_slope,
                demand_slope=demand_slope,
                min_price=min_price,
                max_price=max_price,
                sat_quantity=sat_quantity,
                eq_quantity=eq_quantity,
                eq_price=eq_price,
            )

            items = _kennzahlen_items(
                min_price=min_price,
                max_price=max_price,
                sat_quantity=sat_quantity,
                eq_quantity=eq_quantity,
                eq_price=eq_price,
                tolerance=0.5,
            )

            tasks.append(
                Task(
                    einleitung=(
                        "Das Diagramm zeigt die Graphen der Angebots- und Nachfragefunktion. "
                        "Bestimmen Sie"
                    ),
                    fragen=[question for question, _ in items],
                    antworten=[answer for _, answer in items],
                    visual=visual,
                )
            )

        return tasks
