"""Konsumenten- und Produzentenrente graphisch deuten und abschätzen.

Das Marktgleichgewicht liegt auf einem Gitterpunkt mit glatten Werten
(x_G = gx*dx, p_G = gy*dy).  Die Funktionen werden zunächst in
Kästcheneinheiten (u = x/dx, v = p/dy) konstruiert, wobei jeweils der
konstante Parameter so bestimmt wird, dass beide Graphen durch (gx|gy)
verlaufen.  Danach werden sie in reale Einheiten skaliert.
"""

import math
import random
from dataclasses import dataclass

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.marktgleichgewicht_grundlagen.shared import _fmt_number
from aufgaben.generators.analysis.marktgleichgewicht_vertiefung.shared import _num_tol


# (dx, dy): Kästchenbreite in ME und Kästchenhöhe in GE/ME -> Kästchenwert dx*dy in GE
_GRID_STEPS: list[tuple[int, int]] = [
    (1, 1), (1, 2), (2, 1), (2, 2), (5, 1), (5, 2), (1, 5), (2, 5),
    (10, 1), (10, 2), (5, 5), (1, 10), (2, 10), (10, 5), (5, 10), (10, 10),
]

_KR_TERM = "kr"
_PR_TERM = "pr"
_UMSATZ = "umsatz"
_ZAHLUNG = "zahlung"
_ANGEBOT = "angebot"

_MEANING = {
    _KR_TERM: "Konsumentenrente",
    _PR_TERM: "Produzentenrente",
    _UMSATZ: "Umsatz im Marktgleichgewicht",
    _ZAHLUNG: "Zahlungsbereitschaft der Konsumenten",
    _ANGEBOT: "Angebotsbereitschaft der Produzenten",
}


@dataclass
class _Curve:
    kind: str  # "linear" | "quadratic" | "exp"
    params: dict  # reale Parameter: p(x) = a*x+b | a*x^2+b*x+c | A*exp(-rate*x)+c

    def __call__(self, x: float) -> float:
        p = self.params
        if self.kind == "linear":
            return p["a"] * x + p["b"]
        if self.kind == "quadratic":
            return p["a"] * x * x + p["b"] * x + p["c"]
        return p["A"] * math.exp(-p["rate"] * x) + p["c"]

    def integral(self, x0: float, x1: float) -> float:
        p = self.params
        if self.kind == "linear":
            antiderivative = lambda x: 0.5 * p["a"] * x * x + p["b"] * x
        elif self.kind == "quadratic":
            antiderivative = lambda x: p["a"] * x ** 3 / 3.0 + 0.5 * p["b"] * x * x + p["c"] * x
        else:
            antiderivative = lambda x: -p["A"] / p["rate"] * math.exp(-p["rate"] * x) + p["c"] * x
        return antiderivative(x1) - antiderivative(x0)

    def term(self) -> str:
        p = self.params
        if self.kind == "linear":
            return f"{_js(p['a'])}*x{_js_signed(p['b'])}"
        if self.kind == "quadratic":
            linear_part = f"{_js_signed(p['b'])}*x" if p["b"] != 0 else ""
            return f"{_js(p['a'])}*x^2{linear_part}{_js_signed(p['c'])}"
        return f"{_js(p['A'])}*exp({_js(-p['rate'])}*x){_js_signed(p['c'])}"


def _js(value: float) -> str:
    """Dezimalzahl ohne Exponentialschreibweise (für buildExpressionFunction)."""
    text = f"{value:.10f}".rstrip("0").rstrip(".")
    if text in {"", "-0"}:
        text = "0"
    return text


def _js_signed(value: float) -> str:
    return f"+{_js(value)}" if value >= 0 else f"-{_js(-value)}"


def _pick(rng: random.Random, lo: float, hi: float, step: float) -> float:
    i_lo = math.ceil(lo / step - 1e-9)
    i_hi = math.floor(hi / step + 1e-9)
    return round(rng.randint(i_lo, i_hi) * step, 6)


