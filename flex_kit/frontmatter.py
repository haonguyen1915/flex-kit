"""Frontmatter parsing + shared text transforms.

The neutral source SKILL.md carries a canonical frontmatter (``name`` + a
single-line ``description``, markdown allowed). Each host adapter renders that
frontmatter into its own dialect; this module owns the transforms they share.
"""

from __future__ import annotations

import re

FM_DELIM = "---"
_EM_DASH = re.compile(r"[—–]")  # em-dash + en-dash -> hyphen
_WS = re.compile(r"[ \t]+")
_BLOCK_SCALAR = {">-", ">", "|", "|-"}
_KEY = re.compile(r"^([A-Za-z0-9_-]+):\s?(.*)$")
_INDENTED = re.compile(r"^\s+\S")


def parse_skill(raw: str) -> tuple[dict[str, str], str]:
    """Split a raw SKILL.md into ``(frontmatter, body)``."""
    lines = raw.split("\n")
    if not lines or lines[0].strip() != FM_DELIM:
        raise ValueError("SKILL.md missing opening `---` frontmatter delimiter")
    end = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == FM_DELIM:
            end = i
            break
    if end == -1:
        raise ValueError("SKILL.md missing closing `---` frontmatter delimiter")

    fm = _parse_frontmatter(lines[1:end])
    body = "\n".join(lines[end + 1 :]).lstrip("\n")
    return fm, body


def _parse_frontmatter(lines: list[str]) -> dict[str, str]:
    """Read ``key: value`` and folded block scalars into an ordered dict."""
    out: dict[str, str] = {}
    i = 0
    while i < len(lines):
        m = _KEY.match(lines[i])
        if not m:
            i += 1
            continue
        key, value = m.group(1), m.group(2)
        if value in _BLOCK_SCALAR:
            folded = []
            while i + 1 < len(lines) and _INDENTED.match(lines[i + 1]):
                i += 1
                folded.append(lines[i].strip())
            value = " ".join(folded)
        out[key] = value.strip()
        i += 1
    return out


def normalize_common(s: str) -> str:
    """Applied for every host: kill em/en dashes, collapse runs of spaces."""
    return _WS.sub(" ", _EM_DASH.sub("-", s)).strip()


def strip_markup(s: str) -> str:
    """Strip markdown a plain-text frontmatter consumer should not see."""
    s = s.replace("`", "").replace("<", "").replace(">", "")
    return _WS.sub(" ", s).strip()


def wrap(s: str, width: int) -> list[str]:
    """Greedy word-wrap to a max line width."""
    lines: list[str] = []
    line = ""
    for word in s.split():
        if not line:
            line = word
        elif len(line) + 1 + len(word) <= width:
            line += " " + word
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def serialize_frontmatter(entries: list[tuple[str, str]]) -> str:
    """Serialize ordered frontmatter pairs to a ``---``-less YAML block."""
    return "\n".join(f"{k}: {v}" for k, v in entries)
