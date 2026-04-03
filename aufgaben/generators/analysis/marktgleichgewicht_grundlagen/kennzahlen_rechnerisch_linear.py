import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.marktgleichgewicht_grundlagen.shared import (
    _align_equations,
    _kennzahlen_items,
    _latex_demand,
    _latex_supply,
    _sample_linear_market_parameters,
)


class MarketEquilibriumKennzahlenRechnerischLinearGenerator(TaskGenerator):
    generator_key = "analysis.marktgleichgewicht_grundlagen.kennzahlen_rechnerisch_linear"

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

            intro = (
                "Gegeben sind die Angebots- und Nachfragefunktion:"
                f"{_align_equations([_latex_supply(supply_slope, min_price), _latex_demand(demand_slope, max_price)])}"
                "Bestimmen Sie (auf 2 NKS gerundet)"
            )

            items = _kennzahlen_items(
                min_price=min_price,
                max_price=max_price,
                sat_quantity=sat_quantity,
                eq_quantity=eq_quantity,
                eq_price=eq_price,
                tolerance=0.1,
            )

            tasks.append(
                Task(
                    einleitung=intro,
                    fragen=[question for question, _ in items],
                    antworten=[answer for _, answer in items],
                )
            )

        return tasks
