"""Gemeinsame Formeln, Formatierung und Sampling für die Finanzmathematik.

Konventionen (siehe aufgaben/README.md, Abschnitt Finanzmathematik):
- ausschließlich jährliche Verzinsung, Zinsfaktor q = 1 + p/100
- gegebene Werte sind "schön" (Vielfache der Stufen-Rundung), Antworten werden aus den
  gegebenen Werten berechnet und mit den FINANZ_*-Toleranzen bewertet
- Tilgungspläne werden zeilenweise auf Cent gerundet (kaufmännisch), gerundete Werte
  werden weiterverwendet
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from aufgaben.core.latex import fmt
from aufgaben.core.tolerances import finanz_geld_tolerance as finanz_geld_tolerance_for

NBSP = "\u00a0"

ZINSSAETZE = (
    1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75,
    4.0, 4.25, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0,
)

TABELLEN_KOPF_TILGUNGSPLAN = (
    "Jahr",
    "Restschuld (Jahresanfang)",
    "Zinsen",
    "Tilgung",
    "Annuität",
    "Restschuld (Jahresende)",
)


# ---------------------------------------------------------------------------
# Rundung & Formatierung
# ---------------------------------------------------------------------------

def rund2(value: float) -> float:
    """Kaufmännische Rundung auf Cent (kein Banker's Rounding)."""
    return float(Decimal(str(round(value, 8))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def runde_auf(value: float, step: float) -> float:
    return float(round(value / step) * step)


def _de_zahl(value: float, decimals: int) -> str:
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def geld(value: float, cents: bool | None = None) -> str:
    """Betrag im Fließtext, z. B. '12.500 €' oder '12.345,67 €'."""
    v = rund2(value)
    if cents is None:
        cents = abs(v - round(v)) > 1e-9
    return f"{_de_zahl(v, 2 if cents else 0)}{NBSP}€"


def prozent(p: float) -> str:
    return f"{fmt(p)}{NBSP}%"


def jahre(n: int) -> str:
    return "1 Jahr" if n == 1 else f"{n} Jahre"


def jahren(n: int) -> str:
    return "einem Jahr" if n == 1 else f"{n} Jahren"


def latex_zahl(value: float, decimals: int | None = None, trim: bool = False) -> str:
    """Zahl für Inline-LaTeX mit Tausenderabstand und Dezimalkomma, z. B. '12\\,500' oder '3{,}25'."""
    v = round(value, 6)
    if decimals is None:
        decimals = 0 if abs(v - round(v)) < 1e-9 else 2
    text = f"{v:,.{decimals}f}"
    int_part, _, frac = text.partition(".")
    if trim:
        frac = frac.rstrip("0")
    int_part = int_part.replace(",", "\\,")
    return int_part + (f"{{,}}{frac}" if frac else "")


def latex_geld(value: float) -> str:
    """Betrag als LaTeX-Zahl (ohne $), z. B. '12\\,500' oder '12\\,345{,}67'."""
    return latex_zahl(rund2(value))


def latex_prozent(p: float) -> str:
    """Zinssatz als LaTeX-Zahl (ohne $), z. B. '3{,}25'."""
    return latex_zahl(p, decimals=2, trim=True)


def g_geld(symbol: str, value: float) -> str:
    return f"${symbol} = {latex_geld(value)}${NBSP}€"


def g_prozent(value: float) -> str:
    return f"$p = {latex_prozent(value)}${NBSP}%"


def g_n(value: int, symbol: str = "n") -> str:
    return f"${symbol} = {value}$"


def tabelle_html(kopf: tuple[str, ...] | list[str], zeilen: list[list[str]]) -> str:
    header = "    <tr>" + "".join(f"<th>{cell}</th>" for cell in kopf) + "</tr>"
    rows = "\n".join("    <tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in zeilen)
    return f"<table class=\"TabelleEinleitung\">\n{header}\n{rows}\n</table>"


def zeitpunkt_phrase(rng: random.Random, vorschuessig: bool) -> str:
    if vorschuessig:
        return rng.choice(("jeweils zu Beginn eines Jahres", "jeweils am Jahresanfang", "vorschüssig"))
    return rng.choice(("jeweils am Ende eines Jahres", "jeweils zum Jahresende", "nachschüssig"))


def rentenart(vorschuessig: bool) -> str:
    return "vorschüssige" if vorschuessig else "nachschüssige"


# ---------------------------------------------------------------------------
# Formeln
# ---------------------------------------------------------------------------

def q_of(p: float) -> float:
    return 1.0 + p / 100.0


def p_of(q: float) -> float:
    return (q - 1.0) * 100.0


def zinseszins_kn(k0: float, q: float, n: float) -> float:
    return k0 * q**n


def zinseszins_k0(kn: float, q: float, n: float) -> float:
    return kn / q**n


def zinseszins_n(k0: float, kn: float, q: float) -> float:
    return math.log(kn / k0) / math.log(q)


def zinseszins_p(k0: float, kn: float, n: float) -> float:
    return p_of((kn / k0) ** (1.0 / n))


def renten_faktor(q: float, n: float, vorschuessig: bool) -> float:
    """Endwert einer Rente mit Rate 1: (q^n - 1)/(q - 1), vorschüssig zusätzlich mal q."""
    f = q if vorschuessig else 1.0
    return f * (q**n - 1.0) / (q - 1.0)


def rentenendwert(r: float, q: float, n: float, vorschuessig: bool) -> float:
    return r * renten_faktor(q, n, vorschuessig)


def rentenbarwert(r: float, q: float, n: float, vorschuessig: bool) -> float:
    return rentenendwert(r, q, n, vorschuessig) / q**n


def rente_n_aus_endwert(r: float, rn: float, q: float, vorschuessig: bool) -> float:
    f = q if vorschuessig else 1.0
    return math.log(rn * (q - 1.0) / (r * f) + 1.0) / math.log(q)


def rente_n_aus_barwert(r: float, r0: float, q: float, vorschuessig: bool) -> float | None:
    f = q if vorschuessig else 1.0
    nenner = r * f - r0 * (q - 1.0)
    if nenner <= 0:
        return None
    return math.log(r * f / nenner) / math.log(q)


def kapital_en(k0: float, r: float, q: float, n: float, vorschuessig: bool, aufbau: bool) -> float:
    rn = rentenendwert(r, q, n, vorschuessig)
    return k0 * q**n + rn if aufbau else k0 * q**n - rn


def kapital_n(k0: float, r: float, q: float, en: float, vorschuessig: bool, aufbau: bool) -> float | None:
    f = q if vorschuessig else 1.0
    c = r * f / (q - 1.0)
    if aufbau:
        ratio = (en + c) / (k0 + c)
    else:
        if not (c > k0 > en):
            return None
        ratio = (en - c) / (k0 - c)
    if ratio <= 1.0:
        return None
    return math.log(ratio) / math.log(q)


def annuitaet(k0: float, q: float, n: float) -> float:
    return k0 * q**n * (q - 1.0) / (q**n - 1.0)


def annuitaet_k0(a: float, q: float, n: float) -> float:
    return a * (q**n - 1.0) / (q**n * (q - 1.0))


def annuitaet_n(k0: float, a: float, q: float) -> float | None:
    t1 = a - k0 * (q - 1.0)
    if t1 <= 0:
        return None
    return math.log(a / t1) / math.log(q)


def restschuld(k0: float, a: float, q: float, k: float) -> float:
    return k0 * q**k - a * (q**k - 1.0) / (q - 1.0)


@dataclass(frozen=True)
class PlanZeile:
    jahr: int
    rk_anfang: float
    zinsen: float
    tilgung: float
    annuitaet: float
    rk_ende: float


def tilgungsplan(k0: float, p: float, a: float, n: int) -> list[PlanZeile]:
    """Zeilenweise auf Cent gerundeter Tilgungsplan mit genau n Zeilen.

    Letzte Zeile: Tilgung = verbliebene Restschuld, Annuität = Zinsen + Tilgung.
    """
    zeilen: list[PlanZeile] = []
    rk = rund2(k0)
    a = rund2(a)
    for jahr in range(1, n + 1):
        zinsen = rund2(rk * p / 100.0)
        if jahr == n:
            tilgung = rk
            annuitaet_jahr = rund2(zinsen + tilgung)
        else:
            tilgung = rund2(a - zinsen)
            annuitaet_jahr = a
        rk_ende = rund2(rk - tilgung)
        zeilen.append(PlanZeile(jahr, rk, zinsen, tilgung, annuitaet_jahr, rk_ende))
        rk = rk_ende
    return zeilen


def plan_zeile_html(zeile: PlanZeile, verborgen: set[str] | None = None) -> list[str]:
    verborgen = verborgen or set()

    def cell(name: str, value: float) -> str:
        return "?" if name in verborgen else geld(value, cents=True)

    return [
        str(zeile.jahr),
        cell("rk_anfang", zeile.rk_anfang),
        cell("zinsen", zeile.zinsen),
        cell("tilgung", zeile.tilgung),
        cell("annuitaet", zeile.annuitaet),
        cell("rk_ende", zeile.rk_ende),
    ]


# ---------------------------------------------------------------------------
# Sampling nach Betragsstufe
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Stufe:
    name: str
    kapital: tuple[int, int, int]
    rate: tuple[int, int, int]
    darlehen: tuple[int, int, int]
    rundung: int


STUFEN: dict[str, Stufe] = {
    "privat_klein": Stufe("privat_klein", (1_000, 20_000, 500), (200, 2_400, 50), (5_000, 30_000, 1_000), 10),
    "privat_gross": Stufe("privat_gross", (20_000, 250_000, 5_000), (1_000, 12_000, 500), (50_000, 400_000, 10_000), 100),
    "unternehmen": Stufe("unternehmen", (50_000, 1_500_000, 10_000), (5_000, 100_000, 5_000), (100_000, 3_000_000, 50_000), 1_000),
}


def _sample_range(rng: random.Random, bereich: tuple[int, int, int]) -> float:
    lo, hi, step = bereich
    return float(rng.randrange(lo, hi + step, step))


def sample_kapital(rng: random.Random, stufe: Stufe) -> float:
    return _sample_range(rng, stufe.kapital)


def sample_rate(rng: random.Random, stufe: Stufe) -> float:
    return _sample_range(rng, stufe.rate)


def sample_darlehen(rng: random.Random, stufe: Stufe) -> float:
    return _sample_range(rng, stufe.darlehen)


def sample_zinssatz(rng: random.Random, ohne: float | None = None) -> float:
    kandidaten = [p for p in ZINSSAETZE if p != ohne]
    return rng.choice(kandidaten)


def sample_laufzeit(rng: random.Random, lo: int = 3, hi: int = 25) -> int:
    return rng.randint(lo, hi)


def schoen(value: float, stufe: Stufe) -> float:
    """Rundet einen abgeleiteten Wert auf die Stufen-Granularität (für gegebene Werte im Text)."""
    return runde_auf(value, stufe.rundung)


def mische_teilfragen(rng: random.Random, paare: list[tuple[str, str]]) -> tuple[list[str], list[str]]:
    gemischt = list(paare)
    rng.shuffle(gemischt)
    return [f for f, _ in gemischt], [a for _, a in gemischt]
