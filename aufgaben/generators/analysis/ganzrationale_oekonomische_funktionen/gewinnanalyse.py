"""Gewinnsituationen im Angebotsmonopol analysieren (Vertiefungs-Check).

Jede Aufgabe:
- Einleitung: Szenario (Monopol), Kostenfunktion als Term, Preis-Absatz-Funktion
  als Term oder nur in Textform (zwei Preis-Mengen-Paare bzw. Höchstpreis und
  Preisrückgang pro ME). E und G stellen die Lernenden selbst auf.
- Teilfrage 1 (immer): Cournotscher Punkt.
- Danach zwei Bausteine mit je zwei Teilfragen aus einem Pool von acht
  (Mindestgewinn, Fixkostenerhöhung, tragbare Fixkosten, Werbekampagne,
  Lage einer Absatzmenge, Fixkosten aus Bedingung, Patent läuft aus,
  Preisgestaltung). Die Teilfragen bauen aufeinander auf, deshalb
  questionOrder "fixed" in checks.json.
"""

from __future__ import annotations

import itertools
import math
import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _bisection_root,
    _format_number,
    _num_tol,
    _poly3_latex,
    _preis_linear_latex,
    _sample_e2k3_parameters,
)
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.szenarien import (
    szenario_folge,
)

X_TOL = 0.1


def _y_tol(value: float) -> float:
    return max(0.1, 0.003 * abs(value))


def _nice(value: float, digits: int = 2) -> float:
    """Rundet auf ``digits`` signifikante Stellen (für Vorgaben im Aufgabentext)."""
    if value == 0:
        return 0.0
    exponent = math.floor(math.log10(abs(value)))
    factor = 10 ** (digits - 1 - exponent)
    return round(value * factor) / factor


def _fmt(value: float) -> str:
    return _format_number(round(value, 4))


def _mc(rng: random.Random, richtig: str, falsch: list[str]) -> str:
    optionen = [f"={richtig}"] + list(falsch)
    rng.shuffle(optionen)
    return "{1:MC:~" + "~".join(optionen) + "}"


class _Modell:
    """Monopol mit p(x) = a2·x + a1 und K(x) = k3·x³ + k2·x² + k1·x + k0."""

    def __init__(self, a2, a1, k3, k2, k1, k0, x_gs, x_gg, x_gmax):
        self.a2, self.a1 = a2, a1
        self.k3, self.k2, self.k1, self.k0 = k3, k2, k1, k0
        self.x_gs, self.x_gg, self.x_gmax = x_gs, x_gg, x_gmax
        self.sm = -a1 / a2

    def p(self, x):
        return self.a2 * x + self.a1

    def K(self, x):
        return ((self.k3 * x + self.k2) * x + self.k1) * x + self.k0

    def Ks(self, x):  # K'(x)
        return (3 * self.k3 * x + 2 * self.k2) * x + self.k1

    def G(self, x):
        return self.p(x) * x - self.K(x)

    def Gs(self, x):  # G'(x)
        return 2 * self.a2 * x + self.a1 - self.Ks(x)

    @property
    def g_max(self):
        return self.G(self.x_gmax)

    @property
    def p_max(self):
        return self.p(self.x_gmax)


# ── Bausteine: liefern [(frage, antwort), (frage, antwort)] oder None ─────────

def _b_mindestgewinn(m: _Modell, rng):
    c = _nice(rng.uniform(0.3, 0.7) * m.g_max)
    if not 0 < c < m.g_max:
        return None
    h = lambda x: m.G(x) - c
    x_links = _bisection_root(h, m.x_gs, m.x_gmax)
    x_rechts = _bisection_root(h, m.x_gmax, m.x_gg)
    return [
        (f"Bestimmen Sie die kleinste Absatzmenge, ab der der Gewinn mindestens {_fmt(c)} GE beträgt.",
         _num_tol(x_links, X_TOL)),
        (f"Bestimmen Sie die größte Absatzmenge, bis zu der der Gewinn mindestens {_fmt(c)} GE beträgt.",
         _num_tol(x_rechts, X_TOL)),
    ]