def _demand_grid(rng: random.Random, kind: str, gx: int, gy: int):
    """Nachfrage in Kästcheneinheiten; liefert (Parameter, Höchstpreis v0) oder None."""
    if kind == "linear":
        s = _pick(rng, 0.25, 1.6, 0.05)
        params = {"a": -s, "b": gy + s * gx}
        v0 = params["b"]
    elif kind == "quadratic":
        a = _pick(rng, 0.01, 0.12, 0.005)
        b = _pick(rng, 0.0, 0.6, 0.05)
        if a * gx * gx < 0.35 * (a * gx * gx + b * gx):
            return None  # Krümmung soll sichtbar sein
        params = {"a": -a, "b": -b, "c": gy + a * gx * gx + b * gx}
        v0 = params["c"]
    else:
        rate = _pick(rng, 0.07, 0.35, 0.01)
        if not (0.8 <= rate * gx <= 1.8):
            return None
        amp = _pick(rng, 4.0, 30.0, 0.5)
        params = {"A": amp, "rate": rate, "c": gy - amp * math.exp(-rate * gx)}
        if params["c"] > 0.4 * gy:
            return None  # Graph soll deutlich fallen und nicht auf hohem Niveau abflachen
        v0 = amp + params["c"]
    h_n = v0 - gy
    if not (3.0 <= h_n <= 11.0):
        return None
    return params, v0


def _supply_grid(rng: random.Random, kind: str, gx: int, gy: int):
    """Angebot in Kästcheneinheiten; liefert (Parameter, Mindestangebotspreis m) oder None."""
    if kind == "linear":
        s = _pick(rng, 0.2, 1.2, 0.05)
        params = {"a": s, "b": gy - s * gx}
        m = params["b"]
    elif kind == "quadratic":
        a = _pick(rng, 0.01, 0.12, 0.005)
        b = _pick(rng, 0.0, 0.5, 0.05)
        if a * gx * gx < 0.4 * (a * gx * gx + b * gx):
            return None
        params = {"a": a, "b": b, "c": gy - a * gx * gx - b * gx}
        m = params["c"]
    else:
        rate = _pick(rng, 0.07, 0.35, 0.01)
        if not (0.8 <= rate * gx <= 1.8):
            return None
        amp = _pick(rng, 3.0, 20.0, 0.5)
        ceiling = gy + amp * math.exp(-rate * gx)
        params = {"A": -amp, "rate": rate, "c": ceiling}
        m = ceiling - amp
    if not (0.5 <= m <= gy - 1.5):
        return None
    return params, m


def _to_real(kind: str, grid_params: dict, dx: int, dy: int, x_g: int, p_g: int) -> _Curve:
    """Skaliert p(x) = dy * f(x/dx); der konstante Term wird in realen Einheiten neu
    berechnet, damit der Graph exakt durch (x_G|p_G) verläuft."""
    if kind == "linear":
        a = round(dy * grid_params["a"] / dx, 8)
        return _Curve(kind, {"a": a, "b": round(p_g - a * x_g, 8)})
    if kind == "quadratic":
        a = round(dy * grid_params["a"] / (dx * dx), 8)
        b = round(dy * grid_params["b"] / dx, 8)
        return _Curve(kind, {"a": a, "b": b, "c": round(p_g - a * x_g * x_g - b * x_g, 8)})
    amp = round(dy * grid_params["A"], 8)
    rate = round(grid_params["rate"] / dx, 8)
    return _Curve(kind, {"A": amp, "rate": rate, "c": round(p_g - amp * math.exp(-rate * x_g), 6)})


def _mc(options: list[str], correct: str) -> str:
    parts = "".join(f"~={opt}" if opt == correct else f"~{opt}" for opt in options)
    return f"{{1:MC:{parts}}}"


def _tex_num(value: float) -> str:
    return _fmt_number(value, max_decimals=4).replace(",", "{,}")


def _statement(rng: random.Random, kr: float, pr: float, want_true: bool) -> tuple[str, bool] | None:
    """Aussage über das Verhältnis KR/PR, die mind. 25 % von ihrer Schwelle entfernt ist."""
    pool = [
        ("Die Konsumentenrente ist größer als die Produzentenrente.", kr / pr, 1.0),
        ("Die Produzentenrente ist größer als die Konsumentenrente.", pr / kr, 1.0),
        ("Die Konsumentenrente ist mehr als doppelt so groß wie die Produzentenrente.", kr / pr, 2.0),
        ("Die Produzentenrente ist mehr als doppelt so groß wie die Konsumentenrente.", pr / kr, 2.0),
    ]
    usable: list[tuple[str, bool]] = []
    for text, ratio, threshold in pool:
        if ratio >= 1.25 * threshold:
            usable.append((text, True))
        elif ratio <= 0.75 * threshold:
            usable.append((text, False))
    matching = [item for item in usable if item[1] == want_true]
    if not matching:
        return None
    return rng.choice(matching)


