"""Claude Code host adapter.

Skills -> .claude/skills/<id>/ ; agents -> .claude/agents/<id>.md.
Claude renders markdown in descriptions, so backticks / angle brackets are kept;
only the shared normalization (em-dash -> hyphen) is applied. The agent `model`
frontmatter is a Claude model alias, passed through as-is.
"""

from __future__ import annotations

from flex_kit.agents import Agent, inject_skills
from flex_kit.emit import OutFile
from flex_kit.frontmatter import normalize_common, serialize_frontmatter
from flex_kit.skills import Skill

ID = "claude"
SKILLS_DIR = ".claude/skills"
AGENTS_DIR = ".claude/agents"


def emit_skill(skill: Skill) -> list[OutFile]:
    entries = [
        (k, normalize_common(v) if k == "description" else v)
        for k, v in skill.frontmatter.items()
    ]
    content = f"---\n{serialize_frontmatter(entries)}\n---\n\n{skill.body.rstrip()}\n"
    files = [OutFile(f"{SKILLS_DIR}/{skill.id}/SKILL.md", content)]
    files += [
        OutFile(f"{SKILLS_DIR}/{skill.id}/{rel}", copy_from=skill.dir / rel)
        for rel in skill.references
    ]
    return files


def emit_agent(agent: Agent, skills: list[Skill]) -> list[OutFile]:
    fm = agent.frontmatter
    entries = [("name", fm["name"]), ("description", normalize_common(fm["description"]))]
    if fm.get("model"):
        entries.append(("model", fm["model"]))
    body = inject_skills(agent.body, skills)
    content = f"---\n{serialize_frontmatter(entries)}\n---\n\n{body.rstrip()}\n"
    return [OutFile(f"{AGENTS_DIR}/{agent.id}.md", content)]
