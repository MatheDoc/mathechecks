import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc, numerical, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.binomialverteilung.shared import binom_cdf
from aufgaben.generators.stochastik.hypothesentests.shared import (
    AblehnungsbereichCase,
    sample_ablehnungsbereich_links,
)


def _p_fmt(p: float, rng: random.Random) -> str:
    """Zeigt p als Dezimalzahl (0,38) oder als Prozent (38 %)."""
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
    "Es besteht nun die Vermutung, dass sich dieser Anteil verringert hat.",
    "Man vermutet, dass die aktuelle Rate darunter liegt.",
    "Neuere Beobachtungen legen nahe, dass der Anteil gesunken sein könnte.",
    "Inzwischen wird vermutet, dass dieser Wert gesunken ist.",
    "Es wird angenommen, dass der wahre Anteil heute kleiner ist.",
]

_STICHPROBE = [
    "Zur Überprüfung werden {n}\u00a0{sample} zufällig ausgewählt.",
    "Daher werden {n}\u00a0{sample} stichprobenartig betrachtet.",
    "{n}\u00a0{sample} werden dafür zufällig untersucht.",
    "Um dies zu überprüfen, betrachtet man {n}\u00a0{sample}.",
]

_ALPHA_SATZ = [
    "Das Signifikanzniveau soll {a} betragen.",
    "Der Test soll ein Signifikanzniveau von {a} einhalten.",
    "Als Signifikanzniveau werden {a} festgelegt.",
]


class AblehnungsbereichLinksseitigGenerator(TaskGenerator):
    generator_key = "stochastik.hypothesentests.ablehnungsbereich_linksseitig"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for _ in range(count):
            case: AblehnungsbereichCase = sample_ablehnungsbereich_links(rng)
            sc = case.scenario
            k = case.critical_value
            n = case.n
            p0 = case.p0
            alpha_req = case.alpha_requested

            p0_fmt = _p_fmt(p0, rng)
            alpha_pct = _alpha_pct(alpha_req)

            # P-Werte für Berechnungsfrage
            p_at_k  = binom_cdf(n=n, p=p0, k=k)
            p_at_k1 = binom_cdf(n=n, p=p0, k=k + 1)

            hist = rng.choice(_HISTORISCH).format(acc=sc.success_event_accusative, p0=p0_fmt)
            vermutung = rng.choice(_VERMUTUNG)
            stichprobe = rng.choice(_STICHPROBE).format(n=n, sample=sc.sample_object_plural)
            alpha_satz = rng.choice(_ALPHA_SATZ).format(a=alpha_pct)

            intro = (
                f"{sc.intro_prefix} "
                f"{hist} "
                f"{vermutung} "
                f"{stichprobe} "
                f"{alpha_satz}"
            )

            # MC-Bausteine
            num_p0    = numerical(p0, tolerance=0, decimals=2)
            num_alpha = numerical(alpha_req, tolerance=0, decimals=2)
            mc_leq    = mc(["≤", "≥"], correct_index=0)

            # Annahmebereich-Grenzen: [k+1, … , n]  -  Distraktoren: 0 bzw. k-1
            mc_an_low = mc(["0", "k+1"], correct_index=1)
            mc_an_up  = mc(["k-1", str(n)], correct_index=1)

            # Ablehnungsbereich-Grenzen: [0, … , k]  -  Distraktoren: k bzw. n
            mc_ab_low = mc(["0", "k"], correct_index=0)
            mc_ab_up  = mc(["k", str(n)], correct_index=0)

            a1 = (
                f"$ H_0: p = $ {num_p0} <br>"
                f"Annahmebereich: [ {mc_an_low}, &nbsp;&#8230;&nbsp; , {mc_an_up} ]"
            )
            a2 = (
                f"$ H_1: p $ {mc(['<', '>'], correct_index=0)}{num_p0}<br>"
                f"Ablehnungsbereich: [ {mc_ab_low}, &nbsp;&#8230;&nbsp; , {mc_ab_up} ]"
            )
            a3 = (
                f"Gesucht ist das {mc(['größte', 'kleinste'], correct_index=0)} $ k $, "
                f"so dass $ P(X $ {mc_leq} $ k) $ &leq; {num_alpha} ist."
            )
            a4 = (
                f"$ P(X $ {mc_leq}{k} $) = $ {numerical_stochastik_calc(p_at_k)}<br>"
                f"$ P(X $ {mc_leq}{k + 1} $ ) = ${numerical_stochastik_calc(p_at_k1)}<br>"
                f"Der Ablehnungsbereich lautet daher $ [ $ {mc_ab_low}, &nbsp;&#8230;&nbsp; , {mc_ab_up} $ ] $."
            )

            tasks.append(Task(
                einleitung=intro,
                fragen=["Nullhypothese:", "Gegenhypothese:", "Entscheidungsregel:", "Berechnungen:"],
                antworten=[a1, a2, a3, a4],
            ))

        return tasks

