"""Gemeinsame Hilfsfunktionen für die MPP-Generatoren (Checks 2–6).

Stellt Matrizenerzeugung, LaTeX-Formatierung und numerische Helfer bereit.
"""

from __future__ import annotations

import random

# ---------------------------------------------------------------------------
# Re-Exporte aus matrizenrechnung.shared
# ---------------------------------------------------------------------------
from aufgaben.generators.lineare_algebra.matrizenrechnung.shared import (
    det_nxn,
    inverse_nxn,
    mat_mul,
    matrix_to_latex,
    numerical_int,
    random_invertible,
    random_matrix,
)


# ---------------------------------------------------------------------------
# Matrixerzeugung
# ---------------------------------------------------------------------------

def random_nonneg_matrix(rng: random.Random, rows: int, cols: int,
                         low: int = 1, high: int = 9) -> list[list[int]]:
    """Erzeuge eine Matrix mit nicht-negativen Einträgen (Standard: 1–9)."""
    return [[rng.randint(low, high) for _ in range(cols)] for _ in range(rows)]


def mat_vec(mat: list[list[int]], vec: list[int]) -> list[int]:
    """Matrix-Vektor-Multiplikation."""
    return [sum(mat[i][j] * vec[j] for j in range(len(vec))) for i in range(len(mat))]


def dot(a: list[int], b: list[int]) -> int:
    """Skalarprodukt zweier Vektoren."""
    return sum(x * y for x, y in zip(a, b))


# ---------------------------------------------------------------------------
# LaTeX-Formatierung (MPP-Konventionen)
# ---------------------------------------------------------------------------

def matrix_latex(name: str, mat: list[list[int]]) -> str:
    r"""``\( RZ = \left(\begin{matrix}...\end{matrix}\right) \)``."""
    rows = len(mat)
    cols = len(mat[0])
    row_strs = [
        "&".join(str(mat[i][j]) for j in range(cols))
        for i in range(rows)
    ]
    inner = "\\\\".join(row_strs)
    return rf"\( {name} = \left(\begin{{matrix}}{inner}\end{{matrix}}\right) \)"


def spaltenvektor_latex(name: str, vec: list[int]) -> str:
    r"""``\( \vec{r} = \left(\begin{matrix}...\end{matrix}\right) \)``."""
    inner = "\\\\".join(str(v) for v in vec)
    return rf"\( \vec{{{name}}} = \left(\begin{{matrix}}{inner}\end{{matrix}}\right) \)"


def zeilenvektor_latex(name: str, vec: list[int]) -> str:
    r"""``\( \vec{k_R} = \left(\begin{matrix}1&2&3\end{matrix}\right) \)``."""
    inner = "&".join(str(v) for v in vec)
    return rf"\( \vec{{{name}}} = \left(\begin{{matrix}}{inner}\end{{matrix}}\right) \)"


def var_spaltenvektor_latex(name: str, n: int, start: str = "a") -> str:
    r"""Spaltenvektor mit Variablen: ``\( \vec{r} = \left(\begin{matrix}a\\b\\c\end{matrix}\right) \)``."""
    chars = [chr(ord(start) + i) for i in range(n)]
    inner = "\\\\".join(chars)
    return rf"\( \vec{{{name}}} = \left(\begin{{matrix}}{inner}\end{{matrix}}\right) \)"


def var_zeilenvektor_latex(name: str, n: int, start: str = "a") -> str:
    r"""Zeilenvektor mit Variablen."""
    chars = [chr(ord(start) + i) for i in range(n)]
    inner = "&".join(chars)
    return rf"\( \vec{{{name}}} = \left(\begin{{matrix}}{inner}\end{{matrix}}\right) \)"


def var_matrix_latex(name: str, rows: int, cols: int) -> str:
    r"""Matrix mit Variablennamen a, b, c, …."""
    idx = 0
    row_strs = []
    for i in range(rows):
        cells = []
        for j in range(cols):
            cells.append(chr(ord("a") + idx))
            idx += 1
        row_strs.append("&".join(cells))
    inner = "\\\\".join(row_strs)
    return rf"\( {name} = \left(\begin{{matrix}}{inner}\end{{matrix}}\right) \)"


def antwort_matrix(mat: list[list[int]]) -> str:
    """Erzeuge kompakte Moodle-Antwort: ``\\( a= \\){…}\\( b= \\){…}<br>…``."""
    rows = len(mat)
    cols = len(mat[0])
    idx = 0
    row_parts = []
    for i in range(rows):
        cells = []
        for j in range(cols):
            var = chr(ord("a") + idx)
            cells.append(f"\\( {var}= \\){numerical_int(mat[i][j])}")
            idx += 1
        row_parts.append("".join(cells))
    return "<br>".join(row_parts) + "<br>"


