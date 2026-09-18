"""Check 02 – Zinseszins im Sachkontext (vier Teilfragen mit eigenen Zahlen, zufällige Reihenfolge)."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import (
    numerical_finanz_geld,
    numerical_finanz_laufzeit,
    numerical_finanz_zinssatz,
)
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.finanzmathematik.shared import (
    geld,
    jahren,
    mische_teilfragen,
    prozent,
    q_of,
    sample_kapital,
    sample_laufzeit,
    sample_zinssatz,
    schoen,
    zinseszins_k0,
    zinseszins_kn,
    zinseszins_n,
    zinseszins_p,
)
from aufgaben.generators.finanzmathematik.szenarien import Szenario, szenario_folge

_T_KN = (
    "{S} legt {k0} zu einem Zinssatz von {p} an. Über welchen Betrag kann {pron} nach {n} verfügen?",
    "{S} zahlt {k0} auf ein Festgeldkonto ein, das mit {p} jährlich verzinst wird. Wie hoch ist das Guthaben nach {n}?",
)
_T_K0 = (
    "{S} möchte in {n} über {kn} verfügen. Welchen Betrag muss {pron} heute zu {p} anlegen?",
    "{S} soll in {n} eine Zahlung von {kn} leisten. Welcher Betrag müsste dafür heute bei einem Zinssatz von {p} zurückgelegt werden?",
)
_T_P = (
    "{S} hat vor {n} einen Betrag von {k0} angelegt; heute beträgt das Guthaben {kn}. Mit welchem Zinssatz wurde das Kapital verzinst?",
    "{S} hat {k0} angelegt. Nach {n} sind daraus {kn} geworden. Welcher jährliche Zinssatz liegt zugrunde?",
)
_T_N = (
    "{S} legt {k0} zu {p} an. Nach wie vielen Jahren ist das Kapital auf {kn} angewachsen?",
    "{S} zahlt {k0} auf ein mit {p} verzinstes Konto ein und benötigt {kn} {zweck}. Wie lange muss das Geld angelegt bleiben?",
)


def _fill(template: str, sz: Szenario, **werte: str) -> str:
    return template.format(S=sz.subjekt, pron=sz.pron, zweck=sz.zweck_anlage, **werte)


class ZinseszinsSachaufgabenGenerator(TaskGenerator):
    generator_key = "finanzmathematik.zinseszinsrechnung.zinseszins_sachaufgaben"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for sz in szenario_folge(rng, count):
            stufe = sz.stufe
            paare: list[tuple[str, str]] = []

            k0 = sample_kapital(rng, stufe)
            p = sample_zinssatz(rng)
            n = sample_laufzeit(rng)
            paare.append((
                _fill(rng.choice(_T_KN), sz, k0=geld(k0), p=prozent(p), n=jahren(n)),
                numerical_finanz_geld(zinseszins_kn(k0, q_of(p), n)),
            ))

            k0 = sample_kapital(rng, stufe)
            p = sample_zinssatz(rng)
            n = sample_laufzeit(rng)
            kn = schoen(zinseszins_kn(k0, q_of(p), n), stufe)
            paare.append((
                _fill(rng.choice(_T_K0), sz, kn=geld(kn), p=prozent(p), n=jahren(n)),
                numerical_finanz_geld(zinseszins_k0(kn, q_of(p), n)),
            ))

            k0 = sample_kapital(rng, stufe)
            p = sample_zinssatz(rng)
            n = sample_laufzeit(rng)
            kn = schoen(zinseszins_kn(k0, q_of(p), n), stufe)
            paare.append((
                _fill(rng.choice(_T_P), sz, k0=geld(k0), kn=geld(kn), n=jahren(n)),
                numerical_finanz_zinssatz(zinseszins_p(k0, kn, n)),
            ))

            k0 = sample_kapital(rng, stufe)
            p = sample_zinssatz(rng)
            n = sample_laufzeit(rng)
            kn = schoen(zinseszins_kn(k0, q_of(p), n), stufe)
            paare.append((
                _fill(rng.choice(_T_N), sz, k0=geld(k0), kn=geld(kn), p=prozent(p)),
                numerical_finanz_laufzeit(zinseszins_n(k0, kn, q_of(p))),
            ))

            fragen, antworten = mische_teilfragen(rng, paare)
            tasks.append(Task(einleitung=sz.intro_anlage, fragen=fragen, antworten=antworten))

        return tasks
