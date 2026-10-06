"""Gemeinsame Hilfsfunktionen für Lagerräumungs-Generatoren (MPP)."""

from __future__ import annotations

import random
from dataclasses import dataclass
from fractions import Fraction


# ---------------------------------------------------------------------------
# Datenmodell
# ---------------------------------------------------------------------------

@dataclass
class ProduktionsSzenario:
    """Alle erzeugten Größen eines Aufgabenszenarios."""
    a: list[int]        # Absolutglieder des Produktionsvektors (4 Komponenten)
    b: list[int]        # Steigungen des Produktionsvektors (4 Komponenten)
    t_min: int
    t_max: int
    kv: list[int]       # variable Stückkosten (4 Komponenten)
    p: list[int]        # Preisvektor (4 Komponenten)


# ---------------------------------------------------------------------------
# Generierung
# ---------------------------------------------------------------------------

def erzeuge_szenario(rng: random.Random) -> ProduktionsSzenario:
    """Erzeuge ein plausibles Produktionsszenario mit 4 Endprodukten.

    Struktur: m(t) = (a1 + b1 t, a2 + b2 t, a3 + b3 t, t).

    Garantiert:
    - letzte Komponente ist genau t (a4 = 0, b4 = 1) => t_min = 0
    - unter den ersten drei Komponenten mindestens ein b_i < 0, alle b_i != 0
    - alle a_i > 0 (für i = 1, 2, 3)
    - t_max = min{ a_i / |b_i| : b_i < 0 } ist exakt ganzzahlig und >= 10,
      d. h. [0; t_max] ist genau der Bereich mit m_i(t) >= 0 für alle i
    """
    n = 4

    for _ in range(500):
        t_max = rng.randint(10, 25)

        neg_count = rng.randint(1, n - 1)
        indices = list(range(n - 1))
        rng.shuffle(indices)
        neg_indices = indices[:neg_count]
        pos_indices = indices[neg_count:]

        a = [0] * n
        b = [0] * n
        a[n - 1], b[n - 1] = 0, 1

        for idx in pos_indices:
            b[idx] = rng.randint(1, 5)
            a[idx] = rng.randint(10, 80)

        # Genau eine negative Komponente bestimmt die obere Grenze exakt,
        # die übrigen negativen Komponenten erst später.
        bindend = neg_indices[0]
        for idx in neg_indices:
            b[idx] = rng.randint(-4, -1)
            if idx == bindend:
                a[idx] = abs(b[idx]) * t_max
            else:
                a[idx] = abs(b[idx]) * t_max + rng.randint(1, 40)

        if any(a[i] <= 0 for i in range(n - 1)) or len(set(zip(a, b))) < n:
            continue

        grenzen = [Fraction(a[i], -b[i]) for i in range(n) if b[i] < 0]
        if min(grenzen) != t_max:
            continue

        # Variable Stückkosten
        kv = [rng.randint(2, 15) for _ in range(n)]

        # Preisvektor: jeder Preis > zugehörige variable Stückkosten
        p = [kv[i] + rng.randint(5, 30) for i in range(n)]

        return ProduktionsSzenario(a=a, b=b, t_min=0, t_max=t_max, kv=kv, p=p)

    raise ValueError("Konnte kein gültiges Szenario erzeugen.")


# ---------------------------------------------------------------------------
# Berechnungen
# ---------------------------------------------------------------------------

def komponente(sz: ProduktionsSzenario, i: int, t: int) -> int:
    """Wert der i-ten Komponente von m(t)."""
    return sz.a[i] + sz.b[i] * t


def summe_komponenten(sz: ProduktionsSzenario, t: int) -> int:
    """Summe aller Komponenten von m(t)."""
    return sum(sz.a[i] + sz.b[i] * t for i in range(4))


def variable_kosten(sz: ProduktionsSzenario, t: int) -> int:
    """K_v(t) = kv . m(t)."""
    return sum(sz.kv[i] * (sz.a[i] + sz.b[i] * t) for i in range(4))


def erloes(sz: ProduktionsSzenario, t: int) -> int:
    """E(t) = p . m(t)."""
    return sum(sz.p[i] * (sz.a[i] + sz.b[i] * t) for i in range(4))


def deckungsbeitrag(sz: ProduktionsSzenario, t: int) -> int:
    """DB(t) = E(t) - K_v(t)."""
    return erloes(sz, t) - variable_kosten(sz, t)


# Koeffizienten der linearen Funktionen (Absolutglied, Steigung)

