"""Direkte Beschriftung von Linien im Diagramm (ersetzt die farbige Legende)."""

from __future__ import annotations

import numpy as np

_RAND_U = (0.05, 0.95)
_RAND_V = (0.06, 0.94)
_ABSTAND = 0.03


def _normiert(x, y, xlim, ylim):
    u = (np.asarray(x, float) - xlim[0]) / (xlim[1] - xlim[0])
    v = (np.asarray(y, float) - ylim[0]) / (ylim[1] - ylim[0])
    ok = np.isfinite(u) & np.isfinite(v)
    return np.column_stack([u[ok], v[ok]])


def _ausduennen(punkte: np.ndarray, maximal: int) -> np.ndarray:
    if len(punkte) <= maximal:
        return punkte
    return punkte[np.linspace(0, len(punkte) - 1, maximal).astype(int)]


def _min_abstand(kandidaten: np.ndarray, hindernisse: np.ndarray) -> np.ndarray:
    if len(hindernisse) == 0:
        return np.full(len(kandidaten), 1.0)
    d = np.linalg.norm(kandidaten[:, None, :] - hindernisse[None, :, :], axis=2)
    return d.min(axis=1)


def beschrifte_linien(ax, linien: list[dict], xlim, ylim, fontsize: float = 13, hindernisse_xy=()) -> None:
    """Setzt Namen direkt an die Linien.

    `linien`: Liste von Dicts mit `x`, `y` (Arrays), `name` (str) und optional `bei_x`
    (feste x-Position der Beschriftung). Die Position wird so gewählt, dass die
    Beschriftung möglichst weit von anderen Linien, Beschriftungen und `hindernisse_xy`
    (z. B. markierte Punkte) entfernt liegt.
    """
    alle = [_normiert(l["x"], l["y"], xlim, ylim) for l in linien]
    belegt: list[np.ndarray] = []
    for hx, hy in hindernisse_xy:
        p = _normiert([hx], [hy], xlim, ylim)
        if len(p):
            # Punkt samt rechts oben stehendem Namen freihalten
            belegt.append(np.vstack([p + np.array([du, dv]) for du in (0, 0.03, 0.06) for dv in (0, 0.03)]))

    for i, linie in enumerate(linien):
        name = linie.get("name")
        if not name:
            continue
        eigene = alle[i]
        if len(eigene) < 3:
            continue

        innen = (
            (eigene[:, 0] > _RAND_U[0]) & (eigene[:, 0] < _RAND_U[1])
            & (eigene[:, 1] > _RAND_V[0]) & (eigene[:, 1] < _RAND_V[1])
        )
        idx = np.flatnonzero(innen)
        if linie.get("bei_x") is not None:
            ziel_u = (linie["bei_x"] - xlim[0]) / (xlim[1] - xlim[0])
            idx = np.array([int(np.argmin(np.abs(eigene[:, 0] - ziel_u)))])
        if len(idx) == 0:
            continue
        idx = idx[(idx > 0) & (idx < len(eigene) - 1)] if len(idx) > 1 else idx
        idx = _ausduennen(idx, 300)

        andere = [alle[j] for j in range(len(linien)) if j != i]
        hindernisse = np.vstack([_ausduennen(a, 1500) for a in andere] + belegt) if (andere or belegt) else np.empty((0, 2))
        eigene_duenn = _ausduennen(eigene, 1500)

        vor = eigene[np.clip(idx + 1, 0, len(eigene) - 1)]
        nach = eigene[np.clip(idx - 1, 0, len(eigene) - 1)]
        tangente = vor - nach
        laenge = np.linalg.norm(tangente, axis=1, keepdims=True)
        laenge[laenge == 0] = 1
        tangente /= laenge
        normale = np.column_stack([-tangente[:, 1], tangente[:, 0]])

        bester = None
        for seite in (1, -1):
            n = normale * seite
            pos = eigene[idx] + n * (_ABSTAND + 0.02)
            score = _min_abstand(pos, hindernisse)
            eigen = _min_abstand(pos, eigene_duenn)
            score = score - np.where(eigen < _ABSTAND * 0.8, 1.0, 0.0)
            # eindeutig zuordenbar: deutlich näher an der eigenen als an jeder anderen Linie
            score = score - np.where(score < 1.4 * eigen, 0.5, 0.0)
            ausserhalb = (pos[:, 0] < 0.03) | (pos[:, 0] > 0.97) | (pos[:, 1] < 0.04) | (pos[:, 1] > 0.96)
            score = score - np.where(ausserhalb, 1.0, 0.0)
            # leichte Bevorzugung oberhalb der Kurve (übliche Lesart)
            score = score + 0.002 * (n[:, 1] > 0)
            k = int(np.argmax(score))
            if bester is None or score[k] > bester[0]:
                bester = (score[k], idx[k], n[k])

        _, k, n = bester
        anker = eigene[k] + n * _ABSTAND
        ha = "left" if n[0] > 0.35 else "right" if n[0] < -0.35 else "center"
        va = "bottom" if n[1] > 0.35 else "top" if n[1] < -0.35 else "center"
        ax.text(
            xlim[0] + anker[0] * (xlim[1] - xlim[0]),
            ylim[0] + anker[1] * (ylim[1] - ylim[0]),
            name,
            ha=ha,
            va=va,
            fontsize=fontsize,
            zorder=6,
            bbox={"boxstyle": "round,pad=0.15", "facecolor": "white", "edgecolor": "none", "alpha": 0.9},
        )
        belegt.append(np.repeat(anker[None, :] + n * 0.03, 8, axis=0))
