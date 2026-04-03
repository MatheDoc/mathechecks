import json
import base64
from pathlib import Path
from typing import Any, Callable
import xml.etree.ElementTree as ET


def _to_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _ensure_plotly():
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise RuntimeError(
            "Für visual.spec Rendering wird 'plotly' benötigt. Bitte installieren."
        ) from exc
    return go


def _build_figure_economic_curves(spec: dict[str, Any]):
    go = _ensure_plotly()
    fig = go.Figure()

    params = spec.get("params", {}) if isinstance(spec.get("params"), dict) else {}
    has_monopoly_revenue = "a2" in params and "a1" in params
    a2 = _to_float(params.get("a2"), -0.15)
    a1 = _to_float(params.get("a1"), 2.0)
    k3 = _to_float(params.get("k3"), 0.05)
    k2 = _to_float(params.get("k2"), -1.0)
    k1 = _to_float(params.get("k1"), 10.0)
    k0 = _to_float(params.get("k0"), 80.0)
    price = _to_float(params.get("price"), 20.0)
    capacity = max(1.0, _to_float(params.get("capacity"), 40.0))
    x_max = max(1.0, _to_float(params.get("xMax"), capacity))
    show_capacity_line = bool(params.get("showCapacityLine", True))

    points = max(40, int(_to_float(spec.get("points"), 300)))
    x_values = [x_max * i / (points - 1) for i in range(points)]

    p_values = [(a2 * x + a1) if has_monopoly_revenue else price for x in x_values]
    e_values = [((a2 * (x ** 2) + a1 * x) if has_monopoly_revenue else (price * x)) for x in x_values]
    k_values = [k3 * (x ** 3) + k2 * (x ** 2) + k1 * x + k0 for x in x_values]
    g_values = [e - k for e, k in zip(e_values, k_values)]

    if has_monopoly_revenue:
        fig.add_scatter(
            x=x_values,
            y=p_values,
            mode="lines",
            name="p(x)",
            line={"color": "#ff7f0e"},
        )

    fig.add_scatter(
        x=x_values,
        y=e_values,
        mode="lines",
        name="E(x)",
        line={"color": "#2ca02c"},
    )
    fig.add_scatter(
        x=x_values,
        y=k_values,
        mode="lines",
        name="K(x)",
        line={"color": "#d62728"},
    )
    fig.add_scatter(
        x=x_values,
        y=g_values,
        mode="lines",
        name="G(x)",
        line={"color": "#1f77b4"},
    )
    if show_capacity_line:
        fig.add_vline(x=capacity, line_dash="dot")
    return fig


def _build_figure_plotly_traces(spec: dict[str, Any]):
    go = _ensure_plotly()
    fig = go.Figure()

    traces = spec.get("traces", [])
    if not isinstance(traces, list) or not traces:
        raise ValueError("visual.spec.traces muss ein nicht-leeres Array sein.")

    for trace in traces:
        if not isinstance(trace, dict):
            continue
        trace_type = str(trace.get("kind", "scatter")).lower()
        trace_kwargs = {
            "x": trace.get("x", []),
            "y": trace.get("y", []),
            "name": trace.get("name"),
            "marker": trace.get("marker"),
        }
        if trace_type == "scatter":
            trace_kwargs["mode"] = trace.get("mode", "lines")
            trace_kwargs["line"] = trace.get("line")
        elif trace_type == "bar":
            optional_bar_keys = ["width", "offset", "base"]
            for key in optional_bar_keys:
                if key in trace:
                    trace_kwargs[key] = trace.get(key)
        else:
            raise ValueError(f"Nicht unterstützter Trace-Typ: {trace_type}")

        optional_keys = [
            "fill",
            "fillcolor",
            "text",
            "textposition",
            "textfont",
            "opacity",
            "showlegend",
            "hoverinfo",
        ]
        for key in optional_keys:
            if key in trace:
                trace_kwargs[key] = trace.get(key)

        if trace_type == "scatter":
            fig.add_scatter(
                **trace_kwargs,
            )
        else:
            fig.add_bar(
                **trace_kwargs,
            )
    return fig


