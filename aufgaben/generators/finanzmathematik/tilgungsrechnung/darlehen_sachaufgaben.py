"""Check 04 – Darlehen im Sachkontext (vier Teilfragen: A, K_0, n, RK_k; zufällige Reihenfolge)."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_finanz_geld, numerical_finanz_laufzeit
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.finanzmathematik.shared import (
    annuitaet,
    annuitaet_k0,
    annuitaet_n,
    geld,
    mische_teilfragen,
    prozent,
    q_of,
    restschuld,
    sample_darlehen,
    sample_zinssatz,
    schoen,
)
from aufgaben.generators.finanzmathematik.szenarien import Szenario, szenario_folge

_T_A = (
    "{S} nimmt {zweck} ein Darlehen über {k0} zu {p} auf, das in {n} Jahren durch gleich hohe Jahresraten getilgt werden soll. Wie hoch ist die jährliche Rate?",
    "{S} finanziert eine Investition {zweck} mit einem Darlehen über {k0}. Die Bank verlangt {p} Zinsen; die Rückzahlung erfolgt durch Annuitätentilgung über {n} Jahre. Welcher Betrag ist jährlich für Zins und Tilgung zu zahlen?",
)
_T_K0 = (
    "{S} kann {zweck} jährlich höchstens {a} für Zins und Tilgung aufbringen. Welche Darlehenssumme ist bei {p} und einer Laufzeit von {n} Jahren möglich?",
    "{S} möchte {zweck} ein Darlehen aufnehmen und dafür {n} Jahre lang jährlich {a} zahlen. Welchen Betrag kann die Bank bei einem Zinssatz von {p} auszahlen?",
)
_T_N = (
    "{S} nimmt {zweck} ein Darlehen über {k0} zu {p} auf und zahlt jährlich eine Annuität von {a}. Nach wie vielen Jahren ist das Darlehen getilgt?",
    "{S} tilgt ein Darlehen über {k0} ({p}) mit jährlichen Zahlungen von {a}. Wie lange dauert die Rückzahlung?",
)
_T_RK = (
    "{S} tilgt ein Darlehen über {k0} zu {p} mit einer jährlichen Annuität von {a}. Welche Restschuld besteht nach {k} Jahren?",
    "{S} hat {zweck} ein Darlehen über {k0} aufgenommen ({p}) und zahlt jährlich {a}. Wie hoch ist die Restschuld nach der {k}. Zahlung?",
)


def _fill(template: str, sz: Szenario, **werte) -> str:
    return template.format(S=sz.subjekt, pron=sz.pron, zweck=sz.zweck_darlehen, **werte)


class DarlehenSachaufgabenGenerator(TaskGenerator):
    generator_key = "finanzmathematik.tilgungsrechnung.darlehen_sachaufgaben"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for sz in szenario_folge(rng, count):
            stufe = sz.stufe
            paare: list[tuple[str, str]] = []

            # A gesucht
            k0, p, n = sample_darlehen(rng, stufe), sample_zinssatz(rng), rng.randint(4, 30)
            paare.append((
                _fill(rng.choice(_T_A), sz, k0=geld(k0), p=prozent(p), n=n),
                numerical_finanz_geld(annuitaet(k0, q_of(p), n)),
            ))

            # K_0 gesucht
            k0, p, n = sample_darlehen(rng, stufe), sample_zinssatz(rng), rng.randint(4, 30)
            a = schoen(annuitaet(k0, q_of(p), n), stufe)
            paare.append((
                _fill(rng.choice(_T_K0), sz, a=geld(a), p=prozent(p), n=n),
                numerical_finanz_geld(annuitaet_k0(a, q_of(p), n)),
            ))

            # n gesucht
            while True:
                k0, p, n = sample_darlehen(rng, stufe), sample_zinssatz(rng), rng.randint(4, 30)
                a = schoen(annuitaet(k0, q_of(p), n), stufe)
                n_antwort = annuitaet_n(k0, a, q_of(p))
                if n_antwort is not None and n_antwort > 1.0:
                    break
            paare.append((
                _fill(rng.choice(_T_N), sz, k0=geld(k0), p=prozent(p), a=geld(a)),
                numerical_finanz_laufzeit(n_antwort),
            ))

            # RK_k gesucht
            while True:
                k0, p, n = sample_darlehen(rng, stufe), sample_zinssatz(rng), rng.randint(6, 30)
                a = schoen(annuitaet(k0, q_of(p), n), stufe)
                k = rng.randint(2, n - 2)
                rk = restschuld(k0, a, q_of(p), k)
                if 0 < rk < k0:
                    break
            paare.append((
                _fill(rng.choice(_T_RK), sz, k0=geld(k0), p=prozent(p), a=geld(a), k=k),
                numerical_finanz_geld(rk),
            ))

            fragen, antworten = mische_teilfragen(rng, paare)
            tasks.append(Task(einleitung=sz.intro_darlehen, fragen=fragen, antworten=antworten))

        return tasks
