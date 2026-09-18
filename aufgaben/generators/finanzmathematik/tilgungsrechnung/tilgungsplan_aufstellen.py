"""Check 01 – Tilgungsplan aufstellen (kurze Laufzeit, Annuität gegeben, Rundungsdifferenz)."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_finanz_tilgungsplan
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.finanzmathematik.shared import (
    TABELLEN_KOPF_TILGUNGSPLAN,
    annuitaet,
    geld,
    prozent,
    q_of,
    rund2,
    sample_darlehen,
    sample_zinssatz,
    tabelle_html,
    tilgungsplan,
)
from aufgaben.generators.finanzmathematik.szenarien import szenario_folge


class TilgungsplanAufstellenGenerator(TaskGenerator):
    generator_key = "finanzmathematik.tilgungsrechnung.tilgungsplan_aufstellen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for sz in szenario_folge(rng, count):
            k0 = sample_darlehen(rng, sz.stufe)
            p = sample_zinssatz(rng)
            n = rng.randint(3, 5)
            a = rund2(annuitaet(k0, q_of(p), n))
            plan = tilgungsplan(k0, p, a, n)
            leer = [[str(j)] + ["?"] * 5 for j in range(1, n + 1)]

            intro = (
                f"{sz.subjekt} nimmt {sz.zweck_darlehen} ein Darlehen über {geld(k0)} auf. "
                f"Der Zinssatz beträgt {prozent(p)}, die Rückzahlung erfolgt durch Annuitätentilgung in {n} Jahren "
                f"mit einer Annuität von {geld(a, cents=True)}. Stellen Sie den Tilgungsplan auf "
                f"(Rundung auf Cent, gerundete Werte weiterverwenden)."
                + tabelle_html(TABELLEN_KOPF_TILGUNGSPLAN, leer)
            )

            mitte = rng.randint(2, n - 1)
            fragen = [
                "Wie hoch sind die Zinsen im 1. Jahr?",
                "Wie hoch ist die Tilgung im 1. Jahr?",
                f"Wie hoch ist die Restschuld am Ende des {mitte}. Jahres?",
                f"Wie hoch ist die Tilgung im {n}. Jahr?",
                f"Wie hoch ist die Annuität im {n}. Jahr?",
                "Um welchen Betrag weicht die Annuität des letzten Jahres von der vereinbarten Annuität ab (Rundungsdifferenz, positiver Wert)?",
            ]
            antworten = [
                numerical_finanz_tilgungsplan(plan[0].zinsen),
                numerical_finanz_tilgungsplan(plan[0].tilgung),
                numerical_finanz_tilgungsplan(plan[mitte - 1].rk_ende),
                numerical_finanz_tilgungsplan(plan[-1].tilgung),
                numerical_finanz_tilgungsplan(plan[-1].annuitaet),
                numerical_finanz_tilgungsplan(abs(plan[-1].annuitaet - a)),
            ]
            tasks.append(Task(einleitung=intro, fragen=fragen, antworten=antworten))

        return tasks
