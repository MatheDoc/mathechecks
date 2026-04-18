"""Zentrale LaTeX-Formatierung für Funktionsterme.

Regeln:
- Koeffizient 0 → Term weglassen
- Koeffizient +1 → nur Variable (kein "1")
- Koeffizient -1 → nur "-" + Variable (kein "-1")
- Deutsches Komma als Dezimaltrennzeichen
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Zahlenformatierung
# ---------------------------------------------------------------------------

def fmt(value: float, max_decimals: int = 4) -> str:
    """Zahl mit deutschem Komma, ohne trailing zeros."""
    rounded = round(float(value), max_decimals)
    text = f"{rounded:.{max_decimals}f}".rstrip("0").rstrip(".")
    if text in {"-0", ""}:
        text = "0"
    return text.replace(".", ",")


# ---------------------------------------------------------------------------
# Term-Bausteine
# ---------------------------------------------------------------------------

def coeff_latex(val: float, var: str, *, leading: bool = False) -> str:
    """Koeffizient · Variable als LaTeX-Fragment.

    - ``val == 0``  → ``""``
    - ``val == 1``  → ``"+x"`` (bzw. ``"x"`` bei *leading*)
    - ``val == -1`` → ``"-x"``
    - sonst         → ``"+3x"`` / ``"-2,5x"``
    """
    if val == 0:
        return ""
    sign = "" if (leading and val > 0) else ("+" if val > 0 else "-")
    a = abs(val)
    num = "" if a == 1 else fmt(a)
    return f"{sign}{num}{var}"


def const_latex(val: float) -> str:
    """Konstanter Term (``"+3"``, ``"-1"``, ``""`` bei 0)."""
    if val == 0:
        return ""
    return ("+" if val > 0 else "-") + fmt(abs(val))


def signed_number(val: float, *, leading: bool = False) -> str:
    """Vorzeichenbehaftete Zahl (ohne Variable)."""
    if val >= 0:
        return ("" if leading else "+") + fmt(val)
    return "-" + fmt(abs(val))


# ---------------------------------------------------------------------------
# Display-Helfer
# ---------------------------------------------------------------------------

def display_eq(expression: str) -> str:
    """Display-Math-Block ``$$ ... $$``."""
    return f"$$ {expression} $$"


def inline(expression: str) -> str:
    """Inline-Math ``$ ... $``."""
    return f"$ {expression} $"
