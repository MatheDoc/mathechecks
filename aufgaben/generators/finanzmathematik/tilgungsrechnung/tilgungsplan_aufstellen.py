"""Check 01 – Tilgungsplan aufstellen: die ersten beiden Zeilen eines Tilgungsplans (Annuität gegeben)."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_finanz_tilgungsplan
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.finanzmathematik.shared import (
    TABELLEN_KOPF_TILGUNGSPLAN,
    annuitaet,
    geld,
    plan_zeile_html,
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
            n = rng.randint(5, 10)
            a = rund2(annuitaet(k0, q_of(p), n))
            plan = tilgungsplan(k0, p, a, n)
            # Gegeben sind Darlehenssumme (Restschuld zu Beginn von Jahr 1) und Annuität; alles andere ist gesucht.
            zeilen = [
                plan_zeile_html(plan[0], {"zinsen", "tilgung", "rk_ende"}),
                plan_zeile_html(plan[1], {"rk_anfang", "zinsen", "tilgung", "rk_ende"}),
                ["…"] * 6,
            ]

            intro = (
                f"{sz.subjekt} nimmt {sz.zweck_darlehen} ein Darlehen über {geld(k0)} auf. "
                f"Der Zinssatz beträgt {prozent(p)}, die Rückzahlung erfolgt durch Annuitätentilgung in {n} Jahren "
                f"mit einer Annuität von {geld(a, cents=True)}. Stellen Sie die ersten beiden Zeilen des Tilgungsplans auf "
                f"(Rundung auf Cent, gerundete Werte weiterverwenden)."
                + tabelle_html(TABELLEN_KOPF_TILGUNGSPLAN, zeilen)
            )

            fragen = [
                "Wie hoch sind die Zinsen im 1. Jahr?",
                "Wie hoch ist die Tilgung im 1. Jahr?",
                "Wie hoch ist die Restschuld am Ende des 1. Jahres?",
                "Wie hoch sind die Zinsen im 2. Jahr?",
                "Wie hoch ist die Tilgung im 2. Jahr?",
                "Wie hoch ist die Restschuld am Ende des 2. Jahres?",
            ]
            antworten = [
                numerical_finanz_tilgungsplan(plan[0].zinsen),
                numerical_finanz_tilgungsplan(plan[0].tilgung),
                numerical_finanz_tilgungsplan(plan[0].rk_ende),
                numerical_finanz_tilgungsplan(plan[1].zinsen),
                numerical_finanz_tilgungsplan(plan[1].tilgung),
                numerical_finanz_tilgungsplan(plan[1].rk_ende),
            ]
            tasks.append(Task(einleitung=intro, fragen=fragen, antworten=antworten))

        return tasks
