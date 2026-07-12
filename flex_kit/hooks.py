"""Hook logic - the active runtime that keeps the agent oriented and guarded.

flex-kit hooks are subcommands of the one CLI (`flex-kit hook <event>`), wired
into the host via `.claude/settings.json`. Keeping them in a single Python binary
is cleaner than prep-kit's scattered `.cjs` scripts. Hooks are a Claude Code
surface; Codex has no event-hook contract.
"""

from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
import sys
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
    if not (root / ".flexkit").is_dir():
        return  # not a flex-kit project here - never create a stray .flexkit/state.json
    payload = payload or {}
    state = plan_mod._read_state(root)
    agents = _running_map(state)
    key = str(payload.get("agent_id") or len(agents))
    agents[key] = str(payload.get("agent_type") or "agent")
    state["running_agents"] = agents
    state["running_at"] = datetime.now().isoformat(timespec="seconds")
    plan_mod._write_state(root, state)


def subagent_stop(root: Path, payload: dict | None = None) -> None:
    if not (root / ".flexkit").is_dir():
        return  # not a flex-kit project here - never create a stray .flexkit/state.json
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

# Sensitive files the guard refuses to let a tool open. Matched against actual PATH
# arguments only - a file_path, or a path-shaped token in a Bash command - never against
# free prose, a search pattern, or file CONTENT. So a commit message, a grep pattern, or a
# skill body that merely names one of these words is fine; only a real path to a sensitive
# file is blocked. Public templates (.env.example etc.) are committable and exempt.
_SENSITIVE_NAME = re.compile(
    r"\.env(?:\.|$)"
    r"|^(?:id_rsa|id_ed25519|prod-keys)$"
    r"|(?:secret|credential)s?\b.*\.(?:json|ya?ml|env|txt|ini|cfg|conf)$"
    r"|\.(?:pem|key)$",
    re.IGNORECASE,
)
_PUBLIC_TEMPLATE = re.compile(r"\.(?:example|sample|template|dist|defaults?)$", re.IGNORECASE)
# Tool-input keys that carry prose / file content, never a path to gate on.
_NON_PATH_KEYS = frozenset(
    {"description", "prompt", "content", "new_string", "old_string", "command"}
)


def _is_sensitive_path(arg: str) -> bool:
    name = arg.rstrip("/").rsplit("/", 1)[-1]
    if not name or _PUBLIC_TEMPLATE.search(name):
        return False  # public template -> committable, not sensitive
    return bool(_SENSITIVE_NAME.search(name))


def _path_tokens(command: str) -> list[str]:
    try:
        toks = shlex.split(command)
    except ValueError:
        toks = command.split()
    return [t for t in toks if not t.startswith("-")]


def _sensitive_paths_in(payload: dict) -> list[str]:
    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input", {}) or {}
    cands: list[str] = []
    if tool == "Bash":
        cands += _path_tokens(str(ti.get("command", "")))
    elif tool in ("Read", "Edit", "Write", "MultiEdit", "NotebookEdit"):
        cands += [str(ti[k]) for k in ("file_path", "notebook_path") if ti.get(k)]
    else:
        cands += [str(v) for k, v in ti.items() if k not in _NON_PATH_KEYS]
    return [c for c in cands if _is_sensitive_path(c)]


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


def _agents_status(root: Path, p: plan_mod.Plan | None) -> str:
    """Last verifier results from the transient handoffs (`review:approve test:pass`).
    handoffs/ is the current-iteration scratchpad, kept at the repo root."""
    if p is None:
        return "none"
    hdir = root / "handoffs"
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
    third = [f"{_C['dim']}agents {_agents_status(root, p)}{_C['reset']}"]
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
    """Deny a tool call only when it targets a sensitive file PATH.

    Scans path arguments (Read/Edit/Write file_path, Bash command tokens) - not prose,
    search patterns, or file content - so legitimate work that merely names a guarded word
    is allowed; only opening a real sensitive file is blocked."""
    hits = _sensitive_paths_in(payload)
    if hits:
        return f"flex-kit guard: blocked - {hits[0]!r} looks like a sensitive file path"
    return None


# Long-running flex commands worth a desktop notification when they finish. A plain
# chat turn or a quick command (e.g. /flex-status) stays silent.
NOTIFY_COMMANDS = (
    "flex-plan",
    "flex-implement",
    "flex-fix",
    "flex-review",
    "flex-codex-review",
)


def _last_user_prompt(transcript_path: str) -> str | None:
    """The most recent human prompt / slash-command text from the host transcript.

    Tool results are recorded as user-type messages with an *array* content; a real
    prompt (typed text or a slash command) has *string* content. We return the last
    string one - the input that drove the turn that just ended.
    """
    path = Path(transcript_path)
    if not path.is_file():
        return None
    last: str | None = None
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") != "user":
            continue
        content = (ev.get("message") or {}).get("content")
        if isinstance(content, str):
            last = content
    return last


def _finished_notify_command(payload: dict) -> str | None:
    """The NOTIFY_COMMANDS entry the just-ended turn was driven by, else None."""
    tp = payload.get("transcript_path")
    if not tp:
        return None
    prompt = _last_user_prompt(str(tp))
    if not prompt:
        return None
    for cmd in NOTIFY_COMMANDS:
        if f"<command-name>/{cmd}</command-name>" in prompt:
            return cmd
    return None


def _os_notify(title: str, message: str) -> None:
    """Best-effort cross-platform desktop notification. Never raises, never blocks long."""
    try:
        if sys.platform == "darwin":
            script = f'display notification "{message}" with title "{title}" sound name "Glass"'
            cmd = ["osascript", "-e", script]
        elif sys.platform.startswith("linux"):
            if not shutil.which("notify-send"):
                return
            cmd = ["notify-send", title, message]
        elif sys.platform.startswith("win"):
            ps = (
                "[reflection.assembly]::LoadWithPartialName('System.Windows.Forms')|Out-Null;"
                "$n=New-Object System.Windows.Forms.NotifyIcon;"
                "$n.Icon=[System.Drawing.SystemIcons]::Information;$n.Visible=$true;"
                f"$n.ShowBalloonTip(5000,'{title}','{message}',"
                "[System.Windows.Forms.ToolTipIcon]::Info)"
            )
            cmd = ["powershell", "-NoProfile", "-Command", ps]
        else:
            return
        subprocess.run(cmd, timeout=10, check=False, capture_output=True)
    except Exception:
        pass


def stop(payload: dict | None = None) -> None:
    """Stop hook: notify when a long-running flex command finishes (if enabled)."""
    cmd = _finished_notify_command(payload or {})
    if cmd:
        _os_notify("flex-kit", f"/{cmd} done")
