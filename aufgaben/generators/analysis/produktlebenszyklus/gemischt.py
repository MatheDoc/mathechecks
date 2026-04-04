import math
import random
from dataclasses import dataclass

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.shared_numbers import uniform_sig


def _fmt(value: float, decimals: int = 4) -> str:
    rounded = round(float(value), decimals)
    text = f"{rounded:.{decimals}f}".rstrip("0").rstrip(".")
    if text in {"", "-0"}:
        text = "0"
    return text.replace(".", ",")


def _signed(value: float, decimals: int = 4) -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}{_fmt(abs(value), decimals)}"


def _num_tol(value: float, tolerance: float = 0.1, decimals: int = 4) -> str:
    return f"{{1:NUMERICAL:={_fmt(value, decimals)}:{_fmt(tolerance, 3)}}}"


def _interval_num(a: float, b: float, tolerance: float = 0.01, decimals: int = 4) -> str:
    left = _num_tol(a, tolerance=tolerance, decimals=decimals)
    right = _num_tol(b, tolerance=tolerance, decimals=decimals)
    return f"[{left};{right}]"


def _rand_step(rng: random.Random, lo: float, hi: float, step: float) -> float:
    i_lo = int(math.ceil(lo / step))
    i_hi = int(math.floor(hi / step))
    if i_lo > i_hi:
        raise ValueError("Ungueltiger Bereich fuer Schritt-Zufallszahl.")
    return rng.randint(i_lo, i_hi) * step


def _nice_step(span: float) -> float:
    if span <= 0:
        return 1.0
    target = span / 7.0
    power = 10 ** math.floor(math.log10(target))
    mantissa = target / power
    if mantissa <= 1.0:
        base = 1.0
    elif mantissa <= 2.0:
        base = 2.0
    elif mantissa <= 2.5:
        base = 2.5
    elif mantissa <= 5.0:
        base = 5.0
    else:
        base = 10.0
    return base * power


def _poly_eval(coeffs: tuple[float, float, float, float], t: float) -> float:
    a3, a2, a1, a0 = coeffs
    return a3 * (t**3) + a2 * (t**2) + a1 * t + a0


def _poly_latex(coeffs: tuple[float, float, float, float], variable: str = "t") -> str:
    a3, a2, a1, a0 = coeffs
    parts: list[str] = []

    if abs(a3) > 1e-12:
        if abs(a3 - 1.0) < 1e-12:
            parts.append(f"{variable}^3")
        elif abs(a3 + 1.0) < 1e-12:
            parts.append(f"-{variable}^3")
        else:
            parts.append(f"{_fmt(a3)}{variable}^3")

    if abs(a2) > 1e-12:
        term = f"{_fmt(abs(a2))}{variable}^2"
        if parts:
            parts.append(("+" if a2 >= 0 else "-") + term)
        else:
            parts.append(term if a2 >= 0 else f"-{term}")

    if abs(a1) > 1e-12:
        term = f"{_fmt(abs(a1))}{variable}"
        if parts:
            parts.append(("+" if a1 >= 0 else "-") + term)
        else:
            parts.append(term if a1 >= 0 else f"-{term}")

    if abs(a0) > 1e-12 or not parts:
        term = _fmt(abs(a0))
        if parts:
            parts.append(("+" if a0 >= 0 else "-") + term)
        else:
            parts.append(term if a0 >= 0 else f"-{term}")

    return "".join(parts)


def _first_derivative_coeffs(
    coeffs: tuple[float, float, float, float],
    exp_rate: float,
) -> tuple[float, float, float, float]:
    a3, a2, a1, a0 = coeffs
    # (p(t)e^{-ct})' = (p'(t) - c p(t))e^{-ct}; represented again in t^3,t^2,t,1 basis.
    p_prime = (0.0, 3.0 * a3, 2.0 * a2, a1)
    return (
        p_prime[0] - exp_rate * a3,
        p_prime[1] - exp_rate * a2,
        p_prime[2] - exp_rate * a1,
        p_prime[3] - exp_rate * a0,
    )


_PLC_POLY_FORMS = [
    "ax+b",
    "ax^2+b",
    "ax^2+bx",
    "ax^3+bx^2",
]


def _requested_start_mode(task_index: int, poly_form: str) -> str:
    mode = "zero" if task_index % 2 == 0 else "positive"
    if mode == "zero" and poly_form in {"ax+b", "ax^2+b"}:
        return "positive"
    return mode


def _poly_from_form(form: str, a: float, b: float) -> tuple[float, float, float, float]:
    if form == "ax+b":
        return (0.0, 0.0, a, b)
    if form == "ax^2+bx":
        return (0.0, a, b, 0.0)
    if form == "ax^2+b":
        return (0.0, a, 0.0, b)
    if form == "ax^3+bx^2":
        return (a, b, 0.0, 0.0)
    if form == "ax^3+bx":
        return (a, 0.0, b, 0.0)
    if form == "ax^3+b":
        return (a, 0.0, 0.0, b)
    raise ValueError(f"Unbekannte Polynomform: {form}")


