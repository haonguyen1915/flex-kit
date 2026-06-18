"""Claude Code host adapter.

Skills -> .claude/skills/<id>/. Claude renders markdown in descriptions, so
backticks / angle brackets are kept; only the shared normalization (em-dash ->
hyphen) is applied.
"""

from __future__ import annotations

from flex_kit.emit import OutFile
from flex_kit.frontmatter import normalize_common, serialize_frontmatter
from flex_kit.skills import Skill

ID = "claude"
SKILLS_DIR = ".claude/skills"


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
