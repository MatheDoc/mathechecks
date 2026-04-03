import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.marktgleichgewicht_grundlagen.shared import _fmt_number
from aufgaben.generators.analysis.marktgleichgewicht_vertiefung.shared import (
    _align_equations,
    _consumer_surplus,
    _num_tol,
    _producer_surplus,
    _sample_market_params,
)


class MarketEquilibriumRentenBestimmungPRKRGenerator(TaskGenerator):
    generator_key = "analysis.marktgleichgewicht_vertiefung.renten_bestimmung_prkr"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used_params: set[tuple] = set()

        for _ in range(count):
            while True:
                (
                    supply_fn,
                    demand_fn,
                    _demand_derivative_fn,
                    supply_latex,
                    demand_latex,
                    market_key,
                    _min_price,
                    _max_price,
                    _sat_quantity,
                    eq_x,
                    eq_p,
                    _x2,
                    _p2,
                    _supply_params,
                    _demand_params,
                ) = _sample_market_params(rng)
                key = market_key
                if key in used_params:
                    continue
                kr_value = _consumer_surplus(demand_fn, eq_x, eq_p)
                pr_value = _producer_surplus(supply_fn, eq_x, eq_p)
                if kr_value <= 0 or pr_value <= 0:
                    continue
                used_params.add(key)
                break

            tasks.append(
                Task(
                    einleitung=(
                        "Gegeben sind die Angebots- und Nachfragefunktion:"
                        f"{_align_equations([supply_latex, demand_latex])}"
                        f"Die Gleichgewichtsmenge beträgt {_fmt_number(eq_x)} ME "
                        f"und der Gleichgewichtspreis {_fmt_number(eq_p)} GE. Bestimmen Sie (auf 2 NKS gerundet)"
                    ),
                    fragen=[
                        "die Konsumentenrente.",
                        "die Produzentenrente.",
                    ],
                    antworten=[
                        _num_tol(kr_value, tolerance=0.1),
                        _num_tol(pr_value, tolerance=0.1),
                    ],
                )
            )

        return tasks
