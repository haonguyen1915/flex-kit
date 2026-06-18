"""Codex host adapter.

Codex frontmatter is plain text: the description is stripped of markdown,
em/en dashes normalized, and emitted as a wrapped YAML block scalar (``>-``).
Codex discovers skills from the skill directory, so AGENTS.md is left untouched.
"""

from __future__ import annotations

from flex_kit.frontmatter import (
    normalize_common,
    serialize_frontmatter,
    strip_markup,
    wrap,
)

ID = "codex"
# Codex natively scans .agents/skills/ (https://developers.openai.com/codex/skills);
# a .codex/skills/ dir is NOT discovered.
BASE_DIR = ".agents/skills"

_LINE_WIDTH = 88
_INDENT = "  "


def render_frontmatter(fm: dict[str, str]) -> str:
    entries: list[tuple[str, str]] = []
    for k, v in fm.items():
        if k != "description":
            entries.append((k, v))
            continue
        clean = strip_markup(normalize_common(v))
        lines = wrap(clean, _LINE_WIDTH - len(_INDENT))
        block = ">-\n" + "\n".join(_INDENT + ln for ln in lines)
        entries.append((k, block))
    return serialize_frontmatter(entries)