def _sample_exit_coeffs(rng: random.Random, form: str, t_end: float) -> tuple[float, float, float, float]:
    if form == "ax+b":
        b = _rand_step(rng, 4.0, 18.0, 1.0)
        a = -b / t_end
        return _poly_from_form(form, a, b)
    if form == "ax^2+b":
        b = _rand_step(rng, 8.0, 28.0, 1.0)
        a = -b / (t_end**2)
        return _poly_from_form(form, a, b)
    if form == "ax^2+bx":
        a = -_rand_step(rng, 0.4, 2.4, 0.1)
        b = -a * t_end
        return _poly_from_form(form, a, b)
    if form == "ax^3+bx^2":
        a = -_rand_step(rng, 0.04, 0.28, 0.01)
        b = -a * t_end
        return _poly_from_form(form, a, b)
    raise ValueError(f"Unbekannte Polynomform: {form}")


def _sample_non_exit_coeffs(rng: random.Random, form: str) -> tuple[float, float, float, float]:
    if form == "ax+b":
        a = _rand_step(rng, 0.2, 1.8, 0.1)
        b = _rand_step(rng, 0.0, 10.0, 1.0)
    elif form == "ax^2+b":
        a = _rand_step(rng, 0.2, 1.6, 0.1)
        b = _rand_step(rng, 0.0, 12.0, 1.0)
    elif form == "ax^2+bx":
        a = _rand_step(rng, 0.1, 1.2, 0.1)
        b = _rand_step(rng, 1.0, 8.0, 0.5)
    elif form == "ax^3+bx^2":
        a = _rand_step(rng, 0.02, 0.18, 0.01)
        b = _rand_step(rng, 0.4, 3.0, 0.1)
    else:
        raise ValueError(f"Unbekannte Polynomform: {form}")

    return _poly_from_form(form, a, b)


def _integral_t_pow_exp(t: float, power: int, exp_rate: float) -> float:
    exp_part = math.exp(-exp_rate * t)
    current = -exp_part / exp_rate
    if power == 0:
        return current

    for degree in range(1, power + 1):
        current = -(t**degree) * exp_part / exp_rate + (degree / exp_rate) * current
    return current


def _integrate_poly_times_exp(
    coeffs: tuple[float, float, float, float],
    exp_rate: float,
    a: float,
    b: float,
) -> float:
    if b <= a:
        return 0.0

    a3, a2, a1, a0 = coeffs
    total = 0.0
    for coefficient, degree in [(a0, 0), (a1, 1), (a2, 2), (a3, 3)]:
        if abs(coefficient) <= 1e-14:
            continue
        total += coefficient * (
            _integral_t_pow_exp(b, degree, exp_rate) - _integral_t_pow_exp(a, degree, exp_rate)
        )
    return total


def _integrate_case_u_exact(case: "_PLCCase", a: float, b: float) -> float:
    if b <= a:
        return 0.0
    return _integrate_poly_times_exp(case.coeffs, case.exp_rate, a, b) + case.offset * (b - a)


def _integrate_ekg_exact(case: "_EKGCase", kind: str, a: float, b: float) -> float:
    if b <= a:
        return 0.0

    raw_integral = _integrate_poly_times_exp((case.a3, case.b2, 0.0, 0.0), case.exp_rate, a, b)
    if kind == "raw":
        return raw_integral
    if kind == "e":
        return (1.0 + case.scale_k) * raw_integral
    if kind == "k":
        return case.scale_k * raw_integral + case.fix_cost * (b - a)
    if kind == "g":
        return raw_integral - case.fix_cost * (b - a)
    raise ValueError(f"Unbekannter Integraltyp: {kind}")


def _roots_by_scan(fn, lo: float, hi: float, steps: int = 2800) -> list[float]:
    roots: list[float] = []
    prev_x = lo
    prev_y = fn(prev_x)

    for idx in range(1, steps + 1):
        x = lo + (hi - lo) * idx / steps
        y = fn(x)

        if abs(y) < 1e-9:
            roots.append(x)
        elif prev_y * y < 0:
            left, right = prev_x, x
            left_y, right_y = prev_y, y
            for _ in range(60):
                mid = 0.5 * (left + right)
                mid_y = fn(mid)
                if abs(mid_y) < 1e-12:
                    left = right = mid
                    break
                if left_y * mid_y <= 0:
                    right, right_y = mid, mid_y
                else:
                    left, left_y = mid, mid_y
            roots.append(0.5 * (left + right))

        prev_x, prev_y = x, y

    unique: list[float] = []
    for value in sorted(roots):
        if not unique or abs(value - unique[-1]) > 1e-3:
            unique.append(value)
    return unique


