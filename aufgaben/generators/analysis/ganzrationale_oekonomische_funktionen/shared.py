import random


def _count_decimals(value: float, max_decimals: int = 4) -> int:
    text = f"{value:.{max_decimals}f}".rstrip("0").rstrip(".")
    if "." not in text:
        return 0
    return len(text.split(".", 1)[1])


def _format_number(value: float) -> str:
    if abs(value) < 1e-12:
        value = 0.0
    decimals = max(0, _count_decimals(value))
    text = f"{value:.{decimals}f}"
    return text.replace(".", ",")


def _num(value: float, tolerance: float = 0.0) -> str:
    del tolerance
    return f"{{1:NUMERICAL:={_format_number(value)}:0}}"


def _signed_term(value: float, variable: str) -> str:
    if abs(value) < 1e-12:
        return ""
    sign = "+" if value > 0 else "-"
    magnitude = abs(value)
    if abs(magnitude - 1.0) < 1e-12:
        return f"{sign}{variable}"
    return f"{sign}{_format_number(magnitude)}{variable}"


def _poly3_latex(label: str, a3: float, a2: float, a1: float, a0: float) -> str:
    return (
        f"\\( {label}(x)={_format_number(a3)}x^3"
        f"{_signed_term(a2, 'x^2')}"
        f"{_signed_term(a1, 'x')}"
        f"{_signed_term(a0, '')} \\)"
    )


def _erlös_latex(price: float) -> str:
    return f"\\( E(x)={_format_number(price)}x \\)"


def _preis_latex(price: float) -> str:
    return f"\\( p(x)={_format_number(price)} \\)"


def _build_intro(given_expressions: list[str]) -> str:
    parts = ["Gegeben:"]
    for expression in given_expressions:
        parts.append(f"</p> <p>{expression}")
    parts.append("</p> <p>Bestimmen Sie die Koeffizienten der angegebenen Funktionen:")
    return "".join(parts)


def _is_ertragsgesetzliche_k(k3: float, k2: float, k1: float, k0: float) -> bool:
    return (
        k3 > 0.0
        and k2 < 0.0
        and k1 > 0.0
        and k0 > 0.0
        and (k2 ** 2) <= 3.0 * k3 * k1 + 1e-12
    )


def _gain_coeff_terms_from_roots(k3: float, r1: float, r2: float, s: float) -> tuple[float, float, float]:
    g2 = k3 * (r1 + r2 - s)
    g1 = k3 * (s * (r1 + r2) - r1 * r2)
    k0 = k3 * s * r1 * r2
    return g2, g1, k0


def _sample_cost_coefficients(rng: random.Random) -> tuple[float, float, float, float]:
    while True:
        k3 = round(rng.uniform(0.01, 0.08), 2)
        k1 = round(rng.uniform(5.0, 55.0), 1)
        k0 = round(rng.uniform(20.0, 180.0), 0)

        # Ertragsgesetzlich: k2 < 0 und k2^2 <= 3*k3*k1
        k2_limit = (3.0 * k3 * k1) ** 0.5
        upper = min(3.2, k2_limit)
        if upper < 0.15:
            continue

        k2_abs = round(rng.uniform(0.15, upper), 2)
        k2 = -k2_abs

        if _is_ertragsgesetzliche_k(k3, k2, k1, k0):
            return k3, k2, k1, k0


def _answers_for_k(a3: float, a2: float, a1: float, a0: float) -> str:
    return (
        "\\( K(x)= \\)"
        f"{_num(a3)}"
        "\\( x^3 \\)+"
        f"{_num(a2)}"
        "\\( x^2 \\)+"
        f"{_num(a1)}"
        "\\( x \\)+"
        f"{_num(a0)}"
    )


def _answers_for_g(g3: float, g2: float, g1: float, g0: float) -> str:
    return (
        "\\( G(x)= \\)"
        f"{_num(g3)}"
        "\\( x^3 \\)+"
        f"{_num(g2)}"
        "\\( x^2 \\)+"
        f"{_num(g1)}"
        "\\( x \\)+"
        f"{_num(g0)}"
    )


def _answers_for_e(price: float) -> str:
    return "\\( E(x)= \\)" + f"{_num(price)}" + "\\( x \\)"


def _answers_for_p(price: float) -> str:
    return "\\( p(x)= \\)" + f"{_num(price)}"


def _num_tol(value: float, tolerance: float = 0.1, decimals: int = 4) -> str:
    rounded_value = round(value, decimals)
    value_text = _format_number(rounded_value)
    tolerance_text = _format_number(round(tolerance, 1))
    return f"{{1:NUMERICAL:={value_text}:{tolerance_text}}}"


