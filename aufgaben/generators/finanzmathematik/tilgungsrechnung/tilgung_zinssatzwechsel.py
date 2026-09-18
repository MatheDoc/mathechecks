"""Check 06 – Zinssatzwechsel im Annuitätendarlehen (Restschuld, neue Annuität bei unveränderter Laufzeit)."""

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


class TilgungZinssatzwechselGenerator(TaskGenerator):
    generator_key = "finanzmathematik.tilgungsrechnung.tilgung_zinssatzwechsel"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for sz in szenario_folge(rng, count):
            k0 = sample_darlehen(rng, sz.stufe)
            p1 = sample_zinssatz(rng)
            p2 = sample_zinssatz(rng, ohne=p1)
            n = rng.randint(8, 25)
            k = rng.randint(3, n - 3)
            q1, q2 = q_of(p1), q_of(p2)

            a1 = rund2(annuitaet(k0, q1, n))
            rk = restschuld(k0, a1, q1, k)
            a2 = annuitaet(rk, q2, n - k)
            zinsen_neu = rk * (q2 - 1.0)

            intro = (
                f"{sz.subjekt} nimmt {sz.zweck_darlehen} ein Annuitätendarlehen über {geld(k0)} mit einer Laufzeit "
                f"von {n} Jahren auf. Der Zinssatz beträgt zunächst {prozent(p1)}. Nach {k} Jahren wird der Zinssatz "
                f"auf {prozent(p2)} angepasst; die Gesamtlaufzeit bleibt unverändert."
            )
            fragen = [
                "Wie hoch ist die ursprüngliche Annuität?",
                f"Wie hoch ist die Restschuld nach {k} Jahren?",
                f"Wie hoch ist die neue Annuität für die verbleibenden {n - k} Jahre?",
                f"Wie hoch sind die Zinsen im {k + 1}. Jahr?",
                f"Wie hoch ist die Tilgung im {k + 1}. Jahr?",
            ]
            antworten = [
                numerical_finanz_geld(a1),
                numerical_finanz_geld(rk),
                numerical_finanz_geld(a2),
                numerical_finanz_geld(zinsen_neu),
                numerical_finanz_geld(a2 - zinsen_neu),
            ]
            tasks.append(Task(einleitung=intro, fragen=fragen, antworten=antworten))

        return tasks
