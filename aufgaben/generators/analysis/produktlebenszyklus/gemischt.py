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


def _fmt_dot(value: float, decimals: int = 4) -> str:
    """Format a number with dot decimal separator (for plain-text/AI context)."""
    rounded = round(float(value), decimals)
    text = f"{rounded:.{decimals}f}".rstrip("0").rstrip(".")
    if text in {"", "-0"}:
        text = "0"
    return text


def _u_term_plain(case: "_PLCCase") -> str:
    """Build a plain-text function term for u(t), e.g. '(0.5*t^2+3*t)*exp(-0.2*t)+5'."""
    poly = _poly_plain(case.coeffs)
    exp_part = f"exp(-{_fmt_dot(case.exp_rate, 2)}*t)"
    base = f"({poly})*{exp_part}"
    if abs(case.offset) < 1e-12:
        return base
    sign = "+" if case.offset >= 0 else ""
    return f"{base}{sign}{_fmt_dot(case.offset, 2)}"


def _du_term_plain(case: "_PLCCase", order: int = 1) -> str:
    """Build a plain-text function term for u'(t) or u''(t)."""
    coeff_map = {1: case.d1_coeffs, 2: case.d2_coeffs, 3: case.d3_coeffs}
    coeffs = coeff_map[order]
    poly = _poly_plain(coeffs)
    exp_part = f"exp(-{_fmt_dot(case.exp_rate, 2)}*t)"
    return f"({poly})*{exp_part}"


def _poly_plain(coeffs: tuple[float, float, float, float]) -> str:
    """Format polynomial with dot-decimal for plain-text context."""
    a3, a2, a1, a0 = coeffs
    parts: list[str] = []

    for coeff, power in [(a3, 3), (a2, 2), (a1, 1), (a0, 0)]:
        if abs(coeff) < 1e-12:
            continue
        abs_c = abs(coeff)
        if power == 0:
            term = _fmt_dot(abs_c)
        elif abs(abs_c - 1.0) < 1e-12:
            term = f"t^{power}" if power > 1 else "t"
        else:
            term = f"{_fmt_dot(abs_c)}*t^{power}" if power > 1 else f"{_fmt_dot(abs_c)}*t"
        if parts:
            parts.append(("+" if coeff >= 0 else "-") + term)
        else:
            parts.append(term if coeff >= 0 else f"-{term}")

    return "".join(parts) if parts else "0"


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


def _u_latex(case: _PLCCase, fname: str = "u") -> str:
    exp_part = f"e^{{-{_fmt(case.exp_rate, 2)}t}}"
    poly = _poly_latex(case.coeffs, variable="t")
    if abs(case.offset) < 1e-12:
        return f"{fname}(t)=({poly}){exp_part}"
    return f"{fname}(t)=({poly}){exp_part}{_signed(case.offset, 2)}"


def _du_latex(case: _PLCCase, order: int, fname: str = "u") -> str:
    coeff_map = {1: case.d1_coeffs, 2: case.d2_coeffs, 3: case.d3_coeffs}
    coeffs = coeff_map[order]
    poly = _poly_latex(coeffs, variable="t")
    exp_part = f"e^{{-{_fmt(case.exp_rate, 2)}t}}"
    name = f"{fname}{chr(39) * order}(t)"
    return f"{name}=({poly}){exp_part}"


@dataclass(frozen=True)
class _Kontext:
    """Sachkontext: Absatz (ME/Monat) als Standard, Umsatz (GE/Jahr) als Variante."""

    groesse: str
    fname: str
    einheit: str
    zeit: str
    zeit_pl: str
    zeit_gen: str
    adj: str

    @property
    def rate(self) -> str:
        return f"{self.einheit}/{self.zeit}"

    @property
    def gesamt(self) -> str:
        return f"Gesamt{self.groesse.lower()}"


_ABSATZ = _Kontext("Absatz", "a", "ME", "Monat", "Monaten", "Monats", "monatlich")
_UMSATZ = _Kontext("Umsatz", "u", "GE", "Jahr", "Jahren", "Jahres", "jährlich")


