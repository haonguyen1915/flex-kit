"""Claude Code host adapter.

Skills -> .claude/skills/<id>/ ; agents -> .claude/agents/<id>.md.
Claude renders markdown in descriptions, so backticks / angle brackets are kept;
only the shared normalization (em-dash -> hyphen) is applied. The agent `model`
frontmatter is a Claude model alias, passed through as-is.
"""

from __future__ import annotations

import json

from flex_kit.agents import Agent, inject_skills
from flex_kit.commands import Command
from flex_kit.emit import OutFile
from flex_kit.frontmatter import normalize_common, serialize_frontmatter
from flex_kit.skills import Skill

ID = "claude"
SKILLS_DIR = ".claude/skills"
AGENTS_DIR = ".claude/agents"
COMMANDS_DIR = ".claude/commands"
SETTINGS_FILE = ".claude/settings.json"

_HOOKS = {
    # "compact" re-orients after compaction - flex-kit's state is durable in plans/,
    # so re-running session-start is enough; no separate snapshot hook is needed.
    "SessionStart": [
        {
            "matcher": "startup|resume|clear|compact",
            "hooks": [{"type": "command", "command": "flex-kit hook session-start"}],
        }
    ],
    "UserPromptSubmit": [
        {"hooks": [{"type": "command", "command": "flex-kit hook user-prompt"}]}
    ],
    "PreToolUse": [
        {
            "matcher": "Bash|Read|Edit|Write|Glob|Grep",
            "hooks": [{"type": "command", "command": "flex-kit hook pre-tool"}],
        }
    ],
}


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


def emit_command(command: Command, skills: list[Skill]) -> list[OutFile]:
    fm = command.frontmatter
    # Claude commands key off the filename, so `name` is dropped from frontmatter.
    entries = [("description", normalize_common(fm["description"]))]
    if fm.get("argument-hint"):
        entries.append(("argument-hint", fm["argument-hint"]))
    body = inject_skills(command.body, skills)
    content = f"---\n{serialize_frontmatter(entries)}\n---\n\n{body.rstrip()}\n"
    return [OutFile(f"{COMMANDS_DIR}/{command.id}.md", content)]


def emit_global() -> list[OutFile]:
    """Host-level output not tied to a single capability: the hooks wiring."""
    content = json.dumps({"hooks": _HOOKS}, indent=2) + "\n"
    return [OutFile(SETTINGS_FILE, content)]
