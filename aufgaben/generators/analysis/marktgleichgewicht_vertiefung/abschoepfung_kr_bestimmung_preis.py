import random

from aufgaben.core.tolerances import nice_axis_max
from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.marktgleichgewicht_vertiefung.shared import (
    _num_tol,
    _sample_market_params,
)


class MarketEquilibriumAbschoepfungKRBestimmungPreisGenerator(TaskGenerator):
    generator_key = "analysis.marktgleichgewicht_vertiefung.abschoepfung_kr_bestimmung_preis"

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
                    supply_latex,
                    demand_latex,
                    market_key,
                    _min_price,
                    max_price,
                    _sat_quantity,
                    eq_x,
                    eq_p,
                    x2,
                    p2,
                    supply_params,
                    demand_params,
                ) = _sample_market_params(rng)
                key = market_key
                if key in used_params:
                    continue
                used_params.add(key)
                break

            max_x = nice_axis_max(eq_x * 1.25)
            max_y = nice_axis_max(max(max_price, p2) * 1.1)

            fragen_antworten = [
                ("die zum Preis $ p_2 $ nachgefragte Menge $ x_2 $.", _num_tol(x2, tolerance=0.1)),
                ("den Preis $ p_2 $.", _num_tol(p2, tolerance=0.1)),
            ]
            fragen = [f for f, _ in fragen_antworten]
            antworten = [a for _, a in fragen_antworten]

            tasks.append(
                Task(
                    einleitung=(
                        "Gegeben sind die Angebotsfunktion <br/></p>"
                        f"{supply_latex}"
                        "<br/></p> und die Nachfragefunktion <br/></p>"
                        f"{demand_latex}"
                        ".</p> "
                        "<p>Mit Hilfe einer Preisdifferenzierung wird der Markt in zwei Teilmärkte "
                        "aufgeteilt. Die Konsumentenrente ergibt sich als Summe aus KR1 und KR2. "
                        "Auf dem ersten Teilmarkt gilt der Gleichgewichtspreis $p_G$. "
                        "Auf dem zweiten Teilmarkt wird ein Preis $p_2$ so festgelegt, "
                        "dass die Konsumentenrente maximal abgeschöpft wird.</p> "
                        "<p>Bestimmen Sie (auf 2 NKS gerundet)"
                    ),
                    fragen=fragen,
                    antworten=antworten,
                    visual={
                        "type": "plot",
                        "spec": {
                            "type": "market-abschoepfung",
                            "params": {
                                "supply": supply_params,
                                "demand": demand_params,
                                "eqX": round(eq_x, 4),
                                "eqP": round(eq_p, 4),
                                "x2": round(x2, 4),
                                "p2": round(p2, 4),
                                "maxX": max_x,
                                "maxY": max_y,
                            },
                            "layout": {
                                "title": "Preisdifferenzierung mit KR1 und KR2",
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
