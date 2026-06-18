"""Claude Code host adapter.

Claude renders markdown in skill descriptions, so backticks / angle brackets are
kept and the description stays a single line. Only the shared normalization
(em-dash -> hyphen) is applied.
"""

from __future__ import annotations

from flex_kit.frontmatter import normalize_common, serialize_frontmatter

ID = "claude"
BASE_DIR = ".claude/skills"


def render_frontmatter(fm: dict[str, str]) -> str:
    entries = [
        (k, normalize_common(v) if k == "description" else v) for k, v in fm.items()
    ]
    return serialize_frontmatter(entries)