def _kontext_for(task_index: int) -> _Kontext:
    return _UMSATZ if task_index % 4 == 3 else _ABSATZ


def _nice_in(rng: random.Random, lo: float, hi: float, steps=(1.0, 0.5, 0.25, 0.1)) -> float | None:
    if hi < lo:
        return None
    for step in steps:
        i_lo = math.ceil(lo / step - 1e-9)
        i_hi = math.floor(hi / step + 1e-9)
        if i_lo <= i_hi:
            return rng.randint(i_lo, i_hi) * step
    return None


def _mc(options: list[str], correct: str) -> str:
    parts = "".join(f"~={opt}" if opt == correct else f"~{opt}" for opt in options)
    return f"{{1:MC:{parts}}}"


def _zeitraum_text(k: _Kontext, p: int, q: int) -> str:
    if p == 0:
        return f"in den ersten {q} {k.zeit_pl}"
    return f"vom Ende des {p}. bis zum Ende des {q}. {k.zeit_gen}"


def _effective_u_plot_limit(case: _PLCCase, t_peak: float, y_peak: float) -> float:
    if case.has_market_exit:
        return case.t_end + max(0.6, min(1.2, 0.05 * case.t_end))

    tau = 1.0 / case.exp_rate
    amplitude = max(0.8, abs(y_peak - case.offset), abs(case.u(0.0) - case.offset))
    threshold = max(0.05, 0.05 * amplitude)
    upper = min(90.0, max(case.t_end + 4.0 * tau, t_peak + 5.0 * tau, t_peak + 12.0))
    tail_buffer = max(1.0, min(2.0, 0.5 * tau))
    t = t_peak + 0.25
    stable_hits = 0

    while t < upper:
        if abs(case.u(t) - case.offset) <= threshold:
            stable_hits += 1
            if stable_hits >= 3:
                return min(upper, t + tail_buffer)
        else:
            stable_hits = 0

        t += 0.25

    return upper


def _effective_du_plot_limit(case: _PLCCase, t_peak: float) -> float:
    t_inc, t_dec = _max_min_of_du(case)
    tau = 1.0 / case.exp_rate
    anchor = max(t_peak, t_inc, t_dec)
    scan_end = min(90.0, max(anchor + 4.5 * tau, case.t_end + 2.5 * tau, 14.0))

    later_roots = [
        root
        for root in _roots_by_scan(case.du, 0.0, scan_end, steps=4200)
        if root > anchor + 1e-3
    ]
    if later_roots:
        anchor = later_roots[-1]

    amplitude = max(0.4, abs(case.du(t_inc)), abs(case.du(t_dec)))
    threshold = max(0.02, 0.05 * amplitude)
    tail_buffer = max(1.0, min(2.5, 0.8 * tau))

    t = anchor + 0.25
    stable_hits = 0
    while t < scan_end:
        if abs(case.du(t)) <= threshold:
            stable_hits += 1
            if stable_hits >= 3:
                return min(scan_end, t + tail_buffer)
        else:
            stable_hits = 0
        t += 0.25

    return scan_end


def _sample_curve_values(x_limit: float, fn, *, points: int = 261) -> list[float]:
    if points <= 1:
        return [float(fn(0.0))]

    values: list[float] = []
    for idx in range(points):
        t = x_limit * idx / (points - 1)
        values.append(float(fn(t)))
    return values


def _tight_axis_range(
    values: list[float],
    *,
    include_zero: bool = False,
    snap_lower_to_zero: bool = False,
    pad_ratio: float = 0.08,
) -> tuple[float, float]:
    finite_values = [float(value) for value in values if math.isfinite(value)]
    if not finite_values:
        return (-1.0, 1.0) if include_zero else (0.0, 1.0)

    v_min = min(finite_values)
    v_max = max(finite_values)
    if include_zero:
        v_min = min(v_min, 0.0)
        v_max = max(v_max, 0.0)

    span = max(v_max - v_min, 0.6)
    pad = max(pad_ratio * span, 0.04 * max(1.0, abs(v_min), abs(v_max)))
    lower = v_min - pad
    upper = v_max + pad

    if snap_lower_to_zero and v_min >= 0.0 and v_min <= 0.15 * span:
        lower = 0.0

    if abs(lower) < 1e-12:
        lower = 0.0
    if abs(upper) < 1e-12:
        upper = 0.0
    return lower, upper


