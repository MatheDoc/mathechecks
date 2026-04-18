import re

from aufgaben.core.models import Task


REQUIRED_KEYS = {"einleitung", "fragen", "antworten"}
PLACEHOLDER_PATTERN = re.compile(r"\{\d+:(NUMERICAL_OPT|NUMERICAL|MC):")


def validate_task(task: Task) -> None:
    payload = task.to_dict()
    allowed_keys = REQUIRED_KEYS | {"visual"}
    if not REQUIRED_KEYS.issubset(payload.keys()) or not set(payload.keys()).issubset(allowed_keys):
        raise ValueError("Ungültige Felder im Aufgabenobjekt.")
    if not isinstance(task.einleitung, str):
        raise ValueError("'einleitung' muss ein String sein.")
    if not isinstance(task.fragen, list) or not all(isinstance(item, str) for item in task.fragen):
        raise ValueError("'fragen' muss ein String-Array sein.")
    if not isinstance(task.antworten, list) or not all(isinstance(item, str) for item in task.antworten):
        raise ValueError("'antworten' muss ein String-Array sein.")
    if len(task.fragen) != len(task.antworten):
        raise ValueError("'fragen' und 'antworten' müssen gleich lang sein.")
    if not task.fragen:
        raise ValueError("Eine Aufgabe muss mindestens eine Frage enthalten.")
    if task.visual is not None:
        if not isinstance(task.visual, dict):
            raise ValueError("'visual' muss ein Objekt sein.")
        spec = task.visual.get("spec")
        if spec is not None and not isinstance(spec, dict):
            raise ValueError("'visual.spec' muss ein Objekt sein.")
    for answer in task.antworten:
        if answer == "---":
            continue
        if PLACEHOLDER_PATTERN.search(answer) is None:
            raise ValueError("Jede Antwort muss einen gültigen Placeholder enthalten.")


def validate_batch(tasks: list[Task], expected_count: int) -> None:
    if len(tasks) != expected_count:
        raise ValueError(f"Erwartet: {expected_count} Aufgaben, erhalten: {len(tasks)}")
    for task in tasks:
        validate_task(task)
