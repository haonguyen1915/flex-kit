"""Codex host adapter.

Skills -> .agents/skills/<id>/ (Codex natively scans this; SKILL.md frontmatter
is name + description). Agents -> .codex/agents/<id>.toml.

Codex frontmatter is plain text, so the description is stripped of markdown and
em/en dashes normalized, kept on a single line (no YAML block scalar required).
"""

from __future__ import annotations

from flex_kit.agents import Agent, inject_skills
from flex_kit.docs import Doc, inject_docs
from flex_kit.emit import OutFile
from flex_kit.frontmatter import normalize_common, serialize_frontmatter, strip_markup
from flex_kit.skills import Skill

ID = "codex"
SKILLS_DIR = ".agents/skills"
AGENTS_DIR = ".codex/agents"

_DEFAULT_MODEL = "gpt-5.5"
_DEFAULT_REASONING = "medium"
# Map Claude model aliases to a Codex model; pass through anything already gpt-*.
_MODEL_MAP = {"opus": _DEFAULT_MODEL, "sonnet": _DEFAULT_MODEL, "haiku": _DEFAULT_MODEL}


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


def _codex_model(model: str | None) -> str:
    if not model:
        return _DEFAULT_MODEL
    if model.startswith("gpt"):
        return model
    return _MODEL_MAP.get(model, _DEFAULT_MODEL)


def _toml_basic(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def emit_agent(agent: Agent, skills: list[Skill], docs: list[Doc]) -> list[OutFile]:
    fm = agent.frontmatter
    body = inject_docs(inject_skills(agent.body, skills), docs).rstrip()
    lines = [
        f'name = "{_toml_basic(fm["name"])}"',
        f'description = "{_toml_basic(_clean(fm["description"]))}"',
        f'model = "{_codex_model(fm.get("model"))}"',
        f'model_reasoning_effort = "{fm.get("reasoning_effort", _DEFAULT_REASONING)}"',
    ]
    if fm.get("sandbox_mode"):
        lines.append(f'sandbox_mode = "{fm["sandbox_mode"]}"')
    # Literal multi-line string ('''…''') avoids escaping markdown/backslashes.
    lines.append(f"developer_instructions = '''\n{body}\n'''")
    content = "\n".join(lines) + "\n"
    return [OutFile(f"{AGENTS_DIR}/{agent.id}.toml", content)]
