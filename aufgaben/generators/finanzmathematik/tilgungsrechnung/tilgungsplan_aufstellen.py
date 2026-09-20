"""Check 01 – Tilgungsplan aufstellen (3 Jahre, Annuität auf Cent, kleine Rundungsdifferenz in der letzten Zeile)."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_finanz_tilgungsplan
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

_N = 3


class TilgungsplanAufstellenGenerator(TaskGenerator):
    generator_key = "finanzmathematik.tilgungsrechnung.tilgungsplan_aufstellen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for sz in szenario_folge(rng, count):
            # Bei 3 Zeilen liegt die Rundungsdifferenz bei 0–2 Cent; Kandidaten ohne Differenz werden verworfen,
            # damit die letzte Teilfrage etwas zu entdecken hat.
            while True:
                k0 = sample_darlehen(rng, sz.stufe)
                p = sample_zinssatz(rng)
                a = rund2(annuitaet(k0, q_of(p), _N))
                plan = tilgungsplan(k0, p, a, _N)
                diff = rund2(plan[-1].annuitaet - a)
                if diff != 0:
                    break
            leer = [[str(j)] + ["?"] * 5 for j in range(1, _N + 1)]

            intro = (
                f"{sz.subjekt} nimmt {sz.zweck_darlehen} ein Darlehen über {geld(k0)} auf. "
                f"Der Zinssatz beträgt {prozent(p)}, die Rückzahlung erfolgt durch Annuitätentilgung in {_N} Jahren "
                f"mit einer Annuität von {geld(a, cents=True)}. Stellen Sie den Tilgungsplan auf "
                f"(Rundung auf Cent, gerundete Werte weiterverwenden)."
                + tabelle_html(TABELLEN_KOPF_TILGUNGSPLAN, leer)
            )

            fragen = [
                "Wie hoch sind die Zinsen im 1. Jahr?",
                "Wie hoch ist die Tilgung im 1. Jahr?",
                "Wie hoch ist die Restschuld am Ende des 2. Jahres?",
                "Wie hoch sind die Zinsen im 3. Jahr?",
                "Wie hoch ist die Tilgung im 3. Jahr?",
                "Wie hoch ist die Annuität im 3. Jahr?",
                "Um welchen Betrag weicht die Annuität des letzten Jahres von der vereinbarten Annuität ab (Rundungsdifferenz, positiver Wert)?",
            ]
            antworten = [
                numerical_finanz_tilgungsplan(plan[0].zinsen),
                numerical_finanz_tilgungsplan(plan[0].tilgung),
                numerical_finanz_tilgungsplan(plan[1].rk_ende),
                numerical_finanz_tilgungsplan(plan[2].zinsen),
                numerical_finanz_tilgungsplan(plan[2].tilgung),
                numerical_finanz_tilgungsplan(plan[2].annuitaet),
                # Differenz ist 1–2 Cent; Standardtoleranz 0,01 würde auch 0 akzeptieren
                numerical(abs(diff), tolerance=0.001, decimals=3),
            ]
            tasks.append(Task(einleitung=intro, fragen=fragen, antworten=antworten))

        return tasks
