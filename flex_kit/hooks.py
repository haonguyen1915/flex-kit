"""Hook logic - the active runtime that keeps the agent oriented and guarded.

flex-kit hooks are subcommands of the one CLI (`flex-kit hook <event>`), wired
into the host via `.claude/settings.json`. Keeping them in a single Python binary
is cleaner than prep-kit's scattered `.cjs` scripts. Hooks are a Claude Code
surface; Codex has no event-hook contract.
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from flex_kit import plan as plan_mod

# A run is "live" while at least one subagent is active. SubagentStart/Stop hooks bump
# a counter in state.json; the TTL guards against a missed Stop (e.g. a crash) leaving
# the bar stuck on "active".
_RUNTIME_TTL = timedelta(minutes=5)


def _running_map(state: dict) -> dict[str, str]:
    raw = state.get("running_agents") or {}
    return {str(k): str(v) for k, v in raw.items()}


def subagent_start(root: Path, payload: dict | None = None) -> None:
    """SubagentStart: record the agent (`agent_type`) by its `agent_id`."""
    payload = payload or {}
    state = plan_mod._read_state(root)
    agents = _running_map(state)
    key = str(payload.get("agent_id") or len(agents))
    agents[key] = str(payload.get("agent_type") or "agent")
    state["running_agents"] = agents
    state["running_at"] = datetime.now().isoformat(timespec="seconds")
    plan_mod._write_state(root, state)


def subagent_stop(root: Path, payload: dict | None = None) -> None:
    payload = payload or {}
    state = plan_mod._read_state(root)
    agents = _running_map(state)
    key = payload.get("agent_id")
    if key is not None and str(key) in agents:
        agents.pop(str(key))
    elif agents:
        agents.pop(next(iter(agents)))
    state["running_agents"] = agents
    plan_mod._write_state(root, state)


def _running_agents(root: Path) -> list[str]:
    """Names of subagents running now (empty when idle, or when the data is stale)."""
    state = plan_mod._read_state(root)
    agents = _running_map(state)
    if not agents:
        return []
    at = state.get("running_at")
    if at:
        try:
            if datetime.now() - datetime.fromisoformat(at) > _RUNTIME_TTL:
                return []  # stale - a Stop was likely missed
        except ValueError:
            pass
    return list(agents.values())

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


# Status-bar styling. Unlike CLI output, this is ALWAYS colored: the host renders the
# status line itself, so we emit ANSI directly (not via ui.py, which strips color when
# piped). Raw codes keep rich out of this hot path.
_C = {
    "reset": "\033[0m",
    "dim": "\033[2m",
    "cyan": "\033[1;36m",
    "green": "\033[32m",
    "yellow": "\033[33m",
}


def _short_path(path: str) -> str:
    parts = Path(path).parts
    return "/".join(parts[-2:]) if len(parts) > 2 else path


def _git_dirty(root: Path) -> str:
    """` ?N` when the tree has N uncommitted entries, else empty."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        n = len([ln for ln in out.stdout.splitlines() if ln.strip()])
        return f" ?{n}" if n else ""
    except Exception:
        return ""


def _human(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.0f}M"
    if n >= 1_000:
        return f"{n // 1000}k"
    return str(n)