def _linkoeff_skalar(vektor: list[int], sz: ProduktionsSzenario) -> tuple[int, int]:
    """Berechne (c0, c1) so dass vektor . m(t) = c0 + c1 * t."""
    c0 = sum(vektor[i] * sz.a[i] for i in range(4))
    c1 = sum(vektor[i] * sz.b[i] for i in range(4))
    return c0, c1


def koeff_variable_kosten(sz: ProduktionsSzenario) -> tuple[int, int]:
    return _linkoeff_skalar(sz.kv, sz)


def koeff_erloes(sz: ProduktionsSzenario) -> tuple[int, int]:
    return _linkoeff_skalar(sz.p, sz)


def koeff_deckungsbeitrag(sz: ProduktionsSzenario) -> tuple[int, int]:
    c0_e, c1_e = koeff_erloes(sz)
    c0_k, c1_k = koeff_variable_kosten(sz)
    return c0_e - c0_k, c1_e - c1_k


def koeff_summe(sz: ProduktionsSzenario) -> tuple[int, int]:
    c0 = sum(sz.a)
    c1 = sum(sz.b)
    return c0, c1


def optimum_linear(c0: int, c1: int, t_min: int, t_max: int, maximize: bool) -> int:
    """Berechne Optimum einer linearen Funktion f(t) = c0 + c1*t auf [t_min, t_max]."""
    f_min = c0 + c1 * t_min
    f_max = c0 + c1 * t_max
    if maximize:
        return max(f_min, f_max)
    else:
        return min(f_min, f_max)


def optimum_t(c1: int, t_min: int, t_max: int, maximize: bool) -> int:
    """t-Wert, bei dem das Optimum angenommen wird."""
    if maximize:
        return t_max if c1 >= 0 else t_min
    else:
        return t_min if c1 >= 0 else t_max


def t_fuer_zielwert(c0: int, c1: int, zielwert: int) -> int | None:
    """Löse c0 + c1 * t = zielwert nach t auf. Gibt None zurück wenn nicht ganzzahlig."""
    if c1 == 0:
        return None
    diff = zielwert - c0
    if diff % c1 != 0:
        return None
    return diff // c1


# ---------------------------------------------------------------------------
# LaTeX-Formatierung
# ---------------------------------------------------------------------------

def numerical_int(value: int) -> str:
    return f"{{1:NUMERICAL:={value}:0}}"


def spaltenvektor_latex(werte: list[str]) -> str:
    """LaTeX-Spaltenvektor aus String-Einträgen."""
    rows = r"\\".join(werte)
    return rf"\left(\begin{{matrix}}{rows}\end{{matrix}}\right)"


def zeilenvektor_latex(werte: list[int]) -> str:
    """LaTeX-Zeilenvektor aus int-Einträgen."""
    entries = "&".join(str(v) for v in werte)
    return rf"\left(\begin{{matrix}}{entries}\end{{matrix}}\right)"


def produktionsvektor_latex(sz: ProduktionsSzenario) -> str:
    """LaTeX für den parametrisierten Produktionsvektor m(t)."""
    zeilen: list[str] = []
    for i in range(4):
        a_i, b_i = sz.a[i], sz.b[i]
        if b_i == 0:
            zeilen.append(str(a_i))
        elif a_i == 0:
            zeilen.append("t" if b_i == 1 else f"{b_i}t")
        elif b_i == 1:
            zeilen.append(f"{a_i}+t")
        elif b_i == -1:
            zeilen.append(f"{a_i}-t")
        elif b_i > 0:
            zeilen.append(f"{a_i}+{b_i}t")
        else:
            zeilen.append(f"{a_i}{b_i}t")  # b_i ist negativ, Minus kommt automatisch
    return spaltenvektor_latex(zeilen)


def einleitung_text(sz: ProduktionsSzenario) -> str:
    """Erzeugt die Einleitung für eine Aufgabe."""
    m_latex = produktionsvektor_latex(sz)
    kv_latex = zeilenvektor_latex(sz.kv)
    p_latex = zeilenvektor_latex(sz.p)

    return (
        f"Gegeben ist der mehrdeutige Produktionsvektor "
        f"\\( \\vec{{m}}(t) = {m_latex} \\) "
        f"mit \\( t \\in [{sz.t_min};\\,{sz.t_max}] \\), "
        f"der Vektor der variablen Stückkosten "
        f"\\( \\vec{{k}}_v = {kv_latex} \\) "
        f"und der Preisvektor "
        f"\\( \\vec{{p}} = {p_latex} \\)."
    )