def _build_figure_cost_curves(spec: dict[str, Any]):
    go = _ensure_plotly()
    fig = go.Figure()

    params = spec.get("params", {}) if isinstance(spec.get("params"), dict) else {}
    k3 = _to_float(params.get("k3"), 0.05)
    k2 = _to_float(params.get("k2"), -1.0)
    k1 = _to_float(params.get("k1"), 10.0)
    k0 = _to_float(params.get("k0"), 80.0)
    max_x = _to_float(params.get("maxX"), 30.0)
    start_x = 0.5

    points = max(40, int(_to_float(spec.get("points"), 300)))
    x_values = [start_x + (max_x - start_x) * i / (points - 1) for i in range(points)]

    gk_values = [3.0 * k3 * (x ** 2) + 2.0 * k2 * x + k1 for x in x_values]
    k_values = [k3 * (x ** 2) + k2 * x + k1 + k0 / x for x in x_values]
    kv_values = [k3 * (x ** 2) + k2 * x + k1 for x in x_values]

    fig.add_scatter(
        x=x_values, y=gk_values, mode="lines", name="GK(x)", line={"color": "#1f77b4"},
    )
    fig.add_scatter(
        x=x_values, y=k_values, mode="lines", name="k(x)", line={"color": "#d62728"},
    )
    fig.add_scatter(
        x=x_values, y=kv_values, mode="lines", name="kv(x)", line={"color": "#2ca02c"},
    )
    return fig


def _build_figure_market_curves(spec: dict[str, Any]):
    go = _ensure_plotly()
    fig = go.Figure()

    params = spec.get("params", {}) if isinstance(spec.get("params"), dict) else {}
    supply_slope = max(0.01, _to_float(params.get("supplySlope"), 1.2))
    demand_slope = max(0.01, _to_float(params.get("demandSlope"), 1.8))
    min_price = _to_float(params.get("minPrice"), 5.0)
    max_price = _to_float(params.get("maxPrice"), 20.0)
    max_x = max(5.0, _to_float(params.get("maxX"), 20.0))

    points = max(40, int(_to_float(spec.get("points"), 220)))
    x_values = [max_x * i / (points - 1) for i in range(points)]

    supply_values = [supply_slope * x + min_price for x in x_values]
    demand_values = [-demand_slope * x + max_price for x in x_values]

    eq_x = (max_price - min_price) / (supply_slope + demand_slope)
    eq_y = supply_slope * eq_x + min_price

    fig.add_scatter(
        x=x_values,
        y=supply_values,
        mode="lines",
        name="Angebot p_A(x)",
        line={"color": "#d62728"},
    )
    fig.add_scatter(
        x=x_values,
        y=demand_values,
        mode="lines",
        name="Nachfrage p_N(x)",
        line={"color": "#1f77b4"},
    )
    return fig


def _eval_fn_params(p: dict[str, Any], x: float) -> float:
    import math as _math
    kind = p.get("type", "linear")
    if kind == "linear":
        return _to_float(p.get("a"), 1.0) * x + _to_float(p.get("b"), 0.0)
    if kind == "quadratic":
        a = _to_float(p.get("a"), 0.0)
        b = _to_float(p.get("b"), 0.0)
        c = _to_float(p.get("c"), 0.0)
        return a * x * x + b * x + c
    if kind == "exp":
        A = _to_float(p.get("A"), 1.0)
        rate = _to_float(p.get("rate"), 0.1)
        c = _to_float(p.get("c"), 0.0)
        return A * _math.exp(-rate * x) + c
    return 0.0


def _build_figure_market_equilibrium(spec: dict[str, Any]):
    go = _ensure_plotly()
    fig = go.Figure()

    params = spec.get("params", {}) if isinstance(spec.get("params"), dict) else {}
    supply_p = params.get("supply", {})
    demand_p = params.get("demand", {})
    eq_x = _to_float(params.get("eqX"), 10.0)
    eq_p = _to_float(params.get("eqP"), 10.0)
    max_x = max(1.0, _to_float(params.get("maxX"), 30.0))
    sat_x = max(eq_x * 1.02, _to_float(params.get("satX"), max_x))

    points = max(40, int(_to_float(spec.get("points"), 260)))
    supply_x = [max_x * i / (points - 1) for i in range(points)]
    supply_values = [_eval_fn_params(supply_p, x) for x in supply_x]

    demand_points = max(40, round(points * sat_x / max_x))
    demand_x = [sat_x * i / (demand_points - 1) for i in range(demand_points)]
    demand_values = [_eval_fn_params(demand_p, x) for x in demand_x]

    fig.add_scatter(x=supply_x, y=supply_values, mode="lines", name="Angebot p_A(x)", line={"color": "#d62728"})
    fig.add_scatter(x=demand_x, y=demand_values, mode="lines", name="Nachfrage p_N(x)", line={"color": "#1f77b4"})
    return fig


