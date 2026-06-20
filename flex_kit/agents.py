"""Discover and parse agents from a project's neutral source directory.

An agent source is a flat `.flexkit/agents/<id>.md`: frontmatter (name,
description, model?, lane?, plus optional codex-only passthrough fields) + a body
(the system prompt). The body may contain a `<!-- SKILLS -->` marker that the
build replaces with the available-skills catalog.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from flex_kit.frontmatter import parse_skill, replace_marker

SKILLS_MARKER = "<!-- SKILLS -->"


@dataclass
class Agent:
    id: str
    body: str
    frontmatter: dict[str, str]


def discover_agents(project_root: Path, agents_dir: str) -> list[Agent]:
    """Agents are optional: a missing source dir yields an empty list."""
    root = project_root / agents_dir
    if not root.exists():
        return []
    agents: list[Agent] = []
    for path in sorted(root.glob("*.md")):
        fm, body = parse_skill(path.read_text(encoding="utf-8"))
        agents.append(Agent(id=path.stem, body=body, frontmatter=fm))
    return agents


def _lead(desc: str) -> str:
    """The lead clause of a description - up to the first ` - ` or sentence period.

    The full description drives host triggering (kept in each skill file); the catalog
    only needs enough for an agent to pick, so it stays terse.
    """
    cuts = [i for i in (desc.find(" - "), desc.find(". ")) if i != -1]
    return (desc[: min(cuts)] if cuts else desc).strip().rstrip(".")


def skill_catalog(skills) -> str:
    """A one-line-per-skill catalog (id + lead clause) injected at SKILLS_MARKER."""
    return "\n".join(f"- {s.id}: {_lead(s.frontmatter.get('description', ''))}" for s in skills)


def inject_skills(body: str, skills) -> str:
    return replace_marker(body, SKILLS_MARKER, skill_catalog(skills))
