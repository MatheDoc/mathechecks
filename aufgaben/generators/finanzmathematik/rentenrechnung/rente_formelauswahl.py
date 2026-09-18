"""Check 03 – Vor-/nachschüssig und Formelauswahl (MC, alle vier Rentenformeln pro Aufgabe)."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.finanzmathematik.shared import geld, prozent, sample_rate, sample_zinssatz
from aufgaben.generators.finanzmathematik.szenarien import Szenario, szenario_folge

_OPTIONEN = (
    "nachschüssiger Rentenendwert $R_n$",
    "vorschüssiger Rentenendwert $\\overline{R}_n$",
    "nachschüssiger Rentenbarwert $R_0$",
    "vorschüssiger Rentenbarwert $\\overline{R}_0$",
)

# Index: 0 = R_n, 1 = R̄_n, 2 = R_0, 3 = R̄_0
_SITUATIONEN: dict[int, tuple[str, ...]] = {
    0: (
        "{S} zahlt {n} Jahre lang jeweils am Ende eines Jahres {r} auf ein mit {p} verzinstes Konto ein. Gesucht ist das Guthaben unmittelbar nach der letzten Einzahlung.",
        "{S} legt {n} Jahre lang zum Jahresende jeweils {r} zurück ({p}). Welcher Betrag steht am Ende des letzten Jahres zur Verfügung?",
        "{S} spart nachschüssig {r} pro Jahr bei {p}. Gesucht ist der Kontostand nach {n} Jahren.",
    ),
    1: (
        "{S} zahlt {n} Jahre lang jeweils zu Beginn eines Jahres {r} auf ein mit {p} verzinstes Konto ein. Gesucht ist das Guthaben am Ende des letzten Jahres.",
        "{S} überweist {n} Jahre lang jeweils am Jahresanfang {r} auf ein Sparkonto ({p}). Wie hoch ist das Guthaben ein Jahr nach der letzten Einzahlung?",
        "{S} spart vorschüssig {r} pro Jahr bei {p}. Gesucht ist der Kontostand am Ende des {n}. Jahres.",
    ),
    2: (
        "{S} möchte {n} Jahre lang jeweils am Ende eines Jahres {r} entnehmen. Gesucht ist der Betrag, der dafür heute bei {p} angelegt werden muss.",
        "{S} soll {n} Jahre lang zum Jahresende jeweils {r} erhalten. Welcher Betrag müsste heute einmalig bei {p} bereitgestellt werden, damit alle Zahlungen geleistet werden können?",
        "{S} bietet an, statt {n} nachschüssiger Jahreszahlungen von {r} einen einmaligen Betrag heute zu zahlen ({p}). Gesucht ist dieser gleichwertige Betrag.",
    ),
    3: (
        "{S} möchte {n} Jahre lang jeweils zu Beginn eines Jahres {r} entnehmen, erstmals sofort. Gesucht ist der Betrag, der dafür heute bei {p} angelegt werden muss.",
        "{S} soll {n} Jahre lang jeweils am Jahresanfang {r} erhalten, die erste Zahlung sofort. Welcher Betrag müsste heute einmalig bei {p} bereitgestellt werden?",
        "{S} bietet an, statt {n} vorschüssiger Jahreszahlungen von {r} einen einmaligen Betrag heute zu zahlen ({p}). Gesucht ist dieser gleichwertige Betrag.",
    ),
}

_INTRO = (
    " Entscheiden Sie für jede Situation, mit welcher Rentenformel die gesuchte Größe berechnet wird."
)


class RenteFormelauswahlGenerator(TaskGenerator):
    generator_key = "finanzmathematik.rentenrechnung.rente_formelauswahl"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for sz in szenario_folge(rng, count):
            # alle vier Formeln je Aufgabe, Reihenfolge zufällig
            typen = rng.sample(range(4), 4)
            fragen: list[str] = []
            antworten: list[str] = []
            for typ in typen:
                fragen.append(self._situation(rng, sz, typ))
                antworten.append(mc(list(_OPTIONEN), typ))
            tasks.append(Task(einleitung=sz.intro_anlage + _INTRO, fragen=fragen, antworten=antworten))

        return tasks

    @staticmethod
    def _situation(rng: random.Random, sz: Szenario, typ: int) -> str:
        template = rng.choice(_SITUATIONEN[typ])
        return template.format(
            S=sz.subjekt,
            n=rng.randint(4, 20),
            r=geld(sample_rate(rng, sz.stufe)),
            p=prozent(sample_zinssatz(rng)),
        )