def _b_fixkosten_steigen(m: _Modell, rng):
    delta = _nice(rng.uniform(0.2, 0.6) * m.g_max)
    if not 0 < delta < m.g_max:
        return None
    x_gs_neu = _bisection_root(lambda x: m.G(x) - delta, m.x_gs, m.x_gmax)
    return [
        (f"Die Fixkosten steigen um {_fmt(delta)} GE. Bestimmen Sie die neue Gewinnschwelle.",
         _num_tol(x_gs_neu, X_TOL)),
        ("Geben Sie an, wie sich der Cournotsche Punkt durch die Fixkostenerhöhung verändert.",
         _mc(rng, "Er bleibt unverändert.", [
             "Die Menge sinkt, der Preis steigt.",
             "Die Menge steigt, der Preis sinkt.",
             "Menge und Preis steigen.",
         ])),
    ]


def _b_tragbare_fixkosten(m: _Modell, rng):
    delta = _nice(rng.uniform(0.2, 0.6) * m.g_max)
    if not 0 < delta < m.g_max:
        return None
    k_f_max = m.k0 + m.g_max
    return [
        ("Bestimmen Sie, wie hoch die Fixkosten höchstens sein dürfen, damit das Unternehmen "
         "noch Gewinn erzielen kann.",
         _num_tol(k_f_max, _y_tol(k_f_max))),
        (f"Bestimmen Sie den maximalen Gewinn, wenn die Fixkosten um {_fmt(delta)} GE steigen.",
         _num_tol(m.g_max - delta, _y_tol(m.g_max - delta))),
    ]


def _b_werbekampagne(m: _Modell, rng):
    x1 = _nice(rng.uniform(0.4, 0.75) * m.x_gmax)
    x2 = _nice(m.x_gmax * rng.uniform(0.95, 1.15))
    if not (m.x_gs < x1 < x2 < m.x_gg):
        return None
    zuwachs = m.G(x2) - m.G(x1)
    if zuwachs <= 0:
        return None
    lohnt = rng.random() < 0.5
    kosten = _nice(zuwachs * (rng.uniform(0.65, 0.85) if lohnt else rng.uniform(1.15, 1.4)))
    if (kosten < zuwachs) != lohnt:
        return None
    ja = "Ja, der Gewinnzuwachs ist größer als die Kosten der Kampagne."
    nein = "Nein, der Gewinnzuwachs ist kleiner als die Kosten der Kampagne."
    return [
        (f"Durch eine Werbekampagne soll der Absatz von {_fmt(x1)} ME auf {_fmt(x2)} ME steigen. "
         "Bestimmen Sie den Gewinnzuwachs.",
         _num_tol(zuwachs, _y_tol(zuwachs))),
        (f"Die Kampagne kostet {_fmt(kosten)} GE. Geben Sie an, ob sie sich lohnt.",
         _mc(rng, ja if lohnt else nein, [
             nein if lohnt else ja,
             "Ja, weil der Erlös durch die Kampagne steigt.",
             "Nein, weil die Produktionskosten steigen.",
         ])),
    ]


_LAGEN = {
    "vor": "Gewinnzone, das Gewinnmaximum ist noch nicht erreicht.",
    "nach": "Gewinnzone, das Gewinnmaximum ist bereits überschritten.",
    "verlust": "Verlustzone",
    "max": "genau im Gewinnmaximum",
}


def _b_lage(m: _Modell, rng):
    zone = rng.choice(["vor", "nach", "verlust"])
    if zone == "vor":
        x0 = _nice(rng.uniform(m.x_gs + 0.2 * (m.x_gmax - m.x_gs), m.x_gmax - 0.15 * (m.x_gmax - m.x_gs)))
        ok = m.x_gs < x0 < m.x_gmax
    elif zone == "nach":
        x0 = _nice(rng.uniform(m.x_gmax + 0.15 * (m.x_gg - m.x_gmax), m.x_gg - 0.2 * (m.x_gg - m.x_gmax)))
        ok = m.x_gmax < x0 < m.x_gg
    else:
        x0 = _nice(rng.uniform(m.x_gg + 0.2 * (m.sm - m.x_gg), m.sm - 0.1 * (m.sm - m.x_gg)))
        ok = m.x_gg < x0 < m.sm
    if not ok or abs(x0 - m.x_gmax) < 0.05 * m.x_gmax:
        return None
    grenzgewinn = m.Gs(x0)
    return [
        (f"Bestimmen Sie den Grenzgewinn bei einer Absatzmenge von {_fmt(x0)} ME.",
         _num_tol(grenzgewinn, _y_tol(grenzgewinn))),
        (f"Geben Sie an, wie die Absatzmenge von {_fmt(x0)} ME einzuordnen ist.",
         _mc(rng, _LAGEN[zone], [v for k, v in _LAGEN.items() if k != zone])),
    ]