def _g_value(x: float, k3: float, k2: float, k1: float, k0: float, price: float) -> float:
    return -k3 * (x ** 3) - k2 * (x ** 2) + (price - k1) * x - k0


def _bisection_root(func, left: float, right: float, iterations: int = 80) -> float:
    f_left = func(left)
    f_right = func(right)
    if f_left == 0:
        return left
    if f_right == 0:
        return right
    if f_left * f_right > 0:
        raise ValueError("Intervall enthält keine Nullstelle.")

    a, b = left, right
    for _ in range(iterations):
        middle = (a + b) / 2.0
        f_middle = func(middle)
        if f_middle == 0:
            return middle
        if f_left * f_middle < 0:
            b = middle
            f_right = f_middle
        else:
            a = middle
            f_left = f_middle
    return (a + b) / 2.0


def _sample_kennzahlen_parameters(
    rng: random.Random,
    for_graph: bool = False,
) -> tuple[float, float, float, float, float, float, float, float, int]:
    for _ in range(4000):
        # Aufbau über gewünschte Gewinn-Nullstellen r1 < r2 und negative dritte Nullstelle -s.
        r1 = rng.uniform(3.0, 35.0)
        r2 = rng.uniform(r1 + 4.0, min(95.0, r1 + 45.0))
        s = rng.uniform(2.0, min(40.0, r1 + r2 - 0.8))
        k3 = round(rng.uniform(0.01, 0.16), 2)

        k2_raw = -k3 * (r1 + r2 - s)
        if k2_raw >= -0.15:
            continue
        k2 = round(k2_raw, 2)
        if k2 >= 0:
            continue

        g2_root, g1_raw, k0_raw = _gain_coeff_terms_from_roots(k3, r1, r2, s)
        k0 = round(k0_raw, 0)
        if k0 <= 0:
            continue

        k1_min = (k2 ** 2) / (3.0 * k3) + 0.2
        k1 = round(rng.uniform(max(3.0, k1_min), max(3.0, k1_min) + 28.0), 1)
        price = round(k1 + g1_raw, 1)
        if price <= 0:
            continue
        if abs(round(price - k1, 1)) < 1e-9:
            continue

        # Konsistenzbedingungen ertragsgesetzlich.
        if not _is_ertragsgesetzliche_k(k3, k2, k1, k0):
            continue

        discr = 4.0 * (k2 ** 2) + 12.0 * k3 * (price - k1)
        if discr <= 0:
            continue

        sqrt_discr = discr ** 0.5
        x_crit_1 = (-2.0 * k2 - sqrt_discr) / (6.0 * k3)
        x_crit_2 = (-2.0 * k2 + sqrt_discr) / (6.0 * k3)
        if x_crit_2 <= 0:
            continue

        g = lambda x: _g_value(x, k3, k2, k1, k0, price)
        g0 = g(0.0)
        g_max = g(x_crit_2)
        if g0 >= 0 or g_max <= 0:
            continue

        # Muss-Kriterien (E1K3): p(0) < K(0) und p(0) < G_max.
        if price >= k0:
            continue
        if price >= g_max:
            continue

        if for_graph and g_max < max(8.0, 0.15 * k0):
            continue

        try:
            x_break_even_low = _bisection_root(g, 0.0, x_crit_2)
        except ValueError:
            continue

        right = max(x_crit_2 + 1.0, x_crit_2 * 1.5)
        while g(right) > 0 and right < 500.0:
            right *= 1.35
        if g(right) > 0:
            continue

        try:
            x_break_even_high = _bisection_root(g, x_crit_2, right)
        except ValueError:
            continue

        if x_break_even_low <= 0 or x_break_even_high <= x_break_even_low:
            continue

        capacity = int(max(8, round(x_break_even_high + rng.uniform(2.0, 12.0))))
        if capacity <= x_break_even_high:
            capacity = int(x_break_even_high) + 2

        x_wende = -k2 / (3.0 * k3)
        return (
            k3,
            k2,
            k1,
            k0,
            price,
            x_break_even_low,
            x_break_even_high,
            x_crit_2,
            capacity,
        )

    raise ValueError("Konnte keine gültigen Kennzahlen-Parameter erzeugen.")