@dataclass
class _PLCCase:
    coeffs: tuple[float, float, float, float]
    exp_rate: float
    offset: float
    t_end: float
    has_market_exit: bool

    @property
    def d1_coeffs(self) -> tuple[float, float, float, float]:
        return _first_derivative_coeffs(self.coeffs, self.exp_rate)

    @property
    def d2_coeffs(self) -> tuple[float, float, float, float]:
        return _first_derivative_coeffs(self.d1_coeffs, self.exp_rate)

    @property
    def d3_coeffs(self) -> tuple[float, float, float, float]:
        return _first_derivative_coeffs(self.d2_coeffs, self.exp_rate)

    def u(self, t: float) -> float:
        return _poly_eval(self.coeffs, t) * math.exp(-self.exp_rate * t) + self.offset

    def du(self, t: float) -> float:
        return _poly_eval(self.d1_coeffs, t) * math.exp(-self.exp_rate * t)

    def d2u(self, t: float) -> float:
        return _poly_eval(self.d2_coeffs, t) * math.exp(-self.exp_rate * t)

    def d3u(self, t: float) -> float:
        return _poly_eval(self.d3_coeffs, t) * math.exp(-self.exp_rate * t)


def _max_min_of_du(case: _PLCCase) -> tuple[float, float]:
    candidates = [0.0, case.t_end]
    for root in _roots_by_scan(case.d2u, 0.0, case.t_end):
        if 0.0 <= root <= case.t_end:
            candidates.append(root)

    max_t = max(candidates, key=case.du)
    min_t = min(candidates, key=case.du)
    return max_t, min_t


def _max_of_u(case: _PLCCase) -> tuple[float, float]:
    candidates = [0.0, case.t_end]
    for root in _roots_by_scan(case.du, 0.0, case.t_end):
        if 0.0 <= root <= case.t_end:
            candidates.append(root)

    t_max = max(candidates, key=case.u)
    return t_max, case.u(t_max)


def _max_u_time_by_sign_change(case: _PLCCase) -> float | None:
    for root in _roots_by_scan(case.du, 0.0, case.t_end):
        left = max(0.0, root - 1e-3)
        right = min(case.t_end, root + 1e-3)
        if case.du(left) > 0 and case.du(right) < 0:
            return root
    return None


def _first_local_min_time(case: _PLCCase) -> float | None:
    for root in _roots_by_scan(case.du, 0.0, case.t_end):
        left = max(0.0, root - 1e-3)
        right = min(case.t_end, root + 1e-3)
        if case.du(left) < 0 and case.du(right) > 0:
            return root
    return None


def _sample_plc_case(
    rng: random.Random,
    *,
    mode: str,
    forced_form: str | None = None,
    start_mode: str = "any",
) -> _PLCCase:
    for _ in range(3200):
        is_exit = rng.random() < 0.5
        edge_mode = rng.choice(["any", "edge", "inner"])
        poly_form = forced_form if forced_form is not None else rng.choice(_PLC_POLY_FORMS)

        if is_exit:
            exp_rate = _rand_step(rng, 0.1, 0.9, 0.1)
            t_end = _rand_step(rng, 8.0, 24.0, 1.0)
            coeffs = _sample_exit_coeffs(rng, poly_form, t_end)
            offset = 0.0
        else:
            exp_rate = _rand_step(rng, 0.1, 0.9, 0.1)
            t_end = _rand_step(rng, 10.0, 22.0, 1.0)
            coeffs = _sample_non_exit_coeffs(rng, poly_form)
            if start_mode == "zero":
                offset = 0.0
            else:
                offset = _rand_step(rng, 1.5, 7.0, 0.5)

        case = _PLCCase(
            coeffs=coeffs,
            exp_rate=exp_rate,
            offset=offset,
            t_end=t_end,
            has_market_exit=is_exit,
        )

        u0 = case.u(0.0)
        if start_mode == "zero" and abs(u0) > 1e-8:
            continue
        if start_mode == "positive" and u0 < 0.8:
            continue

        t_peak = _max_u_time_by_sign_change(case)
        if t_peak is None:
            continue

        if case.du(0.0) < -1e-8:
            t_local_min = _first_local_min_time(case)
            if t_local_min is None:
                continue
            if t_local_min < 0.1 * case.t_end:
                continue

        t_inc, t_dec = _max_min_of_du(case)
        if abs(t_inc - t_dec) < 0.2:
            continue

        if edge_mode == "edge":
            edge_dist = min(
                abs(t_inc - 0.0),
                abs(t_inc - case.t_end),
                abs(t_dec - 0.0),
                abs(t_dec - case.t_end),
            )
            if edge_dist > 0.35:
                continue
        elif edge_mode == "inner":
            if min(t_inc, t_dec) < 0.35 or max(t_inc, t_dec) > case.t_end - 0.35:
                continue

        _, y_max = _max_of_u(case)
        if y_max < case.u(0.0) + 2.0:
            continue

        if mode == "graph_u":
            if not case.has_market_exit:
                if case.offset < 1.0:
                    continue
                if case.offset < 0.1 * y_max:
                    continue
            t_eval = min(case.t_end * 0.85, max(1.0, case.t_end * 0.35))
            if case.u(t_eval) <= 0.0:
                continue

        return case

    raise ValueError("Konnte keine geeigneten Produktlebenszyklus-Parameter erzeugen.")


