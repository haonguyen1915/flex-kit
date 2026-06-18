"""Delivery modes + escalation.

A plan declares a mode (`patch` / `build` / `design`); the *effective* mode is
computed from the plan's actual size. A `patch` that grows past its budget
escalates to `build`, and a `build` past its budget escalates to `design` - so a
"small fix" can't silently balloon without surfacing the change.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

MODES = ("patch", "build", "design")


class _Budget(TypedDict):
    max_steps: int
    max_files: int | None  # None = unbounded


# Escalation budgets. The top mode (design) has no cap, so it is absent here.
_BUDGET: dict[str, _Budget] = {
    "patch": {"max_steps": 3, "max_files": 2},
    "build": {"max_steps": 15, "max_files": None},
}


@dataclass
class ModeVerdict:
    declared: str
    effective: str
    reason: str | None  # why it escalated, if it did


def is_valid(mode: str) -> bool:
    return mode in MODES


def _exceeds(mode: str, n_steps: int, n_files: int) -> str | None:
    budget = _BUDGET[mode]
    if n_steps > budget["max_steps"]:
        return f"steps={n_steps} > {budget['max_steps']}"
    if budget["max_files"] is not None and n_files > budget["max_files"]:
        return f"files={n_files} > {budget['max_files']}"
    return None


def effective_mode(declared: str, n_steps: int, n_files: int = 0) -> ModeVerdict:
    effective, reason = declared, None
    if effective == "patch" and (r := _exceeds("patch", n_steps, n_files)):
        effective, reason = "build", r
    if effective == "build" and (r := _exceeds("build", n_steps, n_files)):
        effective, reason = "design", r
    return ModeVerdict(declared=declared, effective=effective, reason=reason)
