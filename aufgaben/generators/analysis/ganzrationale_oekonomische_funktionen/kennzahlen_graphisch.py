"""Kennzahlen ökonomischer Funktionen graphisch bestimmen (Polypol und Monopol gemischt).

Gerade Aufgabenindizes: Angebotspolypol (``kennzahlen_graphisch_e1k3``),
ungerade: Angebotsmonopol (``kennzahlen_graphisch_e2k3``). Je Aufgabe sechs
Teilfragen (Auswahl siehe ``_select_kennzahlen_items`` in ``shared.py``).
"""

import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.kennzahlen_graphisch_e1k3 import (
    polypol_graph_task,
)
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.kennzahlen_graphisch_e2k3 import (
    monopol_graph_task,
)
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.szenarien import (
    szenario_folge,
)


class EconomicPolynomialKennzahlenGraphischGenerator(TaskGenerator):
    """Erzeugt gemischte graphische Kennzahlen-Aufgaben mit visual.spec."""

    generator_key = "analysis.ganzrationale_oekonomische_funktionen.kennzahlen_graphisch"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        szenarien = szenario_folge(rng, count)
        tasks: list[Task] = []
        used: set = set()

        for index in range(count):
            variante = index // 2
            if index % 2 == 0:
                tasks.append(polypol_graph_task(rng, used, szenarien[index].polypol, variante))
            else:
                tasks.append(monopol_graph_task(rng, used, szenarien[index].monopol, variante))

        return tasks
