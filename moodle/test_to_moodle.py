"""Konvertiert die Test-JSONs in Moodle-XML (Fragetyp multichoice, single, shuffle).

Quelle:  test/<gebiet>/<lernbereich>/<check_id>.json
Ziel:    moodle/<gebiet>/<lernbereich>/<check_id>.xml (eine Datei pro Check)
Vorlage: moodle/gebiet__lernbereich__01.xml

Aufruf: python moodle/test_to_moodle.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = REPO_ROOT / "test"
OUT_ROOT = REPO_ROOT / "moodle"


def cdata(text: str) -> str:
    return "<![CDATA[" + str(text).replace("]]>", "]]]]><![CDATA[>") + "]]>"


def xml_text(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render_category(path: str) -> str:
    return f"""  <question type="category">
    <category>
      <text>{xml_text(path)}</text>
    </category>
  </question>
"""


def render_answer(text: str, correct: bool, feedback: str = "") -> str:
    fraction = "100" if correct else "0"
    feedback_markup = cdata(f"<p>{feedback}</p>") if feedback else ""
    return f"""    <answer fraction="{fraction}" format="html">
      <text>{cdata(f"<p>{text}</p>")}</text>
      <feedback format="html">
        <text>{feedback_markup}</text>
      </feedback>
    </answer>
"""


def render_question(name: str, frage: str, antworten: list[str], fehler: list[str]) -> str:
    answers = [render_answer(antworten[0], correct=True)]
    for index, antwort in enumerate(antworten[1:]):
        feedback = fehler[index] if index < len(fehler) else ""
        answers.append(render_answer(antwort, correct=False, feedback=feedback))

    return f"""  <question type="multichoice">
    <name>
      <text>{xml_text(name)}</text>
    </name>
    <questiontext format="html">
      <text>{cdata(f"<p>{frage}</p>")}</text>
    </questiontext>
    <generalfeedback format="html">
      <text></text>
    </generalfeedback>
    <defaultgrade>1.0000000</defaultgrade>
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
    <idnumber></idnumber>
    <single>true</single>
    <shuffleanswers>true</shuffleanswers>
    <answernumbering>abc</answernumbering>
    <showstandardinstruction>0</showstandardinstruction>
    <correctfeedback format="html">
      <text>{cdata("<p>Die Antwort ist richtig.</p>")}</text>
    </correctfeedback>
    <partiallycorrectfeedback format="html">
      <text>{cdata("<p>Die Antwort ist teilweise richtig.</p>")}</text>
    </partiallycorrectfeedback>
    <incorrectfeedback format="html">
      <text>{cdata("<p>Die Antwort ist falsch.</p>")}</text>
    </incorrectfeedback>
    <shownumcorrect/>
{"".join(answers)}  </question>
"""


def convert_check(source: Path, gebiet: str, lernbereich: str) -> tuple[Path, int]:
    check_id = source.stem
    data = json.loads(source.read_text(encoding="utf-8"))
    fragen = data.get("fragen")
    if not isinstance(fragen, list) or not fragen:
        raise ValueError(f"{source}: 'fragen' fehlt oder ist leer")

    parts = ['<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n']
    parts.append(render_category(f"$course$/{gebiet}"))
    parts.append(render_category(f"$course$/{gebiet}/{lernbereich}"))
    parts.append(render_category(f"$course$/{gebiet}/{lernbereich}/{check_id}"))

    for index, frage in enumerate(fragen, start=1):
        text = str(frage.get("frage", "")).strip()
        antworten = frage.get("antworten")
        if not text or not isinstance(antworten, list) or len(antworten) != 4:
            raise ValueError(f"{source}: Frage {index} ist unvollständig")
        fehler = frage.get("fehler") if isinstance(frage.get("fehler"), list) else []
        parts.append(render_question(f"{check_id}-{index:02d}", text, antworten, fehler))

    parts.append("</quiz>\n")

    target = OUT_ROOT / gebiet / lernbereich / f"{check_id}.xml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(parts), encoding="utf-8")
    return target, len(fragen)


def main() -> int:
    written = 0
    question_count = 0
    errors: list[str] = []

    for source in sorted(TEST_ROOT.rglob("*.json")):
        relative = source.relative_to(TEST_ROOT)
        if len(relative.parts) != 3:
            continue
        gebiet, lernbereich = relative.parts[0], relative.parts[1]
        try:
            _, fragen_count = convert_check(source, gebiet, lernbereich)
            written += 1
            question_count += fragen_count
        except (ValueError, OSError, json.JSONDecodeError) as error:
            errors.append(str(error))

    print(f"Moodle-XMLs geschrieben: {written} ({question_count} Fragen)")
    if errors:
        print(f"\nFEHLER ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
