"""Aufgaben generieren – einfach ausführen.

Nutzung:
    python aufgaben/run.py              # alle Jobs
    python aufgaben/run.py e2k3         # nur Jobs mit "e2k3"
    python aufgaben/run.py binomial     # nur Jobs mit "binomial"
"""

import sys
from pathlib import Path

# Projektroot ermitteln, damit Importe funktionieren
_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))

from aufgaben.cli import run_batch  # noqa: E402

CONFIG = str(_root / "aufgaben" / "project_config.json")

if __name__ == "__main__":
    filter_text = sys.argv[1] if len(sys.argv) > 1 else None
    run_batch(CONFIG, filter_text=filter_text)
