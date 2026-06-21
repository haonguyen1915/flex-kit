"""Discover and parse agents from a project's neutral source directory.

An agent source is a flat `.flexkit/agents/<id>.md`: frontmatter (name,
description, model?, lane?, plus optional codex-only passthrough fields) + a body
(the system prompt). The body may contain a `<!-- SKILLS -->` marker that the
build replaces with the available-skills catalog.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from flex_kit.docs import DOCS_MARKER
from flex_kit.frontmatter import parse_skill, replace_marker

SKILLS_MARKER = "<!-- SKILLS -->"
AGENTS_MARKER = "<!-- AGENTS -->"


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
    """A compact inline list of domain-skill names (`a`, `b`) injected at SKILLS_MARKER.

    Two deliberate trims: (1) `process-*` orchestration skills are excluded - they are the
    main agent's / a command's protocols, wired explicitly where used, not skills a
    subagent applies to code; (2) no descriptions - the host already surfaces each skill's
    name + description, so the catalog only needs to point at which skills exist.
    """
    domain = [s for s in skills if not s.id.startswith("process-")]
    if not domain:
        return "_(none yet - add domain packs with `flex-kit add`)_"
    return ", ".join(f"`{s.id}`" for s in domain)


def inject_skills(body: str, skills) -> str:
    return replace_marker(body, SKILLS_MARKER, skill_catalog(skills))


def agent_catalog(agents: list[Agent]) -> str:
    """One line per agent (id, lane, `[docs]` if it can receive injected docs, lead)
    injected at AGENTS_MARKER - so a command choosing `inject:` targets sees the real
    roster instead of hardcoded names."""
    lines = []
    for a in agents:
        lane = a.frontmatter.get("lane", "")
        tag = f" ({lane})" if lane else ""
        docs = " [docs]" if DOCS_MARKER in a.body else ""
        lines.append(f"- {a.id}{tag}{docs}: {_lead(a.frontmatter.get('description', ''))}")
    return "\n".join(lines)


def inject_agents(body: str, agents: list[Agent]) -> str:
    return replace_marker(body, AGENTS_MARKER, agent_catalog(agents))
