"""Discover and parse skills from a project's neutral source directory."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from flex_kit.frontmatter import parse_skill


@dataclass
class Skill:
    id: str
    dir: Path
    body: str
    frontmatter: dict[str, str]
    references: list[str]  # paths relative to `dir`, copied verbatim per host


def discover_skills(project_root: Path, skills_dir: str) -> list[Skill]:
    root = project_root / skills_dir
    if not root.exists():
        raise FileNotFoundError(f"Skills source not found: {root}")

    skills: list[Skill] = []
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        skill_path = entry / "SKILL.md"
        if not skill_path.exists():
            continue
        fm, body = parse_skill(skill_path.read_text(encoding="utf-8"))
        skills.append(
            Skill(
                id=entry.name,
                dir=entry,
                body=body,
                frontmatter=fm,
                references=_list_files(entry),
            )
        )
    return skills


def _list_files(base: Path) -> list[str]:
    """All files under ``base`` except the top-level SKILL.md, relative to base."""
    out = []
    for p in sorted(base.rglob("*")):
        if p.is_file():
            rel = p.relative_to(base).as_posix()
            if rel != "SKILL.md":
                out.append(rel)
    return out