def _display_equation(expression: str) -> str:
    return f"$$ {expression} $$"


def _align_equations(expressions: list[str]) -> str:
    lines: list[str] = []
    for expression in expressions:
        cleaned = expression.strip().rstrip(".")
        if "=" in cleaned:
            left, right = cleaned.split("=", 1)
            lines.append(f"{left}&={right}")
        else:
            lines.append(cleaned)
    joined = r" \\ ".join(lines)
    return f"$$ \\begin{{align*}} {joined} \\end{{align*}} $$"


def _u_latex(case: _PLCCase) -> str:
    exp_part = f"e^{{-{_fmt(case.exp_rate, 2)}t}}"
    poly = _poly_latex(case.coeffs, variable="t")
    if abs(case.offset) < 1e-12:
        return f"u(t)=({poly}){exp_part}"
    return f"u(t)=({poly}){exp_part}{_signed(case.offset, 2)}"


def _du_latex(case: _PLCCase, order: int) -> str:
    coeff_map = {1: case.d1_coeffs, 2: case.d2_coeffs, 3: case.d3_coeffs}
    coeffs = coeff_map[order]
    poly = _poly_latex(coeffs, variable="t")
    exp_part = f"e^{{-{_fmt(case.exp_rate, 2)}t}}"
    if order == 1:
        name = "u'(t)"
    elif order == 2:
        name = "u''(t)"
    else:
        name = "u'''(t)"
    return f"{name}=({poly}){exp_part}"


def _effective_u_plot_limit(case: _PLCCase, t_peak: float, y_peak: float) -> float:
    if case.has_market_exit:
        return case.t_end

    amplitude = max(0.8, y_peak - case.offset)
    threshold = max(0.2, 0.04 * amplitude)
    slope_threshold = max(0.03, 0.015 * amplitude)
    t = max(t_peak + 1.0, case.t_end)
    upper = min(75.0, max(case.t_end * 2.8, t_peak + 18.0))
    stable_hits = 0
    prev_val = case.u(t)

    while t < upper:
        current_val = case.u(t)
        slope_estimate = abs(current_val - prev_val) / 0.25
        if abs(current_val - case.offset) <= threshold and slope_estimate <= slope_threshold:
            stable_hits += 1
            # Require a sustained near-horizontal tail so the asymptote is visually clear.
            if stable_hits >= 8:
                return min(upper, max(case.t_end * 1.35, t + 2.0))
        else:
            stable_hits = 0

        prev_val = current_val
        t += 0.25

    return max(case.t_end * 1.35, upper)


def _effective_du_plot_limit(case: _PLCCase, t_peak: float) -> float:
    d2_roots = [root for root in _roots_by_scan(case.d2u, 0.0, case.t_end) if 0.0 <= root <= case.t_end]
    right_ref = max(d2_roots) if d2_roots else t_peak
    return min(55.0, max(16.0, case.t_end * 1.4, right_ref + 0.4 * case.t_end, t_peak + 6.0))


def _plot_visual(
    *,
    title: str,
    x_axis: str,
    y_axis: str,
    trace_name: str,
    x_values: list[float],
    y_values: list[float],
    x_tick: float,
    y_tick: float,
    x_range: tuple[float, float],
    y_range: tuple[float, float],
) -> dict:
    return {
        "type": "plot",
        "spec": {
            "type": "plotly",
            "traces": [
                {
                    "kind": "scatter",
                    "mode": "lines",
                    "name": trace_name,
                    "x": x_values,
                    "y": y_values,
                    "line": {"color": "#1f77b4", "width": 2},
                }
            ],
            "layout": {
                "title": title,
                "xaxis": {
                    "title": x_axis,
                    "range": [round(x_range[0], 4), round(x_range[1], 4)],
                    "dtick": round(x_tick, 4),
                },
                "yaxis": {
                    "title": y_axis,
                    "range": [round(y_range[0], 4), round(y_range[1], 4)],
                    "dtick": round(y_tick, 4),
                },
            },
        },
    }