def _positive_y_axis_range(values: list[float], *, pad_ratio: float = 0.04) -> tuple[float, float]:
    finite_values = [float(value) for value in values if math.isfinite(value)]
    if not finite_values:
        return 0.0, 1.0

    y_max = max(0.0, max(finite_values))
    pad = max(0.12, pad_ratio * max(1.0, y_max))
    return 0.0, y_max + pad


def _plot_visual(
    *,
    title: str,
    x_axis: str,
    y_axis: str,
    trace_name: str,
    term: str,
    beschreibung: str,
    x_tick: float,
    y_tick: float,
    x_range: tuple[float, float],
    y_range: tuple[float, float],
) -> dict:
    spec: dict = {
        "type": "expression-curves",
        "title": title,
        "curves": [
            {
                "term": term,
                "variable": "t",
                "mode": "lines",
                "name": trace_name,
                "description": beschreibung,
                "line": {"color": "#1f77b4", "width": 2},
            }
        ],
        "points": 261,
        "layout": {
            "title": title,
            "xaxis": {
                "title": x_axis,
                "range": [round(x_range[0], 4), round(x_range[1], 4)],
                "dtick": round(x_tick, 4),
                "zeroline": True,
                "showline": True,
            },
            "yaxis": {
                "title": y_axis,
                "range": [round(y_range[0], 4), round(y_range[1], 4)],
                "dtick": round(y_tick, 4),
                "zeroline": True,
                "showline": True,
            },
        },
        "funktionen": [
            {
                "name": trace_name,
                "term": term,
                "beschreibung": beschreibung,
            }
        ],
    }
    return {"type": "plot", "spec": spec}




def _plc_case_for_task(rng: random.Random, task_index: int, mode: str) -> _PLCCase:
    requested_form = _PLC_POLY_FORMS[task_index % len(_PLC_POLY_FORMS)]
    requested_start = _requested_start_mode(task_index, requested_form)
    return _sample_plc_case(
        rng,
        mode=mode,
        forced_form=requested_form,
        start_mode=requested_start,
    )


