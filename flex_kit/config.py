"""Load a project's .flexkit/flexkit.config.json, applying defaults."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

_DEFAULT_HOSTS = ["claude", "codex"]
_DEFAULT_SKILLS_DIR = ".flexkit/skills"
_DEFAULT_AGENTS_DIR = ".flexkit/agents"
_DEFAULT_COMMANDS_DIR = ".flexkit/commands"
_DEFAULT_DOCS_DIR = "docs"  # project specs/conventions, indexed into agents via <!-- DOCS -->


@dataclass
class Config:
    hosts: list[str] = field(default_factory=lambda: list(_DEFAULT_HOSTS))
    skills_dir: str = _DEFAULT_SKILLS_DIR
    agents_dir: str = _DEFAULT_AGENTS_DIR
    commands_dir: str = _DEFAULT_COMMANDS_DIR
    docs_dir: str = _DEFAULT_DOCS_DIR


def load_config(project_root: Path) -> Config:
    path = project_root / ".flexkit" / "flexkit.config.json"
    if not path.exists():
        raise FileNotFoundError(f"No .flexkit/flexkit.config.json found in {project_root}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return Config(
        hosts=raw.get("hosts", list(_DEFAULT_HOSTS)),
        skills_dir=raw.get("skillsDir", _DEFAULT_SKILLS_DIR),
        agents_dir=raw.get("agentsDir", _DEFAULT_AGENTS_DIR),
        commands_dir=raw.get("commandsDir", _DEFAULT_COMMANDS_DIR),
        docs_dir=raw.get("docsDir", _DEFAULT_DOCS_DIR),
    )