def _fmt_duration(ms: float) -> str:
    s = int(ms // 1000)
    h, m = s // 3600, (s % 3600) // 60
    if h:
        return f"{h}h{m:02d}m"
    if m:
        return f"{m}m{s % 60:02d}s"
    return f"{s}s"


def _bar(pct: float, width: int = 8) -> str:
    filled = max(0, min(width, round(pct / 100 * width)))
    return f"{_C['dim']}{'▰' * filled}{'▱' * (width - filled)}{_C['reset']}"


def _ctx_segment(payload: dict) -> str | None:
    """`ctx 114k/1M 11% ▰▱▱…` from the host's context_window payload, if present."""
    ctx = payload.get("context_window") or {}
    size = int(ctx.get("context_window_size") or 0)
    usage = ctx.get("current_usage") or {}
    used = sum(
        int(usage.get(k) or 0)
        for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    )
    pct = ctx.get("used_percentage")
    if not size and not used:
        return None
    if pct is None and size:
        pct = used / size * 100
    pct = float(pct or 0)
    used_h = _human(used) if used else "?"
    size_h = _human(size) if size else "?"
    return f"{_C['green']}ctx {used_h}/{size_h} {int(pct)}%{_C['reset']} {_bar(pct)}"


def _agents_status(p: plan_mod.Plan | None) -> str:
    """Last verifier results from the plan's handoffs (`review:approve test:pass`)."""
    if p is None:
        return "none"
    hdir = p.dir / "handoffs"
    bits: list[str] = []
    verdict = hdir / "review-verdict.md"
    if verdict.exists():
        t = verdict.read_text(encoding="utf-8", errors="ignore").lower()
        v = "revise" if "revise" in t else "approve" if "approve" in t else "?"
        bits.append(f"review:{v}")
    report = hdir / "test-report.md"
    if report.exists():
        t = report.read_text(encoding="utf-8", errors="ignore").lower()
        r = "fail" if "fail" in t else "pass" if "pass" in t else "?"
        bits.append(f"test:{r}")
    return " ".join(bits) if bits else "none"


def status_line(root: Path, payload: dict | None = None) -> str:
    """Multi-line status for the Claude Code status bar.

    Line 1: model · cwd · git±dirty · plan. Line 2 (when the host supplies it):
    ctx usage + bar · cost · duration. Line 3: the next step. `payload` is the JSON
    Claude Code pipes to the statusLine command (empty when run by hand).
    """
    payload = payload or {}
    sep = f"{_C['dim']} · {_C['reset']}"

    top: list[str] = []
    model = (payload.get("model") or {}).get("display_name")
    top.append(f"{_C['cyan']}{model or 'flex-kit'}{_C['reset']}")
    cwd = (payload.get("workspace") or {}).get("current_dir") or str(root)
    top.append(f"{_C['dim']}{_short_path(cwd)}{_C['reset']}")
    branch = _git_branch(root)
    if branch:
        top.append(f"{_C['yellow']}⎇ {branch}{_git_dirty(root)}{_C['reset']}")
    p = plan_mod.active_plan(root)
    if p is None:
        top.append(f"{_C['dim']}plan none{_C['reset']}")
    else:
        v = p.mode_verdict
        color = _C["yellow"] if v.reason else _C["green"]
        top.append(f"plan {color}{v.effective} {p.done_count}/{len(p.steps)}{_C['reset']}")
    lines = [sep.join(top)]

    # Line 2: context, gate, runtime, cost, time.
    bottom: list[str] = []
    ctx = _ctx_segment(payload)
    if ctx:
        bottom.append(ctx)
    escalated = bool(p and p.mode_verdict.reason)
    gate_color = _C["yellow"] if escalated else _C["dim"]
    bottom.append(f"{gate_color}gate {'scope' if escalated else 'n/a'}{_C['reset']}")
    running = _running_agents(root)
    if running:
        names = ", ".join(dict.fromkeys(running))  # de-dup, keep order
        bottom.append(f"{_C['green']}runtime active: {names}{_C['reset']}")
    else:
        bottom.append(f"{_C['dim']}runtime idle{_C['reset']}")
    cost = payload.get("cost") or {}
    if cost.get("total_cost_usd") is not None:
        bottom.append(f"{_C['dim']}${cost['total_cost_usd']:.4f}{_C['reset']}")
    if cost.get("total_duration_ms"):
        bottom.append(f"{_C['dim']}{_fmt_duration(cost['total_duration_ms'])}{_C['reset']}")
    lines.append(sep.join(bottom))

    # Line 3: last verifier results + next step.
    third = [f"{_C['dim']}agents {_agents_status(p)}{_C['reset']}"]
    if p is not None and p.next_step:
        text = p.next_step.text
        text = text if len(text) <= 50 else text[:49] + "…"
        third.append(f"{_C['dim']}next: {text}{_C['reset']}")
    lines.append(sep.join(third))

    return "\n".join(lines)


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
