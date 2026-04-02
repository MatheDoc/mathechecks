import json
import re
from pathlib import Path

from aufgaben.core.models import Task


_CLOZE_PLACEHOLDER_PATTERN = re.compile(r"\{\d+:[^{}]*\}")
_DECIMAL_COMMA_PATTERN = re.compile(r"(?<=\d),(?=\d)")
_LATEX_DISPLAY_PATTERN = re.compile(r"\$\$(.*?)\$\$", re.DOTALL)
_LATEX_INLINE_PATTERN = re.compile(r"(?<!\$)\$((?!\$).*?)\$(?!\$)", re.DOTALL)


def _normalize_latex_segment(pattern: re.Pattern[str], text: str) -> str:
    def _replace(match: re.Match[str]) -> str:
        segment = match.group(0)
        inner = match.group(1)
        normalized_inner = _DECIMAL_COMMA_PATTERN.sub("{,}", inner)
        return segment.replace(inner, normalized_inner, 1)

    return pattern.sub(_replace, text)


def _normalize_decimal_commas(text: str) -> str:
    """Setzt Dezimal-Kommas nur in LaTeX-Bereichen auf {,}, außer in CLOZE-Placeholdern."""
    placeholders: list[str] = []

    def _mask(match: re.Match[str]) -> str:
        placeholders.append(match.group(0))
        return f"__CLOZE_PLACEHOLDER_{len(placeholders) - 1}__"

    masked = _CLOZE_PLACEHOLDER_PATTERN.sub(_mask, text)
    normalized = _normalize_latex_segment(_LATEX_DISPLAY_PATTERN, masked)
    normalized = _normalize_latex_segment(_LATEX_INLINE_PATTERN, normalized)

    for index, original in enumerate(placeholders):
        normalized = normalized.replace(f"__CLOZE_PLACEHOLDER_{index}__", original)

    return normalized


def _normalize_export_payload(value: object) -> object:
    if isinstance(value, str):
        return _normalize_decimal_commas(value)
    if isinstance(value, list):
        return [_normalize_export_payload(item) for item in value]
    if isinstance(value, dict):
        return {key: _normalize_export_payload(item) for key, item in value.items()}
    return value


def write_tasks(path: str, tasks: list[Task]) -> None:
    out_file = Path(path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    payload = _normalize_export_payload([task.to_dict() for task in tasks])
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