def _b_fixkosten_bedingung(m: _Modell, rng):
    links = rng.random() < 0.5
    if links:
        x0 = _nice(rng.uniform(m.x_gs + 0.25 * (m.x_gmax - m.x_gs), m.x_gmax - 0.25 * (m.x_gmax - m.x_gs)))
        ok = m.x_gs < x0 < m.x_gmax
    else:
        x0 = _nice(rng.uniform(m.x_gmax + 0.25 * (m.x_gg - m.x_gmax), m.x_gg - 0.25 * (m.x_gg - m.x_gmax)))
        ok = m.x_gmax < x0 < m.x_gg
    if not ok:
        return None
    k_f_neu = m.k0 + m.G(x0)
    richtig = "Gewinnschwelle, weil der Gewinn dort steigt." if links else "Gewinngrenze, weil der Gewinn dort fällt."
    return [
        (f"Bestimmen Sie, wie hoch die Fixkosten sein müssten, damit bei {_fmt(x0)} ME "
         "weder Gewinn noch Verlust entsteht.",
         _num_tol(k_f_neu, _y_tol(k_f_neu))),
        (f"Geben Sie an, ob {_fmt(x0)} ME bei diesen Fixkosten die Gewinnschwelle oder die Gewinngrenze ist.",
         _mc(rng, richtig, [
             "Gewinngrenze, weil der Gewinn dort fällt." if links else "Gewinnschwelle, weil der Gewinn dort steigt.",
             "Gewinnschwelle, weil der Gewinn dort fällt.",
             "Gewinngrenze, weil der Gewinn dort steigt.",
         ])),
    ]


def _b_patent(m: _Modell, rng):
    p_markt = _nice(rng.uniform(0.55, 0.85) * m.p_max)
    # Polypol: G_P(x) = p_markt·x − K(x), G_P'(x) = p_markt − K'(x) = 0
    a = 3 * m.k3
    b = 2 * m.k2
    c = m.k1 - p_markt
    disk = b * b - 4 * a * c
    if disk <= 0:
        return None
    x_p = (-b + math.sqrt(disk)) / (2 * a)
    g_p = p_markt * x_p - m.K(x_p)
    if x_p <= 0 or g_p <= 0 or g_p >= m.g_max:
        return None
    verlust = m.g_max - g_p
    return [
        (f"Nach Ablauf des Patents bieten weitere Unternehmen das Produkt an. Der Marktpreis liegt dann "
         f"bei {_fmt(p_markt)} GE/ME, die Kosten bleiben gleich. Bestimmen Sie die neue gewinnmaximale Menge.",
         _num_tol(x_p, X_TOL)),
        ("Bestimmen Sie, um wie viel GE der maximale Gewinn gegenüber dem Monopol sinkt.",
         _num_tol(verlust, _y_tol(verlust))),
    ]


def _b_preisgestaltung(m: _Modell, rng):
    x_ziel = _nice(m.x_gmax * rng.uniform(1.1, 1.3))
    # G'(x) = 2·a2·x + a1' − K'(x) = 0  ⇒  a1' = K'(x) − 2·a2·x
    a1_neu = m.Ks(x_ziel) - 2 * m.a2 * x_ziel
    zweite = 2 * m.a2 - (6 * m.k3 * x_ziel + 2 * m.k2)
    p_neu = m.a2 * x_ziel + a1_neu
    if zweite >= 0 or a1_neu <= m.a1 or p_neu <= 0:
        return None
    return [
        ("Durch eine Imagekampagne verschiebt sich die Preis-Absatz-Funktion parallel nach oben, ihre Steigung "
         f"bleibt gleich. Bestimmen Sie den neuen Höchstpreis, bei dem die gewinnmaximale Menge "
         f"{_fmt(x_ziel)} ME beträgt.",
         _num_tol(a1_neu, _y_tol(a1_neu))),
        ("Bestimmen Sie den zugehörigen gewinnmaximalen Preis.",
         _num_tol(p_neu, _y_tol(p_neu))),
    ]