def antwort_spaltenvektor(vec: list[int], start: str = "a") -> str:
    """Erzeuge kompakte Moodle-Antwort für einen Spaltenvektor."""
    parts = []
    for i, v in enumerate(vec):
        var = chr(ord(start) + i)
        parts.append(f"\\( {var}= \\){numerical_int(v)}")
    return " ".join(parts)


def antwort_zeilenvektor(vec: list[int], start: str = "a") -> str:
    """Erzeuge kompakte Moodle-Antwort für einen Zeilenvektor."""
    parts = []
    for i, v in enumerate(vec):
        var = chr(ord(start) + i)
        parts.append(f"\\( {var}= \\){numerical_int(v)}")
    return "".join(parts) + "<br>"


# ---------------------------------------------------------------------------
# Szenario-Erzeugung: MPP-Matrizen
# ---------------------------------------------------------------------------

def erzeuge_mpp_triple(
    rng: random.Random,
    *,
    brauche_inv: str | None = None,
    max_entry: int = 9,
    max_re_entry: int = 200,
) -> tuple[int, int, int, list[list[int]], list[list[int]], list[list[int]]] | None:
    """Erzeuge konsistente (nR, nZ, nE, RZ, ZE, RE) mit RE = RZ · ZE.

    brauche_inv:
        None  – keine Matrix muss invertierbar sein
        "RZ"  – RZ soll quadratisch und Z-invertierbar sein (det = ±1)
        "ZE"  – ZE soll quadratisch und Z-invertierbar sein (det = ±1)
        "RE"  – RE soll quadratisch und Z-invertierbar sein (det = ±1)

    Gibt None zurück, wenn die Erzeugung in diesem Versuch scheitert.
    """
    sizes = [2, 3, 4]

    if brauche_inv == "RZ":
        n = rng.choice(sizes)
        nR, nZ, nE = n, n, rng.choice(sizes)
    elif brauche_inv == "ZE":
        n = rng.choice(sizes)
        nR, nZ, nE = rng.choice(sizes), n, n
    elif brauche_inv == "RE":
        n = rng.choice(sizes)
        nR, nZ, nE = n, rng.choice(sizes), n
    else:
        nR = rng.choice(sizes)
        nZ = rng.choice(sizes)
        nE = rng.choice(sizes)

    # RZ erzeugen
    if brauche_inv == "RZ":
        rz = random_invertible(rng, nR, max_entry=max_entry, steps_range=(3, 6))
        # Einträge auf nicht-negativ prüfen
        if any(rz[i][j] < 0 for i in range(nR) for j in range(nZ)):
            return None
    else:
        rz = random_nonneg_matrix(rng, nR, nZ, low=1, high=max_entry)

    # ZE erzeugen
    if brauche_inv == "ZE":
        ze = random_invertible(rng, nZ, max_entry=max_entry, steps_range=(3, 6))
        if any(ze[i][j] < 0 for i in range(nZ) for j in range(nE)):
            return None
    else:
        ze = random_nonneg_matrix(rng, nZ, nE, low=1, high=max_entry)

    # RE = RZ · ZE
    re = mat_mul(rz, ze)

    # Prüfe RE-Einträge
    if any(abs(re[i][j]) > max_re_entry for i in range(nR) for j in range(nE)):
        return None
    if any(re[i][j] < 0 for i in range(nR) for j in range(nE)):
        return None

    # Falls RE invertierbar sein soll: prüfe det = ±1
    if brauche_inv == "RE":
        if abs(det_nxn(re)) != 1:
            return None

    return nR, nZ, nE, rz, ze, re


def einleitung_matrizen(
    teile: dict[str, list[list[int]] | list[int]],
    extras: dict[str, str] | None = None,
) -> str:
    """Baue den 'Gegeben:'-Einleitungstext aus gegebenen Matrizen/Vektoren.

    teile: Mapping Name → Matrix/Vektor, z. B. {"RZ": [[...]], "ZE": [[...]]}
    extras: zusätzliche LaTeX-Fragmente als Schlüssel→LaTeX-String

    Matrizen (list[list[int]]) werden als Matrix-LaTeX, Vektoren (list[int])
    als Spaltenvektor-LaTeX dargestellt.
    """
    parts: list[str] = []
    for name, data in teile.items():
        if isinstance(data[0], list):
            parts.append(matrix_latex(name, data))  # type: ignore[arg-type]
        else:
            parts.append(spaltenvektor_latex(name, data))  # type: ignore[arg-type]
    if extras:
        for _name, latex in extras.items():
            parts.append(latex)
    joined = r"\(;\quad\)".join(parts)
    return f"Gegeben:</p> <p>{joined}"
