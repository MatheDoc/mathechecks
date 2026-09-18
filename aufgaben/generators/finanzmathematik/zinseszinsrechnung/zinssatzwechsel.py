"""Check 03 – Zinssatzwechsel (zwei oder drei Zinsphasen, eine fehlende Größe)."""

from __future__ import annotations

import math
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
    p_of,
    prozent,
    q_of,
    sample_kapital,
    sample_zinssatz,
    schoen,
)
from aufgaben.generators.finanzmathematik.szenarien import Szenario, szenario_folge

_ORDINAL = ("ersten", "zweiten", "dritten")


def _phasen_text(phasen: list[tuple[int, float | None]]) -> str:
    """Beschreibt die Zinsphasen; ``None`` als Zinssatz markiert die unbekannte Phase."""
    teile: list[str] = []
    for index, (n, p) in enumerate(phasen):
        satz = "einem zunächst unbekannten Zinssatz" if p is None else prozent(p)
        if index == 0:
            teile.append(f"In den ersten {n} Jahren wird das Kapital mit {satz} verzinst")
        elif index == len(phasen) - 1 and len(phasen) == 3:
            teile.append(f"in den letzten {n} Jahren mit {satz}")
        else:
            teile.append(f"in den folgenden {n} Jahren mit {satz}")
    return ", ".join(teile) + "."


def _sample_phasen(rng: random.Random) -> list[tuple[int, float]]:
    anzahl = rng.choice((2, 2, 3))
    phasen: list[tuple[int, float]] = []
    letzter = None
    for _ in range(anzahl):
        p = sample_zinssatz(rng, ohne=letzter)
        phasen.append((rng.randint(2, 8), p))
        letzter = p
    return phasen


def _endkapital(k0: float, phasen: list[tuple[int, float]]) -> float:
    wert = k0
    for n, p in phasen:
        wert *= q_of(p) ** n
    return wert


class ZinssatzwechselGenerator(TaskGenerator):
    generator_key = "finanzmathematik.zinseszinsrechnung.zinssatzwechsel"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        typen = ("kn", "k0", "p", "n")
        tasks: list[Task] = []

        for index, sz in enumerate(szenario_folge(rng, count)):
            typ = typen[index % len(typen)]
            tasks.append(self._build(rng, sz, typ))

        return tasks

    def _build(self, rng: random.Random, sz: Szenario, typ: str) -> Task:
        stufe = sz.stufe
        k0 = sample_kapital(rng, stufe)
        phasen = _sample_phasen(rng)
        gesamt = sum(n for n, _ in phasen)
        n1, p1 = phasen[0]
        kapital_phase1 = k0 * q_of(p1) ** n1

        if typ == "kn":
            intro = f"{sz.subjekt} legt {geld(k0)} {sz.zweck_anlage} an. {_phasen_text(phasen)}"
            return Task(
                einleitung=intro,
                fragen=[
                    "Wie hoch ist das Guthaben am Ende der ersten Zinsphase?",
                    f"Über welchen Betrag kann {sz.pron} nach insgesamt {gesamt} Jahren verfügen?",
                ],
                antworten=[
                    numerical_finanz_geld(kapital_phase1),
                    numerical_finanz_geld(_endkapital(k0, phasen)),
                ],
            )

        kn = schoen(_endkapital(k0, phasen), stufe)

        if typ == "k0":
            intro = (
                f"{sz.subjekt} hat vor {gesamt} Jahren einen Betrag {sz.zweck_anlage} angelegt. "
                f"{_phasen_text(phasen).replace('wird das Kapital', 'wurde das Kapital')} "
                f"Heute beträgt das Guthaben {geld(kn)}."
            )
            faktor = math.prod(q_of(p) ** n for n, p in phasen)
            k0_antwort = kn / faktor
            return Task(
                einleitung=intro,
                fragen=[
                    "Welcher Betrag wurde ursprünglich angelegt?",
                    "Wie hoch war das Guthaben am Ende der ersten Zinsphase?",
                ],
                antworten=[
                    numerical_finanz_geld(k0_antwort),
                    numerical_finanz_geld(k0_antwort * q_of(p1) ** n1),
                ],
            )

        if typ == "p":
            unbekannt = rng.randrange(len(phasen))
            n_u = phasen[unbekannt][0]
            beschreibung = [(n, None if i == unbekannt else p) for i, (n, p) in enumerate(phasen)]
            intro = (
                f"{sz.subjekt} legt {geld(k0)} {sz.zweck_anlage} an. {_phasen_text(beschreibung)} "
                f"Nach insgesamt {gesamt} Jahren beträgt das Guthaben {geld(kn)}."
            )
            bekannt = math.prod(q_of(p) ** n for i, (n, p) in enumerate(phasen) if i != unbekannt)
            q_u = (kn / (k0 * bekannt)) ** (1.0 / n_u)
            return Task(
                einleitung=intro,
                fragen=[f"Mit welchem Zinssatz wurde das Kapital in der {_ORDINAL[unbekannt]} Zinsphase verzinst?"],
                antworten=[numerical_finanz_zinssatz(p_of(q_u))],
            )

        # typ == "n": Dauer der letzten Phase gesucht
        n_letzte, p_letzte = phasen[-1]
        vorher = phasen[:-1]
        intro_phasen = _phasen_text(vorher).rstrip(".")
        intro = (
            f"{sz.subjekt} legt {geld(k0)} {sz.zweck_anlage} an. {intro_phasen}, "
            f"danach mit {prozent(p_letzte)}, bis das Guthaben {geld(kn)} erreicht hat."
        )
        kapital_vorher = _endkapital(k0, vorher)
        n_antwort = math.log(kn / kapital_vorher) / math.log(q_of(p_letzte))
        return Task(
            einleitung=intro,
            fragen=[
                f"Wie hoch ist das Guthaben zu Beginn der {_ORDINAL[len(phasen) - 1]} Zinsphase?",
                f"Wie viele Jahre dauert die {_ORDINAL[len(phasen) - 1]} Zinsphase?",
            ],
            antworten=[
                numerical_finanz_geld(kapital_vorher),
                numerical_finanz_laufzeit(n_antwort),
            ],
        )