class ProduktlebenszyklusIntegraleGemischtGenerator(TaskGenerator):
    generator_key = "analysis.produktlebenszyklus.integrale_gemischt"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        while len(tasks) < count:
            requested_form = _PLC_POLY_FORMS[len(tasks) % len(_PLC_POLY_FORMS)]
            requested_start = _requested_start_mode(len(tasks), requested_form)
            case = _sample_plc_case(
                rng,
                mode="integrals",
                forced_form=requested_form,
                start_mode=requested_start,
            )

            if case.has_market_exit:
                t_lifecycle = case.t_end
                lifecycle_text = "Der Produktlebenszyklus endet, wenn das Produkt vom Markt genommen wird."
            else:
                t_lifecycle = case.t_end
                lifecycle_text = f"Der Produktlebenszyklus endet nach {_fmt(t_lifecycle, 2)} Jahren."

            a = float(rng.randint(2, max(3, int(t_lifecycle * 0.4))))
            b = float(rng.randint(max(int(a) + 1, int(t_lifecycle * 0.6)), max(int(a) + 1, int(t_lifecycle))))
            n = float(rng.randint(2, max(3, int(t_lifecycle * 0.8))))
            t_eval = float(rng.randint(1, max(1, int(t_lifecycle))))

            total = _integrate_case_u_exact(case, 0.0, t_lifecycle)
            interval_value = _integrate_case_u_exact(case, a, b)
            avg_value = _integrate_case_u_exact(case, 0.0, n) / n
            point_value = case.u(t_eval)

            items = [
                (
                    "den Umsatz, der während des gesamten Lebenszyklus des Produkts erzielt wird.",
                    _num_tol(total, tolerance=0.1),
                ),
                (
                    f"den Umsatz, der vom Ende des {int(a)}. bis zum Ende des {int(b)}. Jahres erzielt wird.",
                    _num_tol(interval_value, tolerance=0.1),
                ),
                (
                    f"den jährlichen Umsatz, der durchschnittlich in den ersten {int(n)} Jahren erzielt wird.",
                    _num_tol(avg_value, tolerance=0.1),
                ),
                (
                    f"den jährlichen Umsatz nach {int(t_eval)} Jahren.",
                    _num_tol(point_value, tolerance=0.1),
                ),
            ]
            rng.shuffle(items)

            tasks.append(
                Task(
                    einleitung=(
                        "Die Funktion"
                        f"{_display_equation(_u_latex(case))}"
                        "gibt den jährlichen Umsatz eines Produkts seit seiner Einführung an."
                        f"{lifecycle_text}" "Bestimmen Sie (auf 2 NKS gerundet)"
                    ),
                    fragen=[q for q, _ in items],
                    antworten=[a_ for _, a_ in items],
                )
            )

        return tasks


@dataclass
class _EKGCase:
    a3: float
    b2: float
    exp_rate: float
    scale_k: float
    fix_cost: float
    t_end: float

    def raw(self, t: float) -> float:
        return (self.a3 * (t**3) + self.b2 * (t**2)) * math.exp(-self.exp_rate * t)

    def e(self, t: float) -> float:
        return (1.0 + self.scale_k) * self.raw(t)

    def k(self, t: float) -> float:
        return self.scale_k * self.raw(t) + self.fix_cost

    def g(self, t: float) -> float:
        return self.e(t) - self.k(t)


def _sample_ekg_case(rng: random.Random) -> _EKGCase:
    for _ in range(3000):
        exp_rate = _rand_step(rng, 0.1, 0.9, 0.1)
        t_end = _rand_step(rng, 8.0, 24.0, 1.0)
        k_shape = _rand_step(rng, 0.5, 2.0, 0.1)
        a3 = -k_shape
        b2 = k_shape * t_end
        scale_k = _rand_step(rng, 0.3, 0.8, 0.1)

        tmp = _EKGCase(a3=a3, b2=b2, exp_rate=exp_rate, scale_k=scale_k, fix_cost=1.0, t_end=t_end)

        peak_raw = max(tmp.raw(x * t_end / 500.0) for x in range(1, 500))
        if peak_raw <= 1.0:
            continue

        fix_cost = _rand_step(rng, 0.2 * peak_raw, 0.6 * peak_raw, 0.1)
        case = _EKGCase(
            a3=a3,
            b2=b2,
            exp_rate=exp_rate,
            scale_k=scale_k,
            fix_cost=fix_cost,
            t_end=t_end,
        )

        roots = [r for r in _roots_by_scan(case.g, 0.0, case.t_end) if 1e-3 < r < case.t_end - 1e-3]
        if len(roots) < 2:
            continue

        t1, t2 = roots[0], roots[1]
        if t2 - t1 < 0.8:
            continue

        return case

    raise ValueError("Konnte keine geeigneten EKG-Parameter erzeugen.")


