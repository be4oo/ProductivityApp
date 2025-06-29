"""Lightweight synchronization placeholder."""

import json
from pathlib import Path

DATA_FILE = Path.home() / ".blitzit_sync.json"

def export_data(tasks):
    DATA_FILE.write_text(json.dumps(tasks, indent=2))


def import_data():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []
