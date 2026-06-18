"""Hook logic - the active runtime that keeps the agent oriented and guarded.

flex-kit hooks are subcommands of the one CLI (`flex-kit hook <event>`), wired
into the host via `.claude/settings.json`. Keeping them in a single Python binary
is cleaner than prep-kit's scattered `.cjs` scripts. Hooks are a Claude Code
surface; Codex has no event-hook contract.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from flex_kit import plan as plan_mod

_SECRET = re.compile(
    r"\.env(\.|$)|\.env\.(production|prod|staging|live)|\.pem$|\.key$|credentials|"
    r"secret|prod-keys|id_rsa|id_ed25519",
    re.IGNORECASE,
)


def _git_branch(root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        return out.stdout.strip() or None
    except Exception:
        return None


def session_start(root: Path) -> str:
    """One orientation line injected at session start: branch + active plan + next."""
    parts: list[str] = []
    branch = _git_branch(root)
    if branch:
        parts.append(f"branch {branch}")
    p = plan_mod.active_plan(root)
    if p is None:
        parts.append("no active plan")
    else:
        v = p.mode_verdict
        parts.append(f"plan {p.id} ({v.effective}, {p.done_count}/{len(p.steps)} steps)")
        nxt = p.next_step
        if nxt:
            parts.append(f"next: {nxt.text}")
    return "flex-kit: " + "; ".join(parts)


def user_prompt(root: Path) -> str | None:
    """Per-prompt plan reminder, deduped - only fires when plan state advances."""
    p = plan_mod.active_plan(root)
    if p is None:
        return None
    v = p.mode_verdict
    nxt = p.next_step
    sig = f"{p.id}|{v.effective}|{p.done_count}/{len(p.steps)}|{nxt.text if nxt else ''}"
    if not plan_mod.reminder_changed(root, sig):
        return None
    line = f"flex-kit plan: {v.effective} {p.done_count}/{len(p.steps)} steps"
    return f"{line}; next: {nxt.text}" if nxt else line


def pre_tool_decision(payload: dict) -> str | None:
    """Return a deny reason if a tool call touches a secret/credential path."""
    tool_input = payload.get("tool_input", {})
    text = " ".join(str(v) for v in tool_input.values())
    if _SECRET.search(text):
        return "flex-kit guard: blocked access to a secret/credential path"
    return None