def _ekg_latex(case: _EKGCase) -> tuple[str, str]:
    e_factor = 1.0 + case.scale_k
    e_poly = f"{_fmt(e_factor * case.a3, 3)}t^3{_signed(e_factor * case.b2, 3)}t^2"
    k_poly = f"{_fmt(case.scale_k * case.a3, 3)}t^3{_signed(case.scale_k * case.b2, 3)}t^2"
    exp_part = f"e^{{-{_fmt(case.exp_rate, 2)}t}}"
    e_ltx = f"E(t)=({e_poly}){exp_part}"
    k_ltx = f"K(t)=({k_poly}){exp_part}{_signed(case.fix_cost, 2)}"
    return e_ltx, k_ltx


class ProduktlebenszyklusEKGZyklusGemischtGenerator(TaskGenerator):
    generator_key = "analysis.produktlebenszyklus.ekg_zyklus_gemischt"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        while len(tasks) < count:
            case = _sample_ekg_case(rng)
            roots = [r for r in _roots_by_scan(case.g, 0.0, case.t_end) if 1e-3 < r < case.t_end - 1e-3]
            t1, t2 = roots[0], roots[1]

            total_profit = _integrate_ekg_exact(case, "g", 0.0, case.t_end)
            v_t1 = -_integrate_ekg_exact(case, "g", 0.0, t1)
            v_t = -_integrate_ekg_exact(case, "g", 0.0, case.t_end)
            t_max_loss = t1 if v_t1 >= v_t else case.t_end

            a = float(rng.randint(1, max(2, int(case.t_end * 0.4))))
            b = float(rng.randint(max(int(a) + 1, int(case.t_end * 0.6)), max(int(a) + 1, int(case.t_end))))
            t_eval = float(rng.randint(1, max(1, int(case.t_end * 0.95))))

            integral_kind = rng.choice(["e", "k", "g"])
            if integral_kind == "e":
                mixed_q = (
                    f"die Erlöse, die vom Ende des {int(a)}. bis zum Ende des {int(b)}. Jahres erzielt werden.",
                    _num_tol(_integrate_ekg_exact(case, "e", a, b), tolerance=0.1),
                )
            elif integral_kind == "k":
                mixed_q = (
                    f"die Kosten, die vom Ende des {int(a)}. bis zum Ende des {int(b)}. Jahres anfallen.",
                    _num_tol(_integrate_ekg_exact(case, "k", a, b), tolerance=0.1),
                )
            else:
                mixed_q = (
                    f"die Gewinne, die vom Ende des {int(a)}. bis zum Ende des {int(b)}. Jahres erzielt werden.",
                    _num_tol(_integrate_ekg_exact(case, "g", a, b), tolerance=0.1),
                )

            point_kind = rng.choice(["e", "k", "g"])
            if point_kind == "e":
                point_q = (
                    f"die jährlichen Erlöse nach {int(t_eval)} Jahren.",
                    _num_tol(case.e(t_eval), tolerance=0.1),
                )
            elif point_kind == "k":
                point_q = (
                    f"die jährlichen Kosten nach {int(t_eval)} Jahren.",
                    _num_tol(case.k(t_eval), tolerance=0.1),
                )
            else:
                point_q = (
                    f"die jährlichen Gewinne nach {int(t_eval)} Jahren.",
                    _num_tol(case.g(t_eval), tolerance=0.1),
                )

            items = [
                mixed_q,
                (
                    "den Gesamtgewinn, der während des Produktlebenszyklus erwirtschaftet wird.",
                    _num_tol(total_profit, tolerance=0.01),
                ),
                (
                    "den Zeitraum, in dem die Kosten von den Erlösen gedeckt werden.",
                    _interval_num(t1, t2, tolerance=0.01),
                ),
                point_q,
                (
                    "den Zeitpunkt t, an dem der maximale Gesamtverlust auftritt. "
                    "Der Gesamtverlust in Abhängigkeit vom Zeitpunkt t bezeichnet hierbei denjenigen Verlust, "
                    "der seit der Produkteinführung bis zum Zeitpunkt t erzielt wird.",
                    _num_tol(t_max_loss, tolerance=0.1),
                ),
            ]
            rng.shuffle(items)
            e_ltx, k_ltx = _ekg_latex(case)

            tasks.append(
                Task(
                    einleitung=(
                        "Die Funktionen"
                        f"{_align_equations([e_ltx, k_ltx])}"
                        "geben den jährlichen Erlös und die jährlichen Kosten seit der Einführung "
                        "eines Produkts an. "
                        f"Der Lebenszyklus des Produkts endet nach {_fmt(case.t_end, 2)} Jahren. Bestimmen Sie (auf 2 NKS gerundet)"
                    ),
                    fragen=[q for q, _ in items],
                    antworten=[a_ for _, a_ in items],
                )
            )

        return tasks


