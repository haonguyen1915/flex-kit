"""flex-kit - single-source AI-host kit for Claude Code + Codex."""

from __future__ import annotations

import re
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def _version() -> str:
    """Single source of truth = pyproject.toml. Read it directly when running from the
    source tree (an editable/dev checkout) so the version is always current; fall back to
    the installed package metadata for a built wheel (which ships no pyproject.toml)."""
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    if pyproject.is_file():
        m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', pyproject.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    try:
        return version("flex-kit")
    except PackageNotFoundError:  # raw checkout that was never installed
        return "0.0.0+source"


__version__ = _version()
