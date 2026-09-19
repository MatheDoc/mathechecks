"""Check 04 – Rente im Sachkontext (vier Teilfragen mit eigenen Zahlen, zufällige Reihenfolge)."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_finanz_geld, numerical_finanz_laufzeit
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.finanzmathematik.shared import (
    geld,
    mische_teilfragen,
    prozent,
    q_of,
    rente_n_aus_barwert,
    rente_n_aus_endwert,
    rentenbarwert,
    rentenendwert,
    renten_faktor,
    sample_rate,
    sample_zinssatz,
    schoen,
    zeitpunkt_phrase,
)
from aufgaben.generators.finanzmathematik.szenarien import Szenario, szenario_folge

_T_RN = (
    "{S} zahlt {n} Jahre lang {zp} {r} auf ein Konto ein, das mit {p} verzinst wird. Über welchen Betrag verfügt {pron} am Ende der Laufzeit?",
    "{S} spart {zweck} und legt dafür {n} Jahre lang {zp} {r} zu {p} an. Wie hoch ist das Guthaben am Ende des letzten Jahres?",
)
_T_R0 = (
    "{S} möchte {n} Jahre lang {zp} {r} entnehmen können. Welcher Betrag muss dafür heute zu {p} angelegt werden?",
    "{S} soll {n} Jahre lang {zp} {r} erhalten. Welcher einmalige Betrag heute ist bei einem Zinssatz von {p} gleichwertig?",
)
_T_R_END = (
    "{S} möchte nach {n} Jahren über {rn} verfügen und zahlt dafür {zp} einen festen Betrag auf ein mit {p} verzinstes Konto ein. Wie hoch muss dieser Betrag sein?",
)
_T_R_BAR = (
    "{S} legt heute {r0} zu {p} an und möchte daraus {n} Jahre lang {zp} einen gleich hohen Betrag entnehmen, sodass das Kapital am Ende aufgebraucht ist. Wie hoch ist dieser Betrag?",
)
_T_N_END = (
    "{S} zahlt {zp} {r} auf ein mit {p} verzinstes Konto ein. Nach wie vielen Jahren ist ein Guthaben von {rn} erreicht?",
)
_T_N_BAR = (
    "{S} legt {r0} zu {p} an und entnimmt {zp} {r}. Wie viele Jahre lang kann {pron} diesen Betrag in voller Höhe entnehmen?",
)


def _fill(template: str, sz: Szenario, **werte) -> str:
    return template.format(S=sz.subjekt, pron=sz.pron, zweck=sz.zweck_anlage, **werte)


class RenteSachaufgabenGenerator(TaskGenerator):
    generator_key = "finanzmathematik.rentenrechnung.rente_sachaufgaben"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for sz in szenario_folge(rng, count):
            stufe = sz.stufe
            paare: list[tuple[str, str]] = []

            # R_n gesucht
            vor = rng.random() < 0.5
            r, p, n = sample_rate(rng, stufe), sample_zinssatz(rng), rng.randint(4, 25)
            paare.append((
                _fill(rng.choice(_T_RN), sz, n=n, zp=zeitpunkt_phrase(rng, vor), r=geld(r), p=prozent(p)),
                numerical_finanz_geld(rentenendwert(r, q_of(p), n, vor)),
            ))

            # R_0 gesucht
            vor = rng.random() < 0.5
            r, p, n = sample_rate(rng, stufe), sample_zinssatz(rng), rng.randint(4, 25)
            paare.append((
                _fill(rng.choice(_T_R0), sz, n=n, zp=zeitpunkt_phrase(rng, vor), r=geld(r), p=prozent(p)),
                numerical_finanz_geld(rentenbarwert(r, q_of(p), n, vor)),
            ))

            # r gesucht (aus Endwert oder Barwert)
            vor = rng.random() < 0.5
            r, p, n = sample_rate(rng, stufe), sample_zinssatz(rng), rng.randint(4, 25)
            q = q_of(p)
            if rng.random() < 0.5:
                rn = schoen(rentenendwert(r, q, n, vor), stufe)
                paare.append((
                    _fill(rng.choice(_T_R_END), sz, n=n, rn=geld(rn), zp=zeitpunkt_phrase(rng, vor), p=prozent(p)),
                    numerical_finanz_geld(rn / renten_faktor(q, n, vor)),
                ))
            else:
                r0 = schoen(rentenbarwert(r, q, n, vor), stufe)
                paare.append((
                    _fill(rng.choice(_T_R_BAR), sz, r0=geld(r0), p=prozent(p), n=n, zp=zeitpunkt_phrase(rng, vor)),
                    numerical_finanz_geld(r0 * q**n / renten_faktor(q, n, vor)),
                ))

            # n gesucht (aus Endwert oder Barwert)
            while True:
                vor = rng.random() < 0.5
                r, p, n = sample_rate(rng, stufe), sample_zinssatz(rng), rng.randint(4, 25)
                q = q_of(p)
                if rng.random() < 0.5:
                    rn = schoen(rentenendwert(r, q, n, vor), stufe)
                    n_antwort = rente_n_aus_endwert(r, rn, q, vor)
                    frage = _fill(rng.choice(_T_N_END), sz, zp=zeitpunkt_phrase(rng, vor), r=geld(r), p=prozent(p), rn=geld(rn))
                else:
                    r0 = schoen(rentenbarwert(r, q, n, vor), stufe)
                    n_antwort = rente_n_aus_barwert(r, r0, q, vor)
                    frage = _fill(rng.choice(_T_N_BAR), sz, r0=geld(r0), p=prozent(p), zp=zeitpunkt_phrase(rng, vor), r=geld(r))
                if n_antwort is not None and n_antwort > 1.0:
                    break
            paare.append((frage, numerical_finanz_laufzeit(n_antwort)))

            fragen, antworten = mische_teilfragen(rng, paare)
            tasks.append(Task(einleitung=sz.intro_anlage, fragen=fragen, antworten=antworten))

        return tasks
