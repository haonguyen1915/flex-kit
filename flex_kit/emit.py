"""The unit of host output: one file to write (content) or copy (copy_from)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class OutFile:
    path: str  # relative to the output root, e.g. ".claude/skills/foo/SKILL.md"
    content: str | None = None
    copy_from: Path | None = None