def _kennzahlen_items(
    rng: random.Random,
    k3: float,
    k2: float,
    k1: float,
    k0: float,
    price: float,
    x_break_even_low: float,
    x_break_even_high: float,
    x_gain_max: float,
    capacity: int,
) -> list[tuple[str, str]]:
    g_max = _g_value(x_gain_max, k3, k2, k1, k0, price)
    x_wende = -k2 / (3.0 * k3)
    e_max = price * capacity

    items = [
        ("den Verkaufspreis.", _num_tol(price)),
        ("die Gewinnschwelle.", _num_tol(x_break_even_low)),
        ("die Fixkosten.", _num_tol(k0)),
        ("den maximalen Gewinn.", _num_tol(g_max)),
        ("die Gewinngrenze.", _num_tol(x_break_even_high)),
        (
            "die Menge beim Übergang vom degressiven zum progressiven Kostenwachstum.",
            _num_tol(x_wende),
        ),
        ("den maximalen Erlös.", _num_tol(e_max)),
        ("die gewinnmaximale Menge.", _num_tol(x_gain_max)),
    ]
    rng.shuffle(items)
    return items


def _erlös_quadratic_latex(a2: float, a1: float) -> str:
    return f"\\( E(x)={_format_number(a2)}x^2{_signed_term(a1, 'x')} \\)"


def _preis_linear_latex(a2: float, a1: float) -> str:
    return f"\\( p(x)={_format_number(a2)}x{_signed_term(a1, '')} \\)"


def _e2k3_kennzahlen_items(
    rng: random.Random,
    a2: float,
    a1: float,
    k3: float,
    k2: float,
    k1: float,
    k0: float,
    x_break_even_low: float,
    x_break_even_high: float,
    x_gain_max: float,
) -> list[tuple[str, str]]:
    g3 = -k3
    g2 = a2 - k2
    g1 = a1 - k1
    g0 = -k0

    g_max = g3 * (x_gain_max ** 3) + g2 * (x_gain_max ** 2) + g1 * x_gain_max + g0
    x_wende = -k2 / (3.0 * k3)
    x_erlös_max = -a1 / (2.0 * a2)
    x_sättigung = -a1 / a2
    e_max = a2 * (x_erlös_max ** 2) + a1 * x_erlös_max
    p_gain_max = a2 * x_gain_max + a1
    p_höchst = a1

    items = [
        ("den maximalen Gewinn.", _num_tol(g_max)),
        ("die Gewinnschwelle.", _num_tol(x_break_even_low)),
        ("die erlösmaximale Menge.", _num_tol(x_erlös_max)),
        ("die Sättigungsmenge.", _num_tol(x_sättigung)),
        ("den maximalen Erlös.", _num_tol(e_max)),
        ("den gewinnmaximalen Verkaufspreis.", _num_tol(p_gain_max)),
        ("die Gewinngrenze.", _num_tol(x_break_even_high)),
        (
            "die Menge beim Übergang vom degressiven zum progressiven Kostenwachstum.",
            _num_tol(x_wende),
        ),
        ("die gewinnmaximale Menge.", _num_tol(x_gain_max)),
        ("den Höchstpreis.", _num_tol(p_höchst)),
        ("die Fixkosten.", _num_tol(k0)),
    ]
    rng.shuffle(items)
    return items


def _g_local_extrema_values(
    a2: float,
    a1: float,
    k3: float,
    k2: float,
    k1: float,
    k0: float,
    x_max: float,
) -> tuple[float | None, float | None]:
    g2 = a2 - k2
    g1 = a1 - k1
    g3 = -k3
    g0 = -k0

    discr = 4.0 * (g2 ** 2) + 12.0 * k3 * g1
    if discr <= 0.0:
        return None, None

    sqrt_discr = discr ** 0.5
    x1 = (2.0 * g2 - sqrt_discr) / (6.0 * k3)
    x2 = (2.0 * g2 + sqrt_discr) / (6.0 * k3)

    y_min: float | None = None
    y_max: float | None = None
    for x in [x1, x2]:
        if x < 0.0 or x > x_max:
            continue
        y = g3 * (x ** 3) + g2 * (x ** 2) + g1 * x + g0
        second = -6.0 * k3 * x + 2.0 * g2
        if second > 0:
            y_min = y if y_min is None else min(y_min, y)
        elif second < 0:
            y_max = y if y_max is None else max(y_max, y)

    return y_min, y_max


