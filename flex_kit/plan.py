"""Plan lifecycle - durable, multi-step work state that survives context resets.

A plan is a directory under `plans/active/<id>/` with a `plan.md` (frontmatter +
Goal / Steps / Done Criteria). The active plan is tracked in `.flexkit/state.json`
so `status` / `next-step` always know where work stands. `close` archives it.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from flex_kit import modes

ACTIVE_DIR = "plans/active"
ARCHIVE_DIR = "plans/archive"
STATE_FILE = ".flexkit/state.json"

_STEP = re.compile(r"^- \[( |x)\] (.+)$")
_META = re.compile(r"^- (\w[\w ]*?): (.*)$")


@dataclass
class Step:
    done: bool
    text: str


@dataclass
class Plan:
    id: str
    dir: Path
    title: str
    mode: str
    status: str
    steps: list[Step]
    files: list[str] = field(default_factory=list)

    @property
    def done_count(self) -> int:
        return sum(1 for s in self.steps if s.done)

    @property
    def next_step(self) -> Step | None:
        return next((s for s in self.steps if not s.done), None)

    @property
    def mode_verdict(self) -> modes.ModeVerdict:
        return modes.effective_mode(self.mode, len(self.steps), len(self.files))


def _slugify(title: str, max_len: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if len(slug) > max_len:  # cap the slug so plan folder names stay short, cut on a word
        slug = slug[:max_len].rsplit("-", 1)[0] or slug[:max_len]
    return slug or "plan"


def _read_state(root: Path) -> dict:
    path = root / STATE_FILE
    return json.loads(path.read_text()) if path.exists() else {}


def _write_state(root: Path, state: dict) -> None:
    path = root / STATE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _render(plan_id: str, title: str, mode: str, created: str) -> str:
    return (
        f"# Plan: {title}\n\n"
        f"- id: {plan_id}\n"
        f"- created: {created}\n"
        f"- mode: {mode}\n"
        f"- status: active\n\n"
        "## Goal\n\n_Describe the outcome._\n\n"
        "## Steps\n\n- [ ] first step\n\n"
        "## Files In Scope\n\n_- path/to/file_\n\n"
        "## Done Criteria\n\n_How we know it is finished._\n"
    )


def _parse(plan_dir: Path) -> Plan:
    text = (plan_dir / "plan.md").read_text(encoding="utf-8")
    title, meta, steps, files, section = plan_dir.name, {}, [], [], ""
    for line in text.splitlines():
        if line.startswith("# Plan: "):
            title = line[len("# Plan: ") :].strip()
        elif line.startswith("## "):
            section = line[3:].strip().lower()
        elif m := _STEP.match(line):
            steps.append(Step(done=m.group(1) == "x", text=m.group(2).strip()))
        elif section == "files in scope" and line.startswith("- "):
            files.append(line[2:].strip())
        elif m := _META.match(line):
            meta[m.group(1).strip()] = m.group(2).strip()
    return Plan(
        id=meta.get("id", plan_dir.name),
        dir=plan_dir,
        title=title,
        mode=meta.get("mode", "build"),
        status=meta.get("status", "active"),
        steps=steps,
        files=files,
    )


def create_plan(root: Path, title: str, mode: str = "build", now: datetime | None = None) -> Plan:
    if not modes.is_valid(mode):
        raise ValueError(f"Invalid mode '{mode}' (use one of {', '.join(modes.MODES)})")
    now = now or datetime.now()
    plan_id = f"{now:%y%m%d-%H%M}-{_slugify(title)}"
    plan_dir = root / ACTIVE_DIR / plan_id
    if plan_dir.exists():
        raise FileExistsError(f"Plan {plan_id} already exists")
    plan_dir.mkdir(parents=True)
    (plan_dir / "plan.md").write_text(
        _render(plan_id, title, mode, now.strftime("%Y-%m-%d %H:%M")), encoding="utf-8"
    )
    state = _read_state(root)
    state["active_plan"] = plan_id
    _write_state(root, state)
    return _parse(plan_dir)


def reminder_changed(root: Path, sig: str) -> bool:
    """True (and records `sig`) when it differs from the last reminder - cheap dedup
    so the per-prompt reminder only fires when plan state actually advances."""
    state = _read_state(root)
    if state.get("last_reminder") == sig:
        return False
    state["last_reminder"] = sig
    _write_state(root, state)
    return True


def active_plan(root: Path) -> Plan | None:
    plan_id = _read_state(root).get("active_plan")
    if not plan_id:
        return None
    plan_dir = root / ACTIVE_DIR / plan_id
    return _parse(plan_dir) if (plan_dir / "plan.md").exists() else None


_SPEC_FILES = {
    "proposal.md": (
        "# Proposal\n\n## Problem\n\n## Desired Outcome\n\n## Constraints\n\n"
        "## Options Considered\n\n## Chosen Direction\n"
    ),
    "design.md": (
        "# Design\n\n## Scope\n\n## System Shape\n\n## Data And Contracts\n\n"
        "## Validation Plan\n\n## Risks\n"
    ),
    "tasks.md": "# Tasks\n\n- [ ] first task\n",
}


def scaffold_spec(root: Path) -> Plan:
    """Create spec/{proposal,design,tasks}.md under the active plan (design-first)."""
    plan = active_plan(root)
    if plan is None:
        raise FileNotFoundError("No active plan to scaffold a spec for")
    spec_dir = plan.dir / "spec"
    spec_dir.mkdir(exist_ok=True)
    for name, content in _SPEC_FILES.items():
        f = spec_dir / name
        if not f.exists():
            f.write_text(content, encoding="utf-8")
    return plan


def close_plan(root: Path, confirm: bool = False) -> Plan:
    plan = active_plan(root)
    if plan is None:
        raise FileNotFoundError("No active plan to close")
    if confirm:
        dest = root / ARCHIVE_DIR / plan.id
        dest.parent.mkdir(parents=True, exist_ok=True)
        plan.dir.rename(dest)
        state = _read_state(root)
        state.pop("active_plan", None)
        _write_state(root, state)
    return plan
