import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.marktgleichgewicht_grundlagen.shared import (
    _align_equations,
    _fmt_number,
    _latex_demand,
    _latex_supply,
    _num_tol,
    _sample_linear_market_parameters,
)
from aufgaben.generators.analysis.shared_numbers import uniform_sig


class MarketEquilibriumUngleichgewichtBestimmungGenerator(TaskGenerator):
    generator_key = "analysis.marktgleichgewicht_grundlagen.marktungleichgewicht_bestimmung"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used_params: set[tuple[float, float, float, float, float]] = set()

        for _ in range(count):
            while True:
                (
                    supply_slope,
                    demand_slope,
                    min_price,
                    max_price,
                    _,
                    eq_quantity,
                    eq_price,
                ) = _sample_linear_market_parameters(rng)

                mode = rng.choice(["nachfrage", "angebot"])
                if mode == "nachfrage":
                    margin = max(2.0, (eq_price - min_price) * uniform_sig(rng, 0.25, 0.8))
                    market_price = round(max(0.0, eq_price - margin))
                else:
                    margin = max(2.0, (max_price - eq_price) * uniform_sig(rng, 0.25, 0.8))
                    market_price = round(min(max_price - 1.0, eq_price + margin))

                if abs(market_price - eq_price) < 0.75:
                    continue

                x_supply = (market_price - min_price) / supply_slope
                x_demand = (max_price - market_price) / demand_slope

                if market_price < eq_price:
                    situation = "Nachfrageüberschuss"
                    surplus_amount = x_demand - x_supply
                else:
                    situation = "Angebotsüberschuss"
                    surplus_amount = x_supply - x_demand

                if surplus_amount <= 0.25:
                    continue

                key = (supply_slope, demand_slope, min_price, max_price, market_price)
                if key in used_params:
                    continue
                used_params.add(key)
                break

            mc_answer = (
                "{1:MC:~=Nachfrageüberschuss~Angebotsüberschuss}"
                if situation == "Nachfrageüberschuss"
                else "{1:MC:~Nachfrageüberschuss~=Angebotsüberschuss}"
            )

            tasks.append(
                Task(
                    einleitung=(
                        "Gegeben sind die Angebots- und Nachfragefunktion:"
                        f"{_align_equations([_latex_supply(supply_slope, min_price), _latex_demand(demand_slope, max_price)])}"
                        f"Auf dem Markt wird ein Preis von {_fmt_number(market_price, max_decimals=0)} GE festgelegt."
                    ),
                    fragen=[
                        "Geben Sie die Marktsituation an.",
                        "Bestimmen Sie (auf 2 NKS gerundet) den Nachfrage- oder Angebotsüberschuss.",
                    ],
                    antworten=[
                        mc_answer,
                        _num_tol(surplus_amount, tolerance=0.1),
                    ],
                )
            )

        return tasks