def _e2k3_graph_y_range(
    a2: float,
    a1: float,
    k3: float,
    k2: float,
    k1: float,
    k0: float,
    x_max: float,
) -> tuple[float, float]:
    x_erlös_max = -a1 / (2.0 * a2)
    e_max = a2 * (x_erlös_max ** 2) + a1 * x_erlös_max
    g0 = -k0
    g_min_local, _ = _g_local_extrema_values(a2, a1, k3, k2, k1, k0, x_max=x_max)

    min_candidates = [g0]
    if g_min_local is not None:
        min_candidates.append(g_min_local)
    y_min = min(min_candidates)

    # Fokus auf ablesbare Kennzahlen: G(0), mögliches lokales Minimum, Erlösmaximum.
    y_min_plot = y_min * 1.15 if y_min < 0 else y_min * 0.9
    y_max_plot = max(e_max * 1.12, 1.0)

    if y_max_plot <= y_min_plot:
        y_max_plot = y_min_plot + 1.0

    return y_min_plot, y_max_plot


def _poly3_value(a3: float, a2: float, a1: float, a0: float, x: float) -> float:
    return a3 * (x ** 3) + a2 * (x ** 2) + a1 * x + a0


def _is_one_decimal(value: float, eps: float = 1e-9) -> bool:
    return abs(value * 10.0 - round(value * 10.0)) < eps


def _make_zuordnung_table(points: list[tuple[float, float]], label: str) -> str:
    header = "    <tr><td>Menge \\(x\\)</td>" + "".join(
        f"<td>\\( {_format_number(x)} \\)</td>" for x, _ in points
    ) + "</tr>"
    row = f"    <tr><td>\\({label}(x)\\)</td>" + "".join(
        f"<td>\\( {_format_number(y)} \\)</td>" for _, y in points
    ) + "</tr>"
    return f"<table class=\"TabelleEinleitung\">\n{header}\n{row}\n</table>"


def _sample_steckbrief_k_coefficients(rng: random.Random) -> tuple[float, float, float, float]:
    for _ in range(3000):
        k3 = rng.choice([0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.75, 1.0])
        k2_abs = rng.choice([0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0])
        k2 = -float(k2_abs)

        lower_k1 = (k2 ** 2) / (3.0 * k3) + 0.5
        k1 = round(rng.uniform(lower_k1 + 0.2, lower_k1 + 40.0), 2)
        k0 = float(rng.randint(20, 260))

        if not _is_ertragsgesetzliche_k(k3, k2, k1, k0):
            continue
        if any(abs(coeff) > 9999 or abs(coeff) < 0.001 for coeff in [k3, k2, k1, k0]):
            continue

        return round(k3, 2), round(k2, 2), round(k1, 2), round(k0, 2)

    raise ValueError("Konnte keine geeignete kubische Kostenfunktion für Steckbriefaufgaben erzeugen.")


def _sample_steckbrief_g_coefficients(
    rng: random.Random,
) -> tuple[float, float, float, float, float, float, float]:
    for _ in range(10000):
        r1 = float(rng.randint(2, 8))
        r2 = float(rng.randint(int(r1) + 2, int(r1) + 10))
        s = float(rng.randint(1, 10))
        a = float(rng.choice([1, 2, 3]))

        g3 = -a
        g2 = a * (r1 + r2 - s)
        g1 = a * (s * (r1 + r2) - r1 * r2)
        g0 = -a * s * r1 * r2

        if any(abs(coeff) > 9999 for coeff in [g3, g2, g1, g0]):
            continue
        if any(abs(coeff) < 0.001 for coeff in [g3, g2, g1, g0]):
            continue
        if g0 >= 0:
            continue
        if abs(_poly3_value(g3, g2, g1, g0, r1)) > 1e-3:
            continue
        if abs(_poly3_value(g3, g2, g1, g0, r2)) > 1e-3:
            continue

        discr = 4.0 * (g2 ** 2) - 12.0 * g3 * g1
        if discr <= 0:
            continue
        sqrt_discr = discr ** 0.5
        extremstellen = [
            (-2.0 * g2 - sqrt_discr) / (6.0 * g3),
            (-2.0 * g2 + sqrt_discr) / (6.0 * g3),
        ]
        x_gain_max: float | None = None
        for candidate in extremstellen:
            second = 6.0 * g3 * candidate + 2.0 * g2
            if second < 0:
                x_gain_max = candidate
                break
        if x_gain_max is None:
            continue
        if not (r1 < x_gain_max < r2):
            continue
        if abs(x_gain_max - round(x_gain_max)) > 1e-9:
            continue

        x_info_int = rng.randint(int(r1) + 1, int(r2) - 1)
        x_info = float(x_info_int)
        if _poly3_value(g3, g2, g1, g0, x_info) <= 0:
            continue

        return round(g3, 2), round(g2, 2), round(g1, 2), round(g0, 2), r1, r2, x_info

    raise ValueError("Konnte keine geeignete kubische Gewinnfunktion für Steckbriefaufgaben erzeugen.")