BAUSTEINE = (
    _b_mindestgewinn,
    _b_fixkosten_steigen,
    _b_tragbare_fixkosten,
    _b_werbekampagne,
    _b_lage,
    _b_fixkosten_bedingung,
    _b_patent,
    _b_preisgestaltung,
)
# Beide Fixkosten-Bausteine arbeiten mit einer Erhöhung um Δ: nicht kombinieren.
_AUSGESCHLOSSEN = {frozenset({_b_fixkosten_steigen, _b_tragbare_fixkosten})}
PAARE = [
    paar for paar in itertools.combinations(BAUSTEINE, 2)
    if frozenset(paar) not in _AUSGESCHLOSSEN
]


def _preis_info(m: _Modell, variante: int, rng) -> str | None:
    if variante == 0:
        return f"Die Preis-Absatz-Funktion lautet ${_preis_linear_latex(m.a2, m.a1)}$."
    if variante == 1:
        x1 = _nice(rng.uniform(0.15, 0.35) * m.sm)
        x2 = _nice(rng.uniform(0.55, 0.8) * m.sm)
        if not 0 < x1 < x2 < m.sm:
            return None
        return (
            f"Bei einem Preis von {_fmt(m.p(x1))} GE/ME werden {_fmt(x1)} ME abgesetzt, "
            f"bei {_fmt(m.p(x2))} GE/ME sind es {_fmt(x2)} ME. "
            "Die Preis-Absatz-Funktion ist linear."
        )
    return (
        f"Der Höchstpreis beträgt {_fmt(m.a1)} GE/ME. Mit jeder zusätzlich abgesetzten ME "
        f"sinkt der erzielbare Preis um {_fmt(-m.a2)} GE/ME."
    )


class EconomicPolynomialGewinnanalyseGenerator(TaskGenerator):
    """Vertiefung: Cournotscher Punkt plus zwei Analyse-Bausteine je Aufgabe (Monopol)."""

    generator_key = "analysis.ganzrationale_oekonomische_funktionen.gewinnanalyse"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        szenarien = szenario_folge(rng, count)
        nutzung = {baustein: 0 for baustein in BAUSTEINE}
        tasks: list[Task] = []
        used: set = set()

        def naechstes_paar():
            # Paar mit den bisher seltensten Bausteinen wählen, damit alle gleich oft vorkommen
            kandidaten = list(PAARE)
            rng.shuffle(kandidaten)
            return min(kandidaten, key=lambda paar: nutzung[paar[0]] + nutzung[paar[1]])

        paar = naechstes_paar()

        while len(tasks) < count:
            index = len(tasks)
            params = _sample_e2k3_parameters(rng, for_graph=False)
            key = tuple(params[:6])
            if key in used:
                continue
            m = _Modell(*params)

            preis_info = _preis_info(m, index % 3, rng)
            if preis_info is None:
                continue

            teile = []
            for baustein in paar:
                ergebnis = None
                for _ in range(40):
                    ergebnis = baustein(m, rng)
                    if ergebnis is not None:
                        break
                if ergebnis is None:
                    break
                teile.extend(ergebnis)
            if len(teile) != 4:
                continue
            used.add(key)
            for baustein in paar:
                nutzung[baustein] += 1
            paar = naechstes_paar()

            einleitung = (
                f"{szenarien[index].monopol} Für die Herstellung gilt die Kostenfunktion "
                f"${_poly3_latex('K', m.k3, m.k2, m.k1, m.k0)}$. {preis_info} "
                "Dabei ist $x$ die Menge in ME, Preise sind in GE/ME und Kosten in GE angegeben. "
                "Runden Sie auf zwei Nachkommastellen."
            )
            cournot = (
                "Bestimmen Sie den Cournotschen Punkt.",
                "$ C( $" + _num_tol(m.x_gmax, X_TOL) + "$ \\mid $" + _num_tol(m.p_max, _y_tol(m.p_max)) + "$ ) $",
            )
            fragen = [cournot] + teile
            tasks.append(
                Task(
                    einleitung=einleitung,
                    fragen=[f for f, _ in fragen],
                    antworten=[a for _, a in fragen],
                )
            )

        return tasks
