import json
from pathlib import Path

from aufgaben.core.models import Task


def write_tasks(path: str, tasks: list[Task]) -> None:
    out_file = Path(path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    payload = [task.to_dict() for task in tasks]
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_manifest(output_dir: str) -> None:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)

    entries = sorted(
        str(path.relative_to(root)).replace("\\", "/")
        for path in root.rglob("*.json")
        if path.name != "manifest.json" and not path.name.endswith("-test.json")
    )

    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
