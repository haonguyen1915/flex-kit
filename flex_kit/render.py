"""Pure rendering: the SKILL.md content a host should have for a skill.

Shared by ``gen`` (writes it) and the generated-in-sync check (compares it), so
the two can never disagree about what "correct output" means.
"""

from __future__ import annotations

import re

from flex_kit.skills import Skill

_TRAILING = re.compile(r"\s*$")


def render_skill_content(host, skill: Skill) -> str:
    fm = host.render_frontmatter(skill.frontmatter)
    body = _TRAILING.sub("", skill.body)
    return f"---\n{fm}\n---\n\n{body}\n"
