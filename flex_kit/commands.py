"""Discover and parse slash commands from a project's neutral source.

A command source is a flat `.flexkit/commands/<id>.md`: frontmatter (name,
description, optional argument-hint) + a body (the prose that drives the flow).
Commands are a Claude Code surface (`.claude/commands/<id>.md`); the Codex host
does not emit them. The body may contain `<!-- SKILLS -->` for the skill catalog.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from flex_kit.frontmatter import parse_skill


@dataclass
class Command:
    id: str
    body: str
    frontmatter: dict[str, str]


def discover_commands(project_root: Path, commands_dir: str) -> list[Command]:
    """Commands are optional: a missing source dir yields an empty list."""
    root = project_root / commands_dir
    if not root.exists():
        return []
    commands: list[Command] = []
    for path in sorted(root.glob("*.md")):
        fm, body = parse_skill(path.read_text(encoding="utf-8"))
        commands.append(Command(id=path.stem, body=body, frontmatter=fm))
    return commands