def _sample_points_for_poly(
    rng: random.Random,
    a3: float,
    a2: float,
    a1: float,
    a0: float,
    min_x: int = 1,
    max_x: int = 12,
) -> list[tuple[float, float]]:
    x_values = sorted(rng.sample(range(min_x, max_x + 1), 4))
    points: list[tuple[float, float]] = []
    for x in x_values:
        y = round(_poly3_value(a3, a2, a1, a0, float(x)), 2)
        points.append((float(x), y))
    return points


def _sample_e2k3_parameters(
    rng: random.Random,
    for_graph: bool = False,
) -> tuple[float, float, float, float, float, float, float, float, float]:
    for _ in range(9000):
        a1 = round(rng.uniform(12.0, 120.0), 1)
        a2 = round(-rng.uniform(0.12, 8.0), 2)

        x_sättigung = -a1 / a2
        if not (8.0 <= x_sättigung <= 140.0):
            continue

        x_erlös_max = x_sättigung / 2.0
        if x_erlös_max <= 1.5:
            continue

        lower_r1 = max(0.5, x_erlös_max * 0.2)
        upper_r1 = max(lower_r1 + 1.0, x_erlös_max * 0.85)
        r1 = rng.uniform(lower_r1, upper_r1)

        lower_r2 = max(r1 + 2.0, x_erlös_max * 1.05)
        upper_r2 = min(x_sättigung * 0.98, r1 + 70.0)
        if upper_r2 <= lower_r2:
            continue
        r2 = rng.uniform(lower_r2, upper_r2)

        s_upper = min(70.0, r1 + r2 - 0.2)
        if s_upper <= 0.5:
            continue
        s = rng.uniform(0.5, s_upper)

        k3 = round(rng.uniform(0.003, 0.35), 4)

        g2, g1, k0_root = _gain_coeff_terms_from_roots(k3, r1, r2, s)
        if abs(g2) < 0.001 or abs(g1) < 0.001:
            continue

        k2 = a2 - g2
        k1 = a1 - g1
        k0 = k0_root

        if not _is_ertragsgesetzliche_k(k3, k2, k1, k0):
            continue

        x_wende = -k2 / (3.0 * k3)
        if x_wende <= 0.0:
            continue

        discr = 4.0 * (g2 ** 2) + 12.0 * k3 * g1
        if discr <= 0.0:
            continue

        sqrt_discr = discr ** 0.5
        crit_1 = (2.0 * g2 - sqrt_discr) / (6.0 * k3)
        crit_2 = (2.0 * g2 + sqrt_discr) / (6.0 * k3)
        candidates = [
            candidate
            for candidate in [crit_1, crit_2]
            if candidate > 0 and (-6.0 * k3 * candidate + 2.0 * g2) < 0
        ]
        if not candidates:
            continue
        x_gain_max = min(candidates)

        if not (r1 < x_gain_max < r2):
            continue

        g3 = -k3
        g0 = -k0
        g_max = g3 * (x_gain_max ** 3) + g2 * (x_gain_max ** 2) + g1 * x_gain_max + g0
        if g_max <= 0.0:
            continue

        # Muss-Kriterien (E2K3): p(0)=a1 < K(0)=k0 und p(0) < G_max.
        if a1 >= k0:
            continue
        if a1 >= g_max:
            continue

        if for_graph:
            if g_max < max(8.0, 0.12 * k0):
                continue
            # Sättigungsmenge etwas größer als Gewinngrenze.
            if not (x_sättigung >= r2 * 1.02):
                continue

        x_sat = -a1 / a2
        x_e_max = x_sat / 2.0
        e_max = a2 * (x_e_max ** 2) + a1 * x_e_max
        if e_max <= 0.0:
            continue

        k_end = k3 * ((x_sat * 1.05) ** 3) + k2 * ((x_sat * 1.05) ** 2) + k1 * (x_sat * 1.05) + k0
        if k_end > e_max * 2.25:
            continue

        g_min_local, _ = _g_local_extrema_values(a2, a1, k3, k2, k1, k0, x_max=x_sat * 1.05)
        g_floor = min(-k0, g_min_local if g_min_local is not None else -k0)
        if abs(g_floor) > e_max * 1.10:
            continue

        p_gain_max = a2 * x_gain_max + a1
        if p_gain_max <= 0.0:
            continue

        return a2, a1, k3, k2, k1, k0, r1, r2, x_gain_max

    raise ValueError("Konnte keine gültigen E2K3-Parameter erzeugen.")


