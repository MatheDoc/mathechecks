import math
import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.marktgleichgewicht_vertiefung.shared import (
    _align_equations,
    _kennzahlen_items_allgemein,
    _sample_market_params,
    _ueberschuss_item,
)


class MarketEquilibriumKennzahlenRechnerischLQEGenerator(TaskGenerator):
    generator_key = "analysis.marktgleichgewicht_vertiefung.kennzahlen_rechnerisch_linearquadratischexp"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used_keys: set[tuple] = set()

        for _ in range(count):
            while True:
                (
                    supply_fn,
                    demand_fn,
                    _demand_derivative_fn,
                    supply_latex,
                    demand_latex,
                    market_key,
                    min_price,
                    max_price,
                    sat_quantity,
                    eq_x,
                    eq_p,
                    _x2,
                    _p2,
                    _supply_params,
                    _demand_params,
                ) = _sample_market_params(rng)
                if market_key in used_keys:
                    continue

                supply_key = market_key[0]
                supply_ceiling = float(supply_key[3]) if supply_key[0] == "exp" else None
                ueberschuss = _ueberschuss_item(
                    rng,
                    supply_fn=supply_fn,
                    demand_fn=demand_fn,
                    min_price=min_price,
                    max_price=max_price,
                    eq_x=eq_x,
                    eq_p=eq_p,
                    supply_ceiling=supply_ceiling,
                )
                if ueberschuss is None:
                    continue
                used_keys.add(market_key)
                break

            # Rechnen mit auf 2 NKS gerundeten x_G, p_G (je ±0,005) soll akzeptiert werden.
            revenue_tol = math.ceil(max(0.1, 0.005 * (eq_x + eq_p) + 0.01) * 100 - 1e-9) / 100
            items = _kennzahlen_items_allgemein(
                min_price=min_price,
                max_price=max_price,
                sat_quantity=sat_quantity,
                eq_quantity=eq_x,
                eq_price=eq_p,
                x_tolerance=0.1,
                y_tolerance=0.1,
                revenue_tolerance=revenue_tol,
            )
            items.append(ueberschuss)

            tasks.append(
                Task(
                    einleitung=(
                        "Gegeben sind die Angebots- und Nachfragefunktion ($ x $ in ME, $ p $ in GE/ME):"
                        f"{_align_equations([supply_latex, demand_latex])}"
                        "Bestimmen Sie (auf 2 NKS gerundet)"
                    ),
                    fragen=[question for question, _ in items],
                    antworten=[answer for _, answer in items],
                )
            )

        return tasks