class ProduktlebenszyklusKennzahlenGraphischUmsatzGenerator(TaskGenerator):
    generator_key = "analysis.produktlebenszyklus.kennzahlen_graphisch_umsatz"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        while len(tasks) < count:
            requested_form = _PLC_POLY_FORMS[len(tasks) % len(_PLC_POLY_FORMS)]
            requested_start = _requested_start_mode(len(tasks), requested_form)
            case = _sample_plc_case(
                rng,
                mode="graph_u",
                forced_form=requested_form,
                start_mode=requested_start,
            )
            t_peak, y_peak = _max_of_u(case)
            t_inc, t_dec = _max_min_of_du(case)

            t_limit = _effective_u_plot_limit(case, t_peak, y_peak)
            x_values = [round(t_limit * idx / 260.0, 4) for idx in range(261)]
            if case.has_market_exit:
                y_values = [round(max(0.0, case.u(x)), 6) for x in x_values]
            else:
                y_values = [round(case.u(x), 6) for x in x_values]

            t_eval = uniform_sig(rng, 1.0, min(case.t_end * 0.85, t_limit * 0.9))

            y_min = min(0.0, min(y_values) * 1.05)
            y_max = max(y_values) * 1.08
            y_span = max(1.0, y_max - y_min)
            x_tick = _nice_step(t_limit)
            y_tick = _nice_step(y_span)
            tol_x = x_tick / 4.0
            tol_y = y_tick / 4.0

            questions = [
                ("den jährlichen Umsatz bei der Produkteinführung.", _num_tol(case.u(0.0), tolerance=tol_y)),
                (
                    "den Zeitpunkt des höchsten jährlichen Umsatzes.",
                    _num_tol(t_peak, tolerance=tol_x),
                ),
                (
                    "die Höhe des höchsten jährlichen Umsatzes.",
                    _num_tol(y_peak, tolerance=tol_y),
                ),
                (
                    f"den jährlichen Umsatz nach {_fmt(t_eval, 2)} Jahren.",
                    _num_tol(case.u(t_eval), tolerance=tol_y),
                ),
                (
                    "den Zeitpunkt des stärksten Umsatzanstiegs.",
                    _num_tol(t_inc, tolerance=tol_x),
                ),
                (
                    "den Zeitpunkt des stärksten Umsatzrückgangs.",
                    _num_tol(t_dec, tolerance=tol_x),
                ),
            ]

            if case.has_market_exit:
                questions.append(
                    ("den Zeitpunkt des Marktaustritts.", _num_tol(case.t_end, tolerance=tol_x))
                )
            else:
                questions.append(
                    (
                        "den langfristig zu erwartenden jährlichen Umsatz.",
                        _num_tol(case.offset, tolerance=tol_y),
                    )
                )

            rng.shuffle(questions)

            tasks.append(
                Task(
                    einleitung=(
                        "Das Diagramm zeigt den Graphen der Umsatzfunktion eines Produktlebenszyklus. "
                        "Bestimmen Sie anhand des Graphen."
                    ),
                    fragen=[q for q, _ in questions],
                    antworten=[a_ for _, a_ in questions],
                    visual=_plot_visual(
                        title="Produktlebenszyklus - Umsatzfunktion u(t)",
                        x_axis="Zeit t in Jahren",
                        y_axis="jährlicher Umsatz u(t)",
                        trace_name="u(t)",
                        x_values=x_values,
                        y_values=y_values,
                        x_tick=x_tick,
                        y_tick=y_tick,
                        x_range=(0.0, t_limit),
                        y_range=(y_min, y_max),
                    ),
                )
            )

        return tasks


