import json
from pathlib import Path

from aufgaben.core.models import Task


def write_tasks(path: str, tasks: list[Task]) -> None:
    out_file = Path(path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    payload = [task.to_dict() for task in tasks]
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