def _build_figure_market_abschoepfung(spec: dict[str, Any]):
    go = _ensure_plotly()
    fig = go.Figure()

    params = spec.get("params", {}) if isinstance(spec.get("params"), dict) else {}
    supply_p = params.get("supply", {})
    demand_p = params.get("demand", {})
    eq_x = _to_float(params.get("eqX"), 10.0)
    eq_p = _to_float(params.get("eqP"), 10.0)
    x2 = _to_float(params.get("x2"), 5.0)
    p2 = _to_float(params.get("p2"), 15.0)
    max_x = max(1.0, _to_float(params.get("maxX"), 30.0))

    points = max(40, int(_to_float(spec.get("points"), 280)))
    x_values = [max_x * i / (points - 1) for i in range(points)]
    supply_values = [_eval_fn_params(supply_p, x) for x in x_values]
    demand_values = [_eval_fn_params(demand_p, x) for x in x_values]

    kr2_curve_x = [x2 * i / 80 for i in range(81)]
    kr2_curve_y = [_eval_fn_params(demand_p, x) for x in kr2_curve_x]
    kr2_x = [0.0, x2] + list(reversed(kr2_curve_x))
    kr2_y = [p2, p2] + list(reversed(kr2_curve_y))

    kr1_curve_x = [x2 + (eq_x - x2) * i / 80 for i in range(81)]
    kr1_curve_y = [_eval_fn_params(demand_p, x) for x in kr1_curve_x]
    kr1_x = [x2, eq_x] + list(reversed(kr1_curve_x))
    kr1_y = [eq_p, eq_p] + list(reversed(kr1_curve_y))

    fig.add_scatter(x=kr2_x, y=kr2_y, mode="lines", name="KR2", line={"width": 0}, fill="toself", fillcolor="rgba(59, 130, 246, 0.25)")
    fig.add_scatter(x=kr1_x, y=kr1_y, mode="lines", name="KR1", line={"width": 0}, fill="toself", fillcolor="rgba(16, 185, 129, 0.25)")
    fig.add_scatter(x=x_values, y=supply_values, mode="lines", name="Angebot p_A(x)", line={"color": "#d62728"})
    fig.add_scatter(x=x_values, y=demand_values, mode="lines", name="Nachfrage p_N(x)", line={"color": "#1f77b4"})
    return fig


PLOTLY_SPEC_BUILDERS: dict[str, Callable[[dict[str, Any]], Any]] = {
    "economic-curves": _build_figure_economic_curves,
    "cost-curves": _build_figure_cost_curves,
    "market-curves": _build_figure_market_curves,
    "market-equilibrium": _build_figure_market_equilibrium,
    "market-abschoepfung": _build_figure_market_abschoepfung,
    "plotly": _build_figure_plotly_traces,
}


def _build_plotly_figure_from_spec(spec: dict[str, Any]):
    spec_type = str(spec.get("type", "plotly")).lower()
    builder = PLOTLY_SPEC_BUILDERS.get(spec_type)
    if builder is None:
        # Unbekannter Spec-Typ (z.B. ab-tree) – wird nur clientseitig gerendert.
        return None

    fig = builder(spec)

    layout = spec.get("layout", {})
    if isinstance(layout, dict):
        fig.update_layout(**layout)

    fig.update_layout(
        template="plotly_white",
        legend={
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.2,
            "yanchor": "top",
        },
        margin={"l": 40, "r": 20, "t": 30, "b": 90},
    )
    return fig


