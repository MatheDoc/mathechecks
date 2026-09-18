"""Check 03 – Restschuldformel: Restschuld nach k Jahren, Zins/Tilgung im Folgejahr, Gesamtzinsen."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_finanz_geld
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.finanzmathematik.shared import (
    annuitaet,
    geld,
    prozent,
    q_of,
    restschuld,
    rund2,
    sample_darlehen,
    sample_zinssatz,
)
from aufgaben.generators.finanzmathematik.szenarien import szenario_folge


class RestschuldformelGenerator(TaskGenerator):
    generator_key = "finanzmathematik.tilgungsrechnung.restschuldformel"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for sz in szenario_folge(rng, count):
            k0 = sample_darlehen(rng, sz.stufe)
            p = sample_zinssatz(rng)
            n = rng.randint(8, 30)
            k = rng.randint(3, n - 2)
            q = q_of(p)
            a = rund2(annuitaet(k0, q, n))
            rk = restschuld(k0, a, q, k)
            zinsen_folge = rk * (q - 1.0)

            intro = (
                f"{sz.subjekt} nimmt {sz.zweck_darlehen} ein Annuitätendarlehen über {geld(k0)} auf. "
                f"Der Zinssatz beträgt {prozent(p)}, die Laufzeit {n} Jahre, die jährliche Annuität {geld(a, cents=True)}."
            )
            fragen = [
                f"Wie hoch ist die Restschuld nach {k} Jahren?",
                f"Wie hoch sind die Zinsen im {k + 1}. Jahr?",
                f"Wie hoch ist die Tilgung im {k + 1}. Jahr?",
                "Wie viel Zinsen werden über die gesamte Laufzeit insgesamt gezahlt?",
            ]
            antworten = [
                numerical_finanz_geld(rk),
                numerical_finanz_geld(zinsen_folge),
                numerical_finanz_geld(a - zinsen_folge),
                numerical_finanz_geld(n * a - k0),
            ]
            tasks.append(Task(einleitung=intro, fragen=fragen, antworten=antworten))

        return tasks
