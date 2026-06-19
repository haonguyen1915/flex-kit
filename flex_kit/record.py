"""The set of files gen produced last run.

Lets gen clean up its own orphans (a renamed/removed source's stale output) while
leaving files it did not generate - hand-authored skills, another tool's output -
untouched in the host dirs. Without this record, gen would have to wipe whole dirs.
"""

from __future__ import annotations

import json
from pathlib import Path

RECORD_FILE = ".flexkit/.generated.json"


def read_record(out_root: Path) -> set[str]:
    path = out_root / RECORD_FILE
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    return set(data) if isinstance(data, list) else set()


def write_record(out_root: Path, paths: set[str]) -> None:
    path = out_root / RECORD_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(paths), indent=2) + "\n", encoding="utf-8")
