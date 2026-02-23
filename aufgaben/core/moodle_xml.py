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
    k3 = _to_float(params.get("k3"), 0.05)
    k2 = _to_float(params.get("k2"), -1.0)
    k1 = _to_float(params.get("k1"), 10.0)
    k0 = _to_float(params.get("k0"), 80.0)
    price = _to_float(params.get("price"), 20.0)
    capacity = max(1.0, _to_float(params.get("capacity"), 40.0))

    points = max(40, int(_to_float(spec.get("points"), 300)))
    x_values = [capacity * i / (points - 1) for i in range(points)]

    e_values = [price * x for x in x_values]
    k_values = [k3 * (x ** 3) + k2 * (x ** 2) + k1 * x + k0 for x in x_values]
    g_values = [e - k for e, k in zip(e_values, k_values)]

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
        if trace_type != "scatter":
            raise ValueError(f"Nicht unterstützter Trace-Typ: {trace_type}")
        fig.add_scatter(
            x=trace.get("x", []),
            y=trace.get("y", []),
            mode=trace.get("mode", "lines"),
            name=trace.get("name"),
            line=trace.get("line"),
            marker=trace.get("marker"),
        )
    return fig


PLOTLY_SPEC_BUILDERS: dict[str, Callable[[dict[str, Any]], Any]] = {
    "economic-curves": _build_figure_economic_curves,
    "plotly": _build_figure_plotly_traces,
}


def _build_plotly_figure_from_spec(spec: dict[str, Any]):
    spec_type = str(spec.get("type", "plotly")).lower()
    builder = PLOTLY_SPEC_BUILDERS.get(spec_type)
    if builder is None:
        raise ValueError(f"Nicht unterstützter visual.spec.type: {spec_type}")

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
    image_bytes = fig.to_image(
        format="png",
        width=int(_to_float(spec.get("width"), 900)),
        height=int(_to_float(spec.get("height"), 520)),
        scale=_to_float(spec.get("scale"), 1.0),
    )
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return encoded, "image/png"


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


def export_manifest_to_moodle_xml(
    manifest_path: str,
    exports_json_root: str,
    output_root: str,
    include_answers: bool = True,
) -> list[Path]:
    manifest_file = Path(manifest_path)
    exports_root = Path(exports_json_root)
    output_base = Path(output_root)

    entries = json.loads(manifest_file.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise ValueError("Manifest muss ein Array von relativen Pfaden sein.")

    created: list[Path] = []
    for entry in entries:
        if not isinstance(entry, str):
            continue
        rel_path = Path(entry)
        input_path = exports_root / rel_path
        output_path = output_base / rel_path.with_suffix(".xml")
        category = str(rel_path.with_suffix("")).replace("\\", "/")
        created.append(
            export_json_to_moodle_xml(
                input_json_path=str(input_path),
                output_xml_path=str(output_path),
                category=category,
                include_answers=include_answers,
            )
        )

    return created
