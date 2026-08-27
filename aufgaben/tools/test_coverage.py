"""Prüft die Abdeckung der Test-Aktivität: je Check aus _data/checks.json muss unter
aufgaben/test/<gebiet>/<lernbereich>/<check_id>.json eine gültige Quelldatei liegen
(10 Fragen, je genau 4 Antworten, erste Antwort = richtig, fehler optional mit max. 3 Einträgen).

Aufruf: python -m aufgaben.tools.test_coverage
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKS_PATH = REPO_ROOT / "_data" / "checks.json"
TEST_ROOT = REPO_ROOT / "aufgaben" / "test"
EXPECTED_QUESTION_COUNT = 10
EXPECTED_ANSWER_COUNT = 4
MAX_ANSWER_LENGTH = 90


def validate_source(path: Path) -> list[str]:
    problems: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"nicht lesbar/parsebar: {error}"]

    fragen = data.get("fragen") if isinstance(data, dict) else None
    if not isinstance(fragen, list):
        return ["'fragen' fehlt oder ist kein Array"]

    if len(fragen) != EXPECTED_QUESTION_COUNT:
        problems.append(f"{len(fragen)} statt {EXPECTED_QUESTION_COUNT} Fragen")

    for index, frage in enumerate(fragen, start=1):
        if not isinstance(frage, dict):
            problems.append(f"Frage {index}: kein Objekt")
            continue
        text = frage.get("frage")
        if not isinstance(text, str) or not text.strip():
            problems.append(f"Frage {index}: 'frage' fehlt oder leer")
        antworten = frage.get("antworten")
        if not isinstance(antworten, list) or len(antworten) != EXPECTED_ANSWER_COUNT:
            problems.append(f"Frage {index}: 'antworten' hat nicht genau {EXPECTED_ANSWER_COUNT} Einträge")
        elif any(not isinstance(a, str) or not a.strip() for a in antworten):
            problems.append(f"Frage {index}: leere Antwort")
        else:
            for a in antworten:
                if len(a) > MAX_ANSWER_LENGTH:
                    problems.append(f"Frage {index}: Antwort mit {len(a)} Zeichen (max. {MAX_ANSWER_LENGTH})")
        fehler = frage.get("fehler")
        if fehler is not None:
            if not isinstance(fehler, list) or len(fehler) > EXPECTED_ANSWER_COUNT - 1:
                problems.append(f"Frage {index}: 'fehler' ungültig (max. {EXPECTED_ANSWER_COUNT - 1} Einträge)")

    return problems


def main() -> int:
    checks = json.loads(CHECKS_PATH.read_text(encoding="utf-8"))
    missing: list[str] = []
    invalid: dict[str, list[str]] = {}
    ok_count = 0

    for check in checks:
        check_id = str(check.get("check_id", "")).strip()
        gebiet = str(check.get("Gebiet", "")).strip()
        lernbereich = str(check.get("Lernbereich", "")).strip()
        if not check_id or not gebiet or not lernbereich:
            invalid[check_id or "<ohne check_id>"] = ["unvollständige Metadaten in checks.json"]
            continue

        source = TEST_ROOT / gebiet / lernbereich / f"{check_id}.json"
        if not source.is_file():
            missing.append(check_id)
            continue

        problems = validate_source(source)
        if problems:
            invalid[check_id] = problems
        else:
            ok_count += 1

    known_ids = {str(check.get("check_id", "")).strip() for check in checks}
    orphans = sorted(
        str(path.relative_to(TEST_ROOT))
        for path in TEST_ROOT.rglob("*.json")
        if path.stem not in known_ids
    )

    print(f"Checks gesamt: {len(checks)}")
    print(f"gültige Test-Quellen: {ok_count}")

    if missing:
        print(f"\nFEHLEND ({len(missing)}):")
        for check_id in missing:
            print(f"  - {check_id}")

    if invalid:
        print(f"\nUNGÜLTIG ({len(invalid)}):")
        for check_id, problems in invalid.items():
            for problem in problems:
                print(f"  - {check_id}: {problem}")

    if orphans:
        print(f"\nVERWAIST (kein zugehöriger Check, {len(orphans)}):")
        for orphan in orphans:
            print(f"  - {orphan}")

    if missing or invalid:
        return 1
    print("\nAbdeckung vollständig.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