def _cumulative_time(case: _PLCCase, target: float, t_hi: float) -> float | None:
    """Zeitpunkt z mit int_0^z u(t) dt = target (kumulierte Funktion ist dort monoton)."""
    if _integrate_case_u_exact(case, 0.0, t_hi) < target:
        return None
    lo, hi = 0.0, t_hi
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if _integrate_case_u_exact(case, 0.0, mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _threshold_question(rng: random.Random, case: _PLCCase, k: _Kontext, y_peak: float):
    lower = max(case.u(0.0), case.offset, 0.0)
    span = y_peak - lower
    if span <= 0.5:
        return None
    step = 1.0 if y_peak >= 8.0 else 0.5
    c = _nice_in(rng, lower + 0.25 * span, y_peak - 0.25 * span, steps=(step, 0.5, 0.25, 0.1))
    if c is None:
        return None

    scan_end = case.t_end if case.has_market_exit else case.t_end + 15.0 / case.exp_rate
    roots = _roots_by_scan(lambda t: case.u(t) - c, 0.0, scan_end, steps=6000)
    if len(roots) != 2 or roots[1] - roots[0] < 0.5:
        return None
    if case.u(scan_end) >= c:
        return None

    text = (
        f"den Zeitraum, in dem der {k.adj}e {k.groesse} über {_fmt(c, 2)} {k.rate} liegt."
    )
    return text, _interval_num(roots[0], roots[1], tolerance=0.05)


def _kruemmung_question(rng: random.Random, case: _PLCCase, k: _Kontext, t_inc: float, t_peak: float):
    if case.du(0.0) < 0.0:
        return None

    options: list[tuple[float, float, str]] = []
    if t_inc > 1.0:
        x2 = _nice_in(rng, 0.4 * t_inc, 0.85 * t_inc)
        if x2 is not None and x2 > 0:
            options.append((0.0, x2, "progressiv"))
    if t_peak - t_inc > 1.5:
        lo = t_inc + 0.15 * (t_peak - t_inc)
        hi = t_peak - 0.15 * (t_peak - t_inc)
        x1 = _nice_in(rng, lo, lo + 0.4 * (hi - lo))
        x2 = _nice_in(rng, lo + 0.6 * (hi - lo), hi)
        if x1 is not None and x2 is not None and x2 > x1:
            options.append((x1, x2, "degressiv"))
    if not options:
        return None

    x1, x2, answer = rng.choice(options)
    samples = [x1 + (x2 - x1) * i / 40 for i in range(1, 40)]
    if any(case.du(t) <= 0 for t in samples):
        return None
    expected_sign = 1 if answer == "progressiv" else -1
    if any(case.d2u(t) * expected_sign <= 0 for t in samples):
        return None

    text = (
        f"ob der {k.adj}e {k.groesse} im Zeitraum von $t={_fmt(x1, 2)}$ bis "
        f"$t={_fmt(x2, 2)}$ progressiv oder degressiv steigt."
    )
    return text, _mc(["progressiv", "degressiv"], answer)


class ProduktlebenszyklusKennzahlenGraphischUmsatzGenerator(TaskGenerator):
    generator_key = "analysis.produktlebenszyklus.kennzahlen_graphisch_umsatz"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        while len(tasks) < count:
            k = _kontext_for(len(tasks))
            case = _plc_case_for_task(rng, len(tasks), "graph_u")
            t_peak, y_peak = _max_of_u(case)
            t_inc, t_dec = _max_min_of_du(case)

            t_limit = _effective_u_plot_limit(case, t_peak, y_peak)
            if case.has_market_exit:
                y_values = _sample_curve_values(t_limit, lambda t: max(0.0, case.u(t)))
            else:
                y_values = _sample_curve_values(t_limit, case.u)

            t_eval = uniform_sig(rng, 1.0, min(case.t_end * 0.85, t_limit * 0.9))

            y_min, y_max = _positive_y_axis_range(y_values, pad_ratio=0.04)
            y_span = max(0.6, y_max - y_min)
            x_tick = _nice_step(t_limit)
            y_tick = _nice_step(y_span)
            tol_x = x_tick / 4.0
            tol_y = y_tick / 4.0

            questions = [
                (f"den {k.adj}en {k.groesse} bei der Markteinführung.", _num_tol(case.u(0.0), tolerance=tol_y)),
                (f"den Zeitpunkt des höchsten {k.adj}en {k.groesse}es.", _num_tol(t_peak, tolerance=tol_x)),
                (f"die Höhe des höchsten {k.adj}en {k.groesse}es.", _num_tol(y_peak, tolerance=tol_y)),
                (
                    f"den {k.adj}en {k.groesse} nach {_fmt(t_eval, 2)} {k.zeit_pl}.",
                    _num_tol(case.u(t_eval), tolerance=tol_y),
                ),
                (f"den Zeitpunkt des stärksten {k.groesse}anstiegs.", _num_tol(t_inc, tolerance=tol_x)),
                (f"den Zeitpunkt des stärksten {k.groesse}rückgangs.", _num_tol(t_dec, tolerance=tol_x)),
            ]

            if case.has_market_exit:
                questions.append(
                    ("den Zeitpunkt, zu dem das Produkt vom Markt genommen wird.", _num_tol(case.t_end, tolerance=tol_x))
                )
            else:
                questions.append(
                    (f"den langfristig zu erwartenden {k.adj}en {k.groesse}.", _num_tol(case.offset, tolerance=tol_y))
                )

            kruemmung = _kruemmung_question(rng, case, k, t_inc, t_peak)
            if kruemmung is not None:
                questions.append(kruemmung)

            rng.shuffle(questions)

            tasks.append(
                Task(
                    einleitung=(
                        f"Das Diagramm zeigt den Graphen der Funktion ${k.fname}$, die den {k.adj}en "
                        f"{k.groesse} eines Produkts in {k.rate} beschreibt ($t$ in {k.zeit_pl} seit der "
                        "Markteinführung). Bestimmen Sie anhand des Graphen"
                    ),
                    fragen=[q for q, _ in questions],
                    antworten=[a_ for _, a_ in questions],
                    visual=_plot_visual(
                        title=f"{k.groesse}funktion {k.fname}(t)",
                        x_axis=f"Zeit t in {k.zeit_pl}",
                        y_axis=f"{k.fname}(t) in {k.rate}",
                        trace_name=f"{k.fname}(t)",
                        term=_u_term_plain(case),
                        beschreibung=f"{k.adj}er {k.groesse}",
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
            k = _kontext_for(len(tasks))
            case = _plc_case_for_task(rng, len(tasks), "graph_du")
            t_peak = _max_u_time_by_sign_change(case)
            if t_peak is None:
                continue

            t_inc, t_dec = _max_min_of_du(case)
            t_limit = _effective_du_plot_limit(case, t_peak)
            t_eval = uniform_sig(rng, 1.0, min(case.t_end * 0.9, t_limit * 0.9))

            y_values = _sample_curve_values(t_limit, case.du)

            y_min, y_max = _tight_axis_range(y_values, include_zero=True, pad_ratio=0.04)
            x_tick = _nice_step(t_limit)
            y_tick = _nice_step(y_max - y_min)
            tol_x = x_tick / 4.0
            tol_y = y_tick / 4.0

            fprime = f"{k.fname}'"
            questions = [
                (f"den Zeitpunkt des höchsten {k.adj}en {k.groesse}es.", _num_tol(t_peak, tolerance=tol_x)),
                (f"den Zeitpunkt des stärksten {k.groesse}anstiegs.", _num_tol(t_inc, tolerance=tol_x)),
                (f"den Zeitpunkt des stärksten {k.groesse}rückgangs.", _num_tol(t_dec, tolerance=tol_x)),
                (
                    f"die momentane Änderungsrate des {k.adj}en {k.groesse}es nach {_fmt(t_eval, 2)} {k.zeit_pl}.",
                    _num_tol(case.du(t_eval), tolerance=tol_y),
                ),
            ]

            amplitude = max(abs(v) for v in y_values)
            candidates = [
                i * 0.5
                for i in range(1, int(t_limit * 0.9 / 0.5) + 1)
                if abs(case.du(i * 0.5)) > 0.2 * amplitude
            ]
            if candidates:
                x_sign = rng.choice(candidates)
                answer = "zunimmt" if case.du(x_sign) > 0 else "abnimmt"
                questions.append(
                    (
                        f"ob der {k.adj}e {k.groesse} zum Zeitpunkt $t={_fmt(x_sign, 2)}$ zunimmt oder abnimmt.",
                        _mc(["zunimmt", "abnimmt"], answer),
                    )
                )

            rng.shuffle(questions)

            tasks.append(
                Task(
                    einleitung=(
                        f"Die Funktion ${k.fname}$ beschreibt den {k.adj}en {k.groesse} eines Produkts in "
                        f"{k.rate} ($t$ in {k.zeit_pl} seit der Markteinführung). Das Diagramm zeigt den "
                        f"Graphen der Ableitungsfunktion ${fprime}$. Bestimmen Sie anhand des Graphen"
                    ),
                    fragen=[q for q, _ in questions],
                    antworten=[a_ for _, a_ in questions],
                    visual=_plot_visual(
                        title=f"Ableitungsfunktion {fprime}(t)",
                        x_axis=f"Zeit t in {k.zeit_pl}",
                        y_axis=f"{fprime}(t) in {k.rate} pro {k.zeit}",
                        trace_name=f"{fprime}(t)",
                        term=_du_term_plain(case, order=1),
                        beschreibung=f"Änderungsrate des {k.adj}en {k.groesse}es",
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
            k = _kontext_for(len(tasks))
            case = _plc_case_for_task(rng, len(tasks), "calc")
            t_peak = _max_u_time_by_sign_change(case)
            if t_peak is None:
                continue

            t_inc, t_dec = _max_min_of_du(case)
            _, y_peak = _max_of_u(case)
            threshold = _threshold_question(rng, case, k, y_peak)
            if threshold is None:
                continue

            t_eval_du = uniform_sig(rng, 1.0, case.t_end * 0.9)

            if case.has_market_exit:
                end_answer = _num_tol(case.t_end, tolerance=0.1)
            else:
                end_answer = _num_tol(case.offset, tolerance=0.01)

            items = [
                (f"den Zeitpunkt des stärksten {k.groesse}rückgangs.", _num_tol(t_dec, tolerance=0.1)),
                (
                    f"die momentane Änderungsrate des {k.adj}en {k.groesse}es nach {_fmt(t_eval_du, 2)} {k.zeit_pl}.",
                    _num_tol(case.du(t_eval_du), tolerance=0.1),
                ),
                (f"den Zeitpunkt des höchsten {k.adj}en {k.groesse}es.", _num_tol(t_peak, tolerance=0.1)),
                (f"die Höhe des höchsten {k.adj}en {k.groesse}es.", _num_tol(y_peak, tolerance=0.1)),
                (f"den Zeitpunkt des stärksten {k.groesse}anstiegs.", _num_tol(t_inc, tolerance=0.1)),
                (f"den {k.adj}en {k.groesse} bei der Markteinführung.", _num_tol(case.u(0.0), tolerance=0.1)),
                (
                    f"ob das Produkt vom Markt genommen wird oder ob sich der {k.adj}e {k.groesse} langfristig "
                    f"einem festen Wert annähert, und geben Sie entsprechend den Zeitpunkt des Marktaustritts "
                    f"bzw. den langfristig zu erwartenden {k.adj}en {k.groesse} an.",
                    end_answer,
                ),
                threshold,
            ]
            rng.shuffle(items)

            f = k.fname
            tasks.append(
                Task(
                    einleitung=(
                        f"Die Funktion ${f}$ beschreibt den {k.adj}en {k.groesse} eines Produkts in {k.rate} "
                        f"($t$ in {k.zeit_pl} seit der Markteinführung). Gegeben sind:"
                        f"{_align_equations([_u_latex(case, f), _du_latex(case, 1, f), _du_latex(case, 2, f)])}"
                        "Bestimmen Sie (auf 2 NKS gerundet)"
                    ),
                    fragen=[q for q, _ in items],
                    antworten=[a_ for _, a_ in items],
                )
            )

        return tasks


class ProduktlebenszyklusGesamtabsatzGraphischGenerator(TaskGenerator):
    generator_key = "analysis.produktlebenszyklus.gesamtabsatz_graphisch"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        while len(tasks) < count:
            k = _kontext_for(len(tasks))
            case = _plc_case_for_task(rng, len(tasks), "graph_u")
            t_peak, y_peak = _max_of_u(case)
            t_limit = _effective_u_plot_limit(case, t_peak, y_peak)
            if not case.has_market_exit:
                t_limit = min(t_limit, 30.0)
            if case.has_market_exit:
                y_values = _sample_curve_values(t_limit, lambda t: max(0.0, case.u(t)))
                t_domain = case.t_end
            else:
                y_values = _sample_curve_values(t_limit, case.u)
                t_domain = t_limit * 0.9

            y_min, y_max = _positive_y_axis_range(y_values, pad_ratio=0.04)
            # Feines Raster, damit sich Flächen über Kästchen abschätzen lassen.
            x_tick = next(step for step in (1.0, 2.0, 5.0) if t_limit / step <= 26)
            y_tick = _nice_step(max(0.6, y_max - y_min))
            cell = x_tick * y_tick

            q_max = int(math.floor(t_domain))
            if q_max < 4:
                continue

            def estimate_tol(value: float) -> float:
                return round(max(0.1 * value, 0.5 * cell), 2)

            # Schätzung Gesamtabsatz in einem Zeitraum
            p = 0 if rng.random() < 0.5 else rng.randint(1, max(1, q_max // 3))
            q = rng.randint(min(q_max, p + 2), min(q_max, p + max(3, q_max // 2)))
            if q - p < 2:
                continue
            total_pq = _integrate_case_u_exact(case, float(p), float(q))
            if total_pq < 2.0 * cell:
                continue

            # Schätzung Durchschnitt
            n = rng.randint(2, max(2, min(q_max, int(t_peak * 1.5) + 1)))
            avg_n = _integrate_case_u_exact(case, 0.0, float(n)) / n

            # Aussage beurteilen
            m = rng.randint(2, q_max)
            true_m = _integrate_case_u_exact(case, 0.0, float(m))
            factor = rng.choice([0.7, 0.75, 1.3, 1.35])
            claim = round(true_m * factor) if true_m * factor >= 10 else round(true_m * factor, 1)
            if claim <= 0:
                continue
            claim_true = true_m >= claim

            # Bedeutung eines Integrals
            r = rng.randint(0, max(0, q_max - 3))
            s = rng.randint(r + 2, q_max)
            f = k.fname
            integral_rs = f"$\\int_{{{r}}}^{{{s}}} {f}(t)\\,dt$"
            meaning_options = [
                f"{k.gesamt} {_zeitraum_text(k, r, s)}",
                f"{k.adj}er {k.groesse} nach {s} {k.zeit_pl}",
                f"Zunahme des {k.adj}en {k.groesse}es von $t={r}$ bis $t={s}$",
                f"durchschnittlicher {k.adj}er {k.groesse} von $t={r}$ bis $t={s}$",
            ]

            # Passenden Ausdruck wählen
            v = rng.randint(1, max(1, q_max - 2))
            w = rng.randint(v + 1, q_max)
            expr_options = [
                f"$\\int_{{{v}}}^{{{w}}} {f}(t)\\,dt$",
                f"${f}({w})-{f}({v})$",
                f"$\\int_{{0}}^{{{w}}} {f}(t)\\,dt$",
                f"${f}({w})$",
            ]

            questions = [
                (
                    f"einen Schätzwert für den {k.gesamt} {_zeitraum_text(k, p, q)}.",
                    _num_tol(total_pq, tolerance=estimate_tol(total_pq)),
                ),
                (
                    f"einen Schätzwert für den durchschnittlichen {k.adj}en {k.groesse} in den ersten {n} {k.zeit_pl}.",
                    _num_tol(avg_n, tolerance=round(max(0.1 * avg_n, 0.5 * y_tick), 2)),
                ),
                (
                    f"ob die Aussage „Der {k.gesamt} in den ersten {m} {k.zeit_pl} beträgt mindestens "
                    f"{_fmt(claim, 1)} {k.einheit}.“ wahr oder falsch ist.",
                    _mc(["wahr", "falsch"], "wahr" if claim_true else "falsch"),
                ),
                (
                    f"die Bedeutung von {integral_rs} im Sachzusammenhang.",
                    _mc(meaning_options, meaning_options[0]),
                ),
                (
                    f"den Ausdruck, der den {k.gesamt} vom Ende des {v}. bis zum Ende des {w}. {k.zeit_gen} angibt.",
                    _mc(expr_options, expr_options[0]),
                ),
            ]
            rng.shuffle(questions)

            tasks.append(
                Task(
                    einleitung=(
                        f"Das Diagramm zeigt den Graphen der Funktion ${f}$, die den {k.adj}en {k.groesse} "
                        f"eines Produkts in {k.rate} beschreibt ($t$ in {k.zeit_pl} seit der Markteinführung). "
                        "Bestimmen Sie anhand des Graphen"
                    ),
                    fragen=[q_ for q_, _ in questions],
                    antworten=[a_ for _, a_ in questions],
                    visual=_plot_visual(
                        title=f"{k.groesse}funktion {f}(t)",
                        x_axis=f"Zeit t in {k.zeit_pl}",
                        y_axis=f"{f}(t) in {k.rate}",
                        trace_name=f"{f}(t)",
                        term=_u_term_plain(case),
                        beschreibung=f"{k.adj}er {k.groesse}",
                        x_tick=x_tick,
                        y_tick=y_tick,
                        x_range=(0.0, t_limit),
                        y_range=(y_min, y_max),
                    ),
                )
            )

        return tasks


class ProduktlebenszyklusIntegraleGemischtGenerator(TaskGenerator):
    generator_key = "analysis.produktlebenszyklus.integrale_gemischt"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        while len(tasks) < count:
            k = _kontext_for(len(tasks))
            case = _plc_case_for_task(rng, len(tasks), "integrals")
            t_lifecycle = case.t_end
            if case.has_market_exit:
                lifecycle_text = " Der Produktlebenszyklus endet, wenn das Produkt vom Markt genommen wird."
            else:
                lifecycle_text = f" Der Produktlebenszyklus endet nach {_fmt(t_lifecycle, 2)} {k.zeit_pl}."

            a = float(rng.randint(2, max(3, int(t_lifecycle * 0.4))))
            b = float(rng.randint(max(int(a) + 1, int(t_lifecycle * 0.6)), max(int(a) + 1, int(t_lifecycle))))
            n = float(rng.randint(2, max(3, int(t_lifecycle * 0.8))))
            t_eval = float(rng.randint(1, max(1, int(t_lifecycle))))

            total = _integrate_case_u_exact(case, 0.0, t_lifecycle)
            interval_value = _integrate_case_u_exact(case, a, b)
            avg_value = _integrate_case_u_exact(case, 0.0, n) / n
            point_value = case.u(t_eval)

            target_raw = total * rng.uniform(0.3, 0.7)
            target = float(round(target_raw)) if target_raw >= 10 else round(target_raw, 1)
            t_target = _cumulative_time(case, target, t_lifecycle) if target > 0 else None
            if t_target is None:
                continue

            items = [
                (
                    f"den {k.gesamt}, der während des gesamten Produktlebenszyklus erzielt wird.",
                    _num_tol(total, tolerance=0.1),
                ),
                (
                    f"den {k.gesamt} vom Ende des {int(a)}. bis zum Ende des {int(b)}. {k.zeit_gen}.",
                    _num_tol(interval_value, tolerance=0.1),
                ),
                (
                    f"den durchschnittlichen {k.adj}en {k.groesse} in den ersten {int(n)} {k.zeit_pl}.",
                    _num_tol(avg_value, tolerance=0.1),
                ),
                (
                    f"den {k.adj}en {k.groesse} nach {int(t_eval)} {k.zeit_pl}.",
                    _num_tol(point_value, tolerance=0.1),
                ),
                (
                    f"den Zeitpunkt, zu dem der {k.gesamt} seit der Markteinführung {_fmt(target, 1)} {k.einheit} erreicht.",
                    _num_tol(t_target, tolerance=0.1),
                ),
            ]
            rng.shuffle(items)

            f = k.fname
            tasks.append(
                Task(
                    einleitung=(
                        "Die Funktion"
                        f"{_display_equation(_u_latex(case, f))}"
                        f"beschreibt den {k.adj}en {k.groesse} eines Produkts in {k.rate} ($t$ in {k.zeit_pl} "
                        f"seit der Markteinführung).{lifecycle_text} Bestimmen Sie (auf 2 NKS gerundet)"
                    ),
                    fragen=[q for q, _ in items],
                    antworten=[a_ for _, a_ in items],
                )
            )

        return tasks
