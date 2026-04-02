import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc, numerical, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.shared import binom_cdf
from aufgaben.generators.stochastik.hypothesentests.shared import (
    AblehnungsbereichCase,
    sample_ablehnungsbereich_rechts,
)


def _p_fmt(p: float, rng: random.Random) -> str:
    if rng.random() < 0.4:
        return f"{round(p * 100)}\u00a0%"
    return f"{p:.2f}".replace(".", ",")


def _alpha_pct(alpha_req: float) -> str:
    return f"{round(alpha_req * 100)}\u00a0%"


_HISTORISCH = [
    "Bisher nahm man an, dass die Wahrscheinlichkeit, {acc} anzutreffen, {p0} beträgt.",
    "Erfahrungsgemäß liegt die Wahrscheinlichkeit, {acc} zu beobachten, bei {p0}.",
    "Aus früheren Erhebungen ist bekannt, dass mit Wahrscheinlichkeit {p0} {acc} auftritt.",
    "Bisherige Daten belegen eine Wahrscheinlichkeit von {p0} dafür, {acc} zu beobachten.",
    "Der bisherige Erfahrungswert sagt: Mit Wahrscheinlichkeit {p0} tritt {acc} auf.",
]

_VERMUTUNG = [
    "Es besteht nun die Vermutung, dass sich dieser Anteil erhöht hat.",
    "Man vermutet, dass die aktuelle Rate darüber liegt.",
    "Neuere Beobachtungen legen nahe, dass der Anteil gestiegen sein könnte.",
    "Inzwischen wird vermutet, dass dieser Wert gestiegen ist.",
    "Es wird angenommen, dass der wahre Anteil heute größer ist.",
]

_STICHPROBE = [
    "Zur Überprüfung werden {n}\u00a0{sample} zufällig ausgewählt.",
    "Daher werden {n}\u00a0{sample} stichprobenartig betrachtet.",
    "{n}\u00a0{sample} werden dafür zufällig untersucht.",
    "Um dies zu überprüfen, betrachtet man {n}\u00a0{sample}.",
]

_ALPHA_SATZ = [
    "Das Signifikanzniveau soll höchstens {a} betragen.",
    "Der Test soll ein Signifikanzniveau von höchstens {a} einhalten.",
    "Als maximales Signifikanzniveau werden {a} festgelegt.",
]


class AblehnungsbereichRechtsseitigGenerator(TaskGenerator):
    generator_key = "stochastik.hypothesentests.ablehnungsbereich_rechtsseitig"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for _ in range(count):
            case: AblehnungsbereichCase = sample_ablehnungsbereich_rechts(rng)
            sc = case.scenario
            k = case.critical_value
            n = case.n
            p0 = case.p0
            alpha_req = case.alpha_requested

            p0_fmt = _p_fmt(p0, rng)
            alpha_pct = _alpha_pct(alpha_req)

            # P-Werte für Berechnungsfrage
            # P(X ≥ k-1) = 1 - P(X ≤ k-2), P(X ≥ k) = 1 - P(X ≤ k-1)
            p_at_km1 = 1.0 - binom_cdf(n=n, p=p0, k=k - 2)
            p_at_k   = 1.0 - binom_cdf(n=n, p=p0, k=k - 1)

            hist = rng.choice(_HISTORISCH).format(acc=sc.success_event_accusative, p0=p0_fmt)
            vermutung = rng.choice(_VERMUTUNG)
            stichprobe = rng.choice(_STICHPROBE).format(n=n, sample=sc.sample_object_plural)
            alpha_satz = rng.choice(_ALPHA_SATZ).format(a=alpha_pct)

            intro = (
                f"<p>{sc.intro_prefix} "
                f"{hist} "
                f"{vermutung} "
                f"{stichprobe} "
                f"{alpha_satz}</p>"
            )

            # MC-Bausteine
            num_p0    = numerical(p0, tolerance=0, decimals=2)
            num_alpha = numerical(alpha_req, tolerance=0, decimals=2)
            mc_geq    = mc(["≥", "≤"], correct_index=0)

            # Annahmebereich-Grenzen: [0, … , k-1]  -  Distraktoren: k bzw. n
            mc_an_low = mc(["0", "k"], correct_index=0)
            mc_an_up  = mc(["k-1", str(n)], correct_index=0)

            # Ablehnungsbereich-Grenzen: [k, … , n]  -  Distraktoren: 0 bzw. k+1
            mc_ab_low = mc(["k", "0"], correct_index=0)
            mc_ab_up  = mc([str(n), "k+1"], correct_index=0)

            a1 = (
                f"$ H_0: p = $ {num_p0}<br>"
                f"Annahmebereich: [ {mc_an_low}, &nbsp;&#8230;&nbsp; , {mc_an_up} ]"
            )
            a2 = (
                f"$ H_1: p $ {mc(['>', '<'], correct_index=0)}{num_p0}<br>"
                f"Ablehnungsbereich: [ {mc_ab_low}, &nbsp;&#8230;&nbsp; , {mc_ab_up} ]"
            )
            a3 = (
                f"Gesucht ist das {mc(['kleinste', 'größte'], correct_index=0)} $ k $, "
                f"so dass $ P(X $ {mc_geq} $ k $ ) &leq; {num_alpha} ist."
            )
            a4 = (
                f"$ P(X $ {mc_geq}{k - 1} $ ) = $ {numerical_stochastik_calc(p_at_km1)}<br>"
                f"$ P(X $ {mc_geq}{k} $ ) = $ {numerical_stochastik_calc(p_at_k)}<br>"
                f"Der Ablehnungsbereich lautet daher $ [ $ {mc_ab_low}, &nbsp;&#8230;&nbsp; , {mc_ab_up} $ ] $."
            )

            tasks.append(Task(
                einleitung=intro,
                fragen=["Nullhypothese:", "Gegenhypothese:", "Entscheidungsregel:", "Berechnungen:"],
                antworten=[a1, a2, a3, a4],
            ))

        return tasks

