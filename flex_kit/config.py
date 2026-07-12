"""Config resolution - a global layer (~/.flex-kit/config.toml) overlaid by a project's
.flexkit/config.toml.

Precedence, low to high: built-in defaults < global (~/.flex-kit) < project (.flexkit/).
The global layer lets a user set machine-wide defaults once (e.g. the Codex review model)
without editing every project. Set `FLEXKIT_GLOBAL_CONFIG` to point the global file elsewhere
(the test suite uses this to stay hermetic).

Files are TOML (so they can carry comments). A legacy `.json` (or `.flexkit.config.json`)
with the same camelCase keys is still read when no `.toml` is present, so pre-migration
projects keep working. TOML has no null - an unset key simply means "use the default", which is
exactly how `codexModel` being absent selects Codex's own model.
"""

from __future__ import annotations

import json
import os
import tomllib
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


def _first_existing(*paths: Path) -> Path | None:
    return next((p for p in paths if p.is_file()), None)


def global_config_path() -> Path:
    """The machine-wide config file. `~/.flex-kit/config.toml` (legacy `.json` read if it is
    the only one present); overridable via FLEXKIT_GLOBAL_CONFIG for tests."""
    override = os.environ.get("FLEXKIT_GLOBAL_CONFIG")
    if override:
        return Path(override)
    base = Path.home() / ".flex-kit"
    return _first_existing(base / "config.toml", base / "config.json") or base / "config.toml"


def project_config_path(project_root: Path) -> Path:
    """The project's config file: `.flexkit/config.toml`. Falls back to a legacy `config.json`
    or `flexkit.config.json` when only those older files are present, so pre-migration projects
    keep working. Returns the canonical `.toml` path when none exists (for creation / messages)."""
    flexkit = project_root / ".flexkit"
    return _first_existing(
        flexkit / "config.toml", flexkit / "config.json", flexkit / "flexkit.config.json"
    ) or (flexkit / "config.toml")


def _read_config(path: Path) -> dict:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix == ".json" else tomllib.loads(text)


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


def config_as_dict(cfg: Config) -> dict:
    """A Config back as the camelCase key dict used in the config files - so `config show`
    and the templates speak the same keys the user edits."""
    return {
        "hosts": cfg.hosts,
        "skillsDir": cfg.skills_dir,
        "agentsDir": cfg.agents_dir,
        "commandsDir": cfg.commands_dir,
        "docsDir": cfg.docs_dir,
        "notify": cfg.notify,
        "codexModel": cfg.codex_model,
        "codexEffort": cfg.codex_effort,
    }


def dumps_toml(d: dict) -> str:
    """Serialize a flat config dict to TOML. `None` is omitted (TOML has no null - absence is
    the default). `json.dumps` already renders str / bool / list of str as valid TOML values."""
    lines = [f"{k} = {json.dumps(v)}" for k, v in d.items() if v is not None]
    return "\n".join(lines) + ("\n" if lines else "")


_TEMPLATE_CONFIG = Path(__file__).parent / "templates" / "flexkit" / "config.toml"

# Seed for a freshly created global ~/.flex-kit/config.toml - only the machine-wide knobs,
# each documented and mostly commented so an unset key keeps the default.
_GLOBAL_SEED = """\
# flex-kit global config (~/.flex-kit/config.toml). Machine-wide defaults; a project's
# .flexkit/config.toml overrides these. Every key is optional - omit one to keep its default.

# Codex cross-model review. Leave codexModel unset to use Codex's own model (the latest it
# ships / your ~/.codex/config.toml); set it to pin one model for every project.
# codexModel = "gpt-5.5"
codexEffort = "high"          # reasoning effort: low | medium | high

# Desktop notification when a long-running flex command finishes.
# notify = true
"""


def default_config_text(*, global_scope: bool) -> str:
    """Seed text for a freshly created config file - a documented TOML skeleton. Project scope
    reuses the shipped template; global scope seeds just the machine-wide knobs."""
    if global_scope:
        return _GLOBAL_SEED
    return _TEMPLATE_CONFIG.read_text(encoding="utf-8")


def _merged_raw(project_root: Path, *, require_project: bool) -> dict:
    """Global config overlaid by the project's - project keys win over global, global over
    defaults. Raises if `require_project` and the project has no config file."""
    project_path = project_config_path(project_root)
    if require_project and not project_path.is_file():
        raise FileNotFoundError(f"No .flexkit/config.toml found in {project_root}")
    return {**_read_config(global_config_path()), **_read_config(project_path)}


def load_config(project_root: Path) -> Config:
    """Project config merged onto the global layer. Raises when the project has none -
    gen / doctor / init-docs need a real flex-kit project."""
    return _from_raw(_merged_raw(project_root, require_project=True))


def resolve_config(project_root: Path) -> Config:
    """Like `load_config` but tolerant of a missing project config - for flows that may run
    outside a flex-kit project (e.g. `codex-review --type diff` on a bare git repo). Falls
    back to global + defaults when the project has no config file."""
    return _from_raw(_merged_raw(project_root, require_project=False))
