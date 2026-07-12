"""Config resolution - a global layer (~/.flex-kit/config.json) overlaid by a project's
.flexkit/flexkit.config.json.

Precedence, low to high: built-in defaults < global (~/.flex-kit) < project (.flexkit/).
The global layer lets a user set machine-wide defaults once (e.g. the Codex review model)
without editing every project. Set `FLEXKIT_GLOBAL_CONFIG` to point the global file elsewhere
(the test suite uses this to stay hermetic).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

_DEFAULT_HOSTS = ["claude", "codex"]
_DEFAULT_SKILLS_DIR = ".flexkit/skills"
_DEFAULT_AGENTS_DIR = ".flexkit/agents"
_DEFAULT_COMMANDS_DIR = ".flexkit/commands"
_DEFAULT_DOCS_DIR = "docs"  # project specs/conventions, indexed into agents via <!-- DOCS -->
_DEFAULT_CODEX_EFFORT = "high"


@dataclass
class Config:
    hosts: list[str] = field(default_factory=lambda: list(_DEFAULT_HOSTS))
    skills_dir: str = _DEFAULT_SKILLS_DIR
    agents_dir: str = _DEFAULT_AGENTS_DIR
    commands_dir: str = _DEFAULT_COMMANDS_DIR
    docs_dir: str = _DEFAULT_DOCS_DIR
    # Opt-in: fire a cross-platform desktop notification when a long-running flex
    # command finishes (Claude host only). Off by default; wires a Stop hook when true.
    notify: bool = False
    # Codex cross-model review knobs. `codex_model = None` means "don't pass -m" so
    # `codex exec` uses its own default (whatever ~/.codex/config.toml / Codex ships) -
    # the "always use the latest" path. Set it (globally or per-project) to pin a model.
    codex_model: str | None = None
    codex_effort: str = _DEFAULT_CODEX_EFFORT


def global_config_path() -> Path:
    """The machine-wide config file. `~/.flex-kit/config.json`, overridable for tests."""
    override = os.environ.get("FLEXKIT_GLOBAL_CONFIG")
    return Path(override) if override else Path.home() / ".flex-kit" / "config.json"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _from_raw(raw: dict) -> Config:
    return Config(
        hosts=raw.get("hosts", list(_DEFAULT_HOSTS)),
        skills_dir=raw.get("skillsDir", _DEFAULT_SKILLS_DIR),
        agents_dir=raw.get("agentsDir", _DEFAULT_AGENTS_DIR),
        commands_dir=raw.get("commandsDir", _DEFAULT_COMMANDS_DIR),
        docs_dir=raw.get("docsDir", _DEFAULT_DOCS_DIR),
        notify=bool(raw.get("notify", False)),
        codex_model=raw.get("codexModel"),
        codex_effort=raw.get("codexEffort", _DEFAULT_CODEX_EFFORT),
    )


def _merged_raw(project_root: Path, *, require_project: bool) -> dict:
    """Global config overlaid by the project's - project keys win over global, global over
    defaults. Raises if `require_project` and the project has no flexkit.config.json."""
    project_path = project_root / ".flexkit" / "flexkit.config.json"
    if require_project and not project_path.is_file():
        raise FileNotFoundError(f"No .flexkit/flexkit.config.json found in {project_root}")
    return {**_read_json(global_config_path()), **_read_json(project_path)}


def load_config(project_root: Path) -> Config:
    """Project config merged onto the global layer. Raises when the project has none -
    gen / doctor / init-docs need a real flex-kit project."""
    return _from_raw(_merged_raw(project_root, require_project=True))


def resolve_config(project_root: Path) -> Config:
    """Like `load_config` but tolerant of a missing project config - for flows that may run
    outside a flex-kit project (e.g. `codex-review --type diff` on a bare git repo). Falls
    back to global + defaults when the project has no flexkit.config.json."""
    return _from_raw(_merged_raw(project_root, require_project=False))
