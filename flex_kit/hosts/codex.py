"""Codex host adapter.

Skills -> .agents/skills/<id>/ (Codex natively scans this; SKILL.md frontmatter
is name + description). Codex frontmatter is plain text, so the description is
stripped of markdown and em/en dashes normalized, kept on a single line (no YAML
block scalar is required).
"""

from __future__ import annotations

from flex_kit.emit import OutFile
from flex_kit.frontmatter import normalize_common, serialize_frontmatter, strip_markup
from flex_kit.skills import Skill

ID = "codex"
SKILLS_DIR = ".agents/skills"


def _clean(text: str) -> str:
    return strip_markup(normalize_common(text))


def emit_skill(skill: Skill) -> list[OutFile]:
    entries = [
        (k, _clean(v) if k == "description" else v)
        for k, v in skill.frontmatter.items()
    ]
    content = f"---\n{serialize_frontmatter(entries)}\n---\n\n{skill.body.rstrip()}\n"
    files = [OutFile(f"{SKILLS_DIR}/{skill.id}/SKILL.md", content)]
    files += [
        OutFile(f"{SKILLS_DIR}/{skill.id}/{rel}", copy_from=skill.dir / rel)
        for rel in skill.references
    ]
    return files
