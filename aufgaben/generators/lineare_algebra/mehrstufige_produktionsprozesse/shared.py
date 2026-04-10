"""Gemeinsame Hilfsfunktionen für Lagerräumungs-Generatoren (MPP)."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass


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

    Garantiert:
    - mindestens ein b_i > 0, mindestens ein b_i < 0
    - t_min >= 0, t_max - t_min >= 10
    - alle Komponenten m_i(t) >= 0 im zulässigen Bereich
    """
    n = 4

    for _ in range(500):
        # Steigungen: Mischung aus positiv und negativ
        b = [0] * n
        # Mindestens eins positiv und eins negativ
        pos_count = rng.randint(1, n - 1)
        neg_count = n - pos_count
        indices = list(range(n))
        rng.shuffle(indices)
        for idx in indices[:pos_count]:
            b[idx] = rng.randint(1, 5)
        for idx in indices[pos_count:]:
            b[idx] = rng.randint(-5, -1)

        # Absolutglieder
        a = [rng.randint(10, 80) for _ in range(n)]

        # Berechne zulässigen t-Bereich aus Nicht-Negativität: a_i + b_i * t >= 0
        lower_bounds: list[float] = []
        upper_bounds: list[float] = []
        for i in range(n):
            if b[i] > 0:
                # a_i + b_i * t >= 0 immer erfüllt für t >= 0
                lb = 0.0
                upper_bounds.append(float('inf'))
                lower_bounds.append(lb)
            elif b[i] < 0:
                # a_i + b_i * t >= 0  =>  t <= -a_i / b_i = a_i / |b_i|
                ub = a[i] / abs(b[i])
                upper_bounds.append(ub)
                lower_bounds.append(0.0)
            else:
                lower_bounds.append(0.0)
                upper_bounds.append(float('inf'))

        t_min_raw = max(lower_bounds)
        t_max_raw = min(upper_bounds)

        t_min = math.ceil(t_min_raw)
        t_max = math.floor(t_max_raw)

        if t_min < 0:
            t_min = 0

        if t_max - t_min < 10:
            continue

        # Prüfe, dass alle Komponenten im gesamten Bereich >= 0
        ok = True
        for t in (t_min, t_max):
            for i in range(n):
                if a[i] + b[i] * t < 0:
                    ok = False
                    break
            if not ok:
                break
        if not ok:
            continue

        # Variable Stückkosten
        kv = [rng.randint(2, 15) for _ in range(n)]

        # Preisvektor: jeder Preis > zugehörige variable Stückkosten
        p = [kv[i] + rng.randint(5, 30) for i in range(n)]

        return ProduktionsSzenario(a=a, b=b, t_min=t_min, t_max=t_max, kv=kv, p=p)

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