class ProduktlebenszyklusKennzahlenGraphischAbleitungGenerator(TaskGenerator):
    generator_key = "analysis.produktlebenszyklus.kennzahlen_graphisch_ableitung"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        while len(tasks) < count:
            requested_form = _PLC_POLY_FORMS[len(tasks) % len(_PLC_POLY_FORMS)]
            requested_start = _requested_start_mode(len(tasks), requested_form)
            case = _sample_plc_case(
                rng,
                mode="graph_du",
                forced_form=requested_form,
                start_mode=requested_start,
            )
            t_peak = _max_u_time_by_sign_change(case)
            if t_peak is None:
                continue

            t_inc, t_dec = _max_min_of_du(case)
            t_limit = _effective_du_plot_limit(case, t_peak)
            t_eval = uniform_sig(rng, 1.0, min(case.t_end * 0.9, t_limit * 0.9))

            x_values = [round(t_limit * idx / 260.0, 4) for idx in range(261)]
            y_values = [round(case.du(x), 6) for x in x_values]

            y_abs = max(abs(min(y_values)), abs(max(y_values)))
            y_pad = max(0.8, 0.15 * y_abs)
            y_min = min(y_values) - y_pad
            y_max = max(y_values) + y_pad
            x_tick = _nice_step(t_limit)
            y_tick = _nice_step(y_max - y_min)
            tol_x = x_tick / 4.0
            tol_y = y_tick / 4.0

            questions = [
                (
                    "den Zeitpunkt des höchsten jährlichen Umsatzes.",
                    _num_tol(t_peak, tolerance=tol_x),
                ),
                (
                    "den Zeitpunkt des stärksten Umsatzanstiegs.",
                    _num_tol(t_inc, tolerance=tol_x),
                ),
                (
                    "den Zeitpunkt des stärksten Umsatzrückgangs.",
                    _num_tol(t_dec, tolerance=tol_x),
                ),
                (
                    f"die jährliche Veränderung des Umsatzes nach {_fmt(t_eval, 2)} Jahren.",
                    _num_tol(case.du(t_eval), tolerance=tol_y),
                ),
            ]
            rng.shuffle(questions)

            tasks.append(
                Task(
                    einleitung=(
                        "Das Diagramm zeigt den Graphen der Ableitungsfunktion eines Produktlebenszyklus. "
                        "Bestimmen Sie anhand des Graphen."
                    ),
                    fragen=[q for q, _ in questions],
                    antworten=[a_ for _, a_ in questions],
                    visual=_plot_visual(
                        title="Produktlebenszyklus - Ableitungsfunktion u'(t)",
                        x_axis="Zeit t in Jahren",
                        y_axis="Änderung u'(t) in GE/Jahr",
                        trace_name="u'(t)",
                        x_values=x_values,
                        y_values=y_values,
                        x_tick=x_tick,
                        y_tick=y_tick,
                        x_range=(0.0, t_limit),
                        y_range=(y_min, y_max),
                    ),
                )
            )

        return tasks


class ProduktlebenszyklusKennzahlenRechnerischGesamtGenerator(TaskGenerator):
    generator_key = "analysis.produktlebenszyklus.kennzahlen_rechnerisch_gesamt"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        while len(tasks) < count:
            requested_form = _PLC_POLY_FORMS[len(tasks) % len(_PLC_POLY_FORMS)]
            requested_start = _requested_start_mode(len(tasks), requested_form)
            case = _sample_plc_case(
                rng,
                mode="calc",
                forced_form=requested_form,
                start_mode=requested_start,
            )
            t_peak = _max_u_time_by_sign_change(case)
            if t_peak is None:
                continue

            t_inc, t_dec = _max_min_of_du(case)
            _, y_peak = _max_of_u(case)

            t_eval_du = uniform_sig(rng, 1.0, case.t_end * 0.9)
            t_eval_u = uniform_sig(rng, 1.0, case.t_end)

            items = [
                (
                    "den Zeitpunkt, an dem der Umsatz am stärksten zurückgeht.",
                    _num_tol(t_dec, tolerance=0.1),
                ),
                (
                    f"die jährliche Veränderung des Umsatzes nach {_fmt(t_eval_du, 2)} Jahren.",
                    _num_tol(case.du(t_eval_du), tolerance=0.1),
                ),
                (
                    "den Zeitpunkt, an dem der höchste jährliche Umsatz erzielt wird.",
                    _num_tol(t_peak, tolerance=0.1),
                ),
                (
                    f"den jährlichen Umsatz nach {_fmt(t_eval_u, 2)} Jahren.",
                    _num_tol(case.u(t_eval_u), tolerance=0.1),
                ),
                (
                    "den Zeitpunkt, an dem der Umsatz am stärksten ansteigt.",
                    _num_tol(t_inc, tolerance=0.1),
                ),
                (
                    "den jährlichen Umsatz, der bei der Produkteinführung erzielt wird.",
                    _num_tol(case.u(0.0), tolerance=0.1),
                ),
                (
                    ", ob entweder das Produkt in Zukunft vom Markt genommen wird oder ob ein langfristig "
                    "zu erwartender jährlicher Umsatz vorliegt. Bestimmen Sie dementsprechend entweder den "
                    "Zeitpunkt, an dem das Produkt vom Markt genommen wird, oder den langfristig zu erwartenden "
                    "jährlichen Umsatz.",
                    _num_tol(
                        case.t_end if case.has_market_exit else case.offset,
                        tolerance=0.1 if case.has_market_exit else 0.01,
                    ),
                ),
                (
                    "die Höhe des höchsten jährlichen Umsatzes.",
                    _num_tol(y_peak, tolerance=0.1),
                ),
            ]
            rng.shuffle(items)

            tasks.append(
                Task(
                    einleitung=(
                        "Die Funktion $u(t)$ gibt den jährlichen Umsatz eines Produkts seit seiner Einführung an. Gegeben sind:"
                        f"{_align_equations([_u_latex(case), _du_latex(case, 1), _du_latex(case, 2), _du_latex(case, 3)])}"
                        "Bestimmen Sie (auf 2 NKS gerundet)"
                    ),
                    fragen=[q for q, _ in items],
                    antworten=[a_ for _, a_ in items],
                )
            )

        return tasks