def _render_visual_spec_to_base64(visual: dict[str, Any]) -> tuple[str, str] | None:
    spec = visual.get("spec")
    if not isinstance(spec, dict):
        return None

    fig = _build_plotly_figure_from_spec(spec)
    if fig is None:
        return None
    width = int(_to_float(spec.get("width"), 900))
    height = int(_to_float(spec.get("height"), 520))
    scale = _to_float(spec.get("scale"), 1.0)

    # Kaleido 1.x can intermittently deadlock in oneshot_async_run on
    # Python 3.14+.  Retry up to 3 times with a per-attempt timeout
    # implemented via a daemon thread so we don't hang forever.
    import threading

    for attempt in range(3):
        result: list[bytes | Exception] = []

        def _render():
            try:
                result.append(fig.to_image(
                    format="png", width=width, height=height, scale=scale,
                ))
            except Exception as exc:  # noqa: BLE001
                result.append(exc)

        t = threading.Thread(target=_render, daemon=True)
        t.start()
        t.join(timeout=30)

        if t.is_alive():
            # Thread still running → Kaleido deadlock; retry
            import sys
            print(
                f"[WARN] Kaleido-Timeout (Versuch {attempt + 1}/3) – neuer Versuch …",
                file=sys.stderr,
            )
            continue

        if result and isinstance(result[0], bytes):
            encoded = base64.b64encode(result[0]).decode("ascii")
            return encoded, "image/png"

        if result and isinstance(result[0], Exception):
            raise result[0]

    raise RuntimeError("Kaleido-Rendering 3× fehlgeschlagen (Timeout/Deadlock).")


def _resolve_visual_image(visual: dict[str, Any]) -> tuple[str, str] | None:
    image_base64 = visual.get("imageBase64")
    image_mime = str(visual.get("mimeType", "image/png"))
    if isinstance(image_base64, str) and image_base64.strip():
        return image_base64, image_mime

    return _render_visual_spec_to_base64(visual)


def _task_to_html(task: dict[str, Any], include_answers: bool = True) -> str:
    html = task.get("einleitung", "")

    visual = task.get("visual")
    if isinstance(visual, dict):
        resolved = _resolve_visual_image(visual)
        if resolved is not None:
            image_base64, image_mime = resolved
            html += f"</p><p><img src='data:{image_mime};base64,{image_base64}' />"

    fragen = task.get("fragen", [])
    antworten = task.get("antworten", [])

    if not isinstance(fragen, list):
        fragen = []
    if not isinstance(antworten, list):
        antworten = []

    for index in range(max(len(fragen), len(antworten))):
        if index < len(fragen):
            html += f"<p>{fragen[index]}</p>"
        if include_answers and index < len(antworten):
            html += f"<p>{antworten[index]}</p>"
    return html


def export_json_to_moodle_xml(
    input_json_path: str,
    output_xml_path: str,
    category: str | None = None,
    include_answers: bool = True,
) -> Path:
    source_path = Path(input_json_path)
    data = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("JSON muss ein Array von Aufgaben enthalten.")

    target_path = Path(output_xml_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    quiz = ET.Element("quiz")

    question_cat = ET.SubElement(quiz, "question", {"type": "category"})
    category_el = ET.SubElement(question_cat, "category")
    category_text = ET.SubElement(category_el, "text")

    category_value = category or source_path.stem.replace("_", "/")
    category_text.text = category_value

    info = ET.SubElement(question_cat, "info", {"format": "html"})
    ET.SubElement(info, "text").text = ""
    ET.SubElement(question_cat, "idnumber").text = ""

    placeholders: list[tuple[str, str]] = []
    for index, task in enumerate(data, start=1):
        if not isinstance(task, dict):
            continue
        question = ET.SubElement(quiz, "question", {"type": "cloze"})
        name = ET.SubElement(question, "name")
        ET.SubElement(name, "text").text = f"{index:02d}"
        questiontext = ET.SubElement(question, "questiontext", {"format": "html"})

        placeholder = f"__CDATA_PLACEHOLDER_{index}__"
        ET.SubElement(questiontext, "text").text = placeholder
        placeholders.append((placeholder, _task_to_html(task, include_answers=include_answers)))

    xml_text = ET.tostring(quiz, encoding="utf-8").decode("utf-8")
    for placeholder, html in placeholders:
        xml_text = xml_text.replace(placeholder, f"<![CDATA[{html}]]>")

    target_path.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + xml_text,
        encoding="utf-8",
    )
    return target_path