class MarketEquilibriumRentenGraphischGenerator(TaskGenerator):
    generator_key = "analysis.marktgleichgewicht_vertiefung.renten_graphisch"

    def _sample(self, rng: random.Random, want_true: bool, used: set[tuple]):
        while True:
            dx, dy = rng.choice(_GRID_STEPS)
            gx = rng.randint(5, 12)
            gy = rng.randint(4, 10)
            kinds = [rng.choice(["linear", "quadratic", "exp"]) for _ in range(2)]
            if kinds == ["linear", "linear"]:
                continue
            supply_kind, demand_kind = kinds

            demand = _demand_grid(rng, demand_kind, gx, gy)
            supply = _supply_grid(rng, supply_kind, gx, gy)
            if demand is None or supply is None:
                continue
            demand_grid, v0 = demand

            x_g, p_g = gx * dx, gy * dy
            supply_fn = _to_real(supply_kind, supply[0], dx, dy, x_g, p_g)
            demand_fn = _to_real(demand_kind, demand_grid, dx, dy, x_g, p_g)

            # Monotonie im sichtbaren Bereich und eindeutiges Gleichgewicht
            u_max = gx + max(3, math.ceil(0.6 * gx))
            x_max = u_max * dx
            xs = [x_max * k / 400.0 for k in range(401)]
            if any(supply_fn(b) <= supply_fn(a) for a, b in zip(xs, xs[1:])):
                continue
            if any(demand_fn(b) >= demand_fn(a) for a, b in zip(xs, xs[1:]) if demand_fn(a) > 0):
                continue
            diffs = [demand_fn(x) - supply_fn(x) for x in xs]
            if sum(1 for a, b in zip(diffs, diffs[1:]) if a * b < 0) > 1:
                continue
            if supply_fn(0.0) <= 0.0:
                continue

            kr = demand_fn.integral(0.0, x_g) - x_g * p_g
            pr = x_g * p_g - supply_fn.integral(0.0, x_g)
            cell = dx * dy
            kr_cells, pr_cells = kr / cell, pr / cell
            if not (8.0 <= kr_cells <= 60.0 and 8.0 <= pr_cells <= 60.0):
                continue

            statement = _statement(rng, kr, pr, want_true)
            if statement is None:
                continue

            key = (dx, dy, gx, gy, supply_kind, demand_kind, tuple(supply_fn.params.values()), tuple(demand_fn.params.values()))
            if key in used:
                continue
            used.add(key)

            y_max_units = math.ceil(v0 + 0.8) + 1
            return {
                "dx": dx,
                "dy": dy,
                "x_g": x_g,
                "p_g": p_g,
                "x_max": x_max,
                "y_max": y_max_units * dy,
                "supply": supply_fn,
                "demand": demand_fn,
                "kr": kr,
                "pr": pr,
                "cell": cell,
                "statement": statement,
            }

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple] = set()
        # ausgewogene Verteilung der zu deutenden Terme (Angebotsbereitschaft seltener)
        meaning_pool = [_KR_TERM, _PR_TERM, _UMSATZ, _ZAHLUNG] * 2 + [_ANGEBOT]
        rng.shuffle(meaning_pool)

        for index in range(count):
            want_true = index % 2 == 0
            s = self._sample(rng, want_true, used)
            x_g, p_g = s["x_g"], s["p_g"]
            xg, pg = _tex_num(x_g), _tex_num(p_g)

            int_n = f"\\int_0^{{{xg}}}p_N(x)\\,dx"
            int_a = f"\\int_0^{{{xg}}}p_A(x)\\,dx"
            umsatz = f"{xg}\\cdot {pg}"
            terms = {
                _KR_TERM: f"${int_n}-{umsatz}$",
                _PR_TERM: f"${umsatz}-{int_a}$",
                _UMSATZ: f"${umsatz}$",
                _ZAHLUNG: f"${int_n}$",
                _ANGEBOT: f"${int_a}$",
            }

            # 1) Ausdruck für die Konsumentenrente
            expr_options = [
                terms[_KR_TERM],
                terms[_ZAHLUNG],
                f"${umsatz}-{int_n}$",
                f"$\\int_0^{{{xg}}}\\left(p_N(x)-p_A(x)\\right)dx$",
            ]
            expr_correct = expr_options[0]
            rng.shuffle(expr_options)

            # 2) Ökonomische Bedeutung eines Terms
            meaning_key = meaning_pool[index % len(meaning_pool)]
            if meaning_key == _ZAHLUNG:
                fourth = _ZAHLUNG
            elif meaning_key == _ANGEBOT:
                fourth = _ANGEBOT
            else:
                fourth = rng.choice([_ZAHLUNG, _ANGEBOT])
            meaning_options = [_MEANING[_KR_TERM], _MEANING[_PR_TERM], _MEANING[_UMSATZ], _MEANING[fourth]]

            def estimate_tol(value: float) -> float:
                return round(max(0.1 * value, 0.5 * s["cell"]), 2)

            statement_text, statement_true = s["statement"]
            items = [
                ("den Ausdruck, der die Konsumentenrente angibt.", _mc(expr_options, expr_correct)),
                (
                    f"die ökonomische Bedeutung von {terms[meaning_key]}.",
                    _mc(meaning_options, _MEANING[meaning_key]),
                ),
                (
                    "einen Schätzwert für die Konsumentenrente (in GE).",
                    _num_tol(s["kr"], tolerance=estimate_tol(s["kr"])),
                ),
                (
                    "einen Schätzwert für die Produzentenrente (in GE).",
                    _num_tol(s["pr"], tolerance=estimate_tol(s["pr"])),
                ),
                (
                    f"ob die Aussage „{statement_text}“ wahr oder falsch ist.",
                    _mc(["wahr", "falsch"], "wahr" if statement_true else "falsch"),
                ),
            ]

            tasks.append(
                Task(
                    einleitung=(
                        "Das Diagramm zeigt die Graphen der Angebotsfunktion $ p_A $ und der "
                        "Nachfragefunktion $ p_N $ ($ x $ in ME, $ p $ in GE/ME). "
                        "Bestimmen Sie anhand des Graphen"
                    ),
                    fragen=[q for q, _ in items],
                    antworten=[a for _, a in items],
                    visual=self._visual(s),
                )
            )

        return tasks

    @staticmethod
    def _visual(s: dict) -> dict:
        x_g, p_g = s["x_g"], s["p_g"]
        supply_term = s["supply"].term()
        demand_term = s["demand"].term()
        guide = {"color": "#6b7280", "width": 1.5, "dash": "dash"}
        title = "Angebots- und Nachfragefunktion"
        spec = {
            "type": "expression-curves",
            "title": title,
            "curves": [
                {
                    "term": supply_term,
                    "variable": "x",
                    "mode": "lines",
                    "name": "Angebot p<sub>A</sub>(x)",
                    "description": "Angebotsfunktion",
                    "line": {"color": "#d62728", "width": 2.5},
                },
                {
                    "term": demand_term,
                    "variable": "x",
                    "mode": "lines",
                    "name": "Nachfrage p<sub>N</sub>(x)",
                    "description": "Nachfragefunktion",
                    "line": {"color": "#1f77b4", "width": 2.5},
                },
            ],
            "extraTraces": [
                {
                    "x": [x_g],
                    "y": [p_g],
                    "mode": "markers",
                    "name": "Marktgleichgewicht",
                    "marker": {"color": "#f59e0b", "size": 10, "line": {"color": "#111827", "width": 1}},
                }
            ],
            "points": 401,
            "layout": {
                "title": title,
                "xaxis": {
                    "title": "Menge x in ME",
                    "range": [0, s["x_max"]],
                    "dtick": s["dx"],
                    "zeroline": True,
                    "showline": True,
                    "showgrid": True,
                    "automargin": True,
                },
                "yaxis": {
                    "title": "Preis p in GE/ME",
                    "range": [0, s["y_max"]],
                    "dtick": s["dy"],
                    "zeroline": True,
                    "showline": True,
                    "showgrid": True,
                    "automargin": True,
                },
                "shapes": [
                    {"type": "line", "x0": x_g, "x1": x_g, "y0": 0, "y1": p_g, "line": guide},
                    {"type": "line", "x0": 0, "x1": x_g, "y0": p_g, "y1": p_g, "line": guide},
                ],
            },
            "funktionen": [
                {"name": "p_A(x)", "term": supply_term, "beschreibung": "Angebotsfunktion"},
                {"name": "p_N(x)", "term": demand_term, "beschreibung": "Nachfragefunktion"},
            ],
        }
        return {"type": "plot", "spec": spec}
