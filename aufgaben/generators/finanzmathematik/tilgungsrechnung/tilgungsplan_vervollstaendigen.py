"""Check 05 – Lückenhaften Tilgungsplan vervollständigen (vorwärts mit unbekanntem Zinssatz oder rückwärts)."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import (
    numerical,
    numerical_finanz_tilgungsplan,
    numerical_finanz_zinssatz,
)
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.finanzmathematik.shared import (
    TABELLEN_KOPF_TILGUNGSPLAN,
    annuitaet,
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

_ALLE = {"rk_anfang", "zinsen", "tilgung", "annuitaet", "rk_ende"}


def _rueckwaerts(value: float) -> str:
    # Rückwärtsrechnung (RK_{k-1} = (RK_k + A)/q) trifft den zeilenweise gerundeten Plan nur bis auf wenige Cent.
    return numerical(value, tolerance=0.05, decimals=2)


class TilgungsplanVervollstaendigenGenerator(TaskGenerator):
    generator_key = "finanzmathematik.tilgungsrechnung.tilgungsplan_vervollstaendigen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index, sz in enumerate(szenario_folge(rng, count)):
            k0 = sample_darlehen(rng, sz.stufe)
            p = sample_zinssatz(rng)
            n = rng.randint(6, 20)
            a = rund2(annuitaet(k0, q_of(p), n))
            plan = tilgungsplan(k0, p, a, n)
            k = rng.randint(2, n - 2)
            z1, z2 = plan[k - 1], plan[k]
            vorwaerts = index % 2 == 0

            if vorwaerts:
                tabelle = tabelle_html(
                    TABELLEN_KOPF_TILGUNGSPLAN,
                    [
                        plan_zeile_html(z1, _ALLE - {"rk_anfang", "zinsen", "annuitaet"}),
                        plan_zeile_html(z2, _ALLE),
                    ],
                )
                intro = (
                    f"{sz.subjekt} zahlt {sz.zweck_darlehen} ein Annuitätendarlehen zurück. "
                    f"Vom Tilgungsplan ist nur der folgende Auszug bekannt (Beträge in €, auf Cent gerundet). "
                    f"Vervollständigen Sie die fehlenden Werte." + tabelle
                )
                fragen = [
                    "Mit welchem Zinssatz wird das Darlehen verzinst?",
                    f"Wie hoch ist die Tilgung im {k}. Jahr?",
                    f"Wie hoch ist die Restschuld am Ende des {k}. Jahres?",
                    f"Wie hoch sind die Zinsen im {k + 1}. Jahr?",
                    f"Wie hoch ist die Restschuld am Ende des {k + 1}. Jahres?",
                ]
                antworten = [
                    numerical_finanz_zinssatz(p),
                    numerical_finanz_tilgungsplan(z1.tilgung),
                    numerical_finanz_tilgungsplan(z1.rk_ende),
                    numerical_finanz_tilgungsplan(z2.zinsen),
                    numerical_finanz_tilgungsplan(z2.rk_ende),
                ]
            else:
                tabelle = tabelle_html(
                    TABELLEN_KOPF_TILGUNGSPLAN,
                    [
                        plan_zeile_html(z1, _ALLE),
                        plan_zeile_html(z2, _ALLE - {"zinsen", "tilgung", "rk_ende"}),
                    ],
                )
                intro = (
                    f"{sz.subjekt} zahlt {sz.zweck_darlehen} ein Annuitätendarlehen mit einem Zinssatz von {prozent(p)} zurück. "
                    f"Vom Tilgungsplan ist nur der folgende Auszug bekannt (Beträge in €, auf Cent gerundet). "
                    f"Vervollständigen Sie die fehlenden Werte – auch rückwärts." + tabelle
                )
                fragen = [
                    "Wie hoch ist die Annuität?",
                    f"Wie hoch ist die Restschuld am Ende des {k}. Jahres?",
                    f"Wie hoch ist die Restschuld zu Beginn des {k}. Jahres?",
                    f"Wie hoch sind die Zinsen im {k}. Jahr?",
                    f"Wie hoch ist die Tilgung im {k}. Jahr?",
                ]
                antworten = [
                    numerical_finanz_tilgungsplan(z2.annuitaet),
                    numerical_finanz_tilgungsplan(z2.rk_anfang),
                    _rueckwaerts(z1.rk_anfang),
                    _rueckwaerts(z1.zinsen),
                    _rueckwaerts(z1.tilgung),
                ]

            tasks.append(Task(einleitung=intro, fragen=fragen, antworten=antworten))

        return tasks
