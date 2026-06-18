"""Cross-model review: ask the Codex CLI for an independent second opinion.

Shells out to `codex exec` (Codex's non-interactive mode) with the active plan, the
git diff, or a file as the prompt, captures the output as a report, and returns its
path. This is the only flow that asks a *different* model to review; every other flow
uses the host's own `reviewer` subagent. Requires the `codex` CLI installed + logged
in.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from flex_kit import plan as plan_mod

DEFAULT_MODEL = "gpt-5.5"
DEFAULT_EFFORT = "high"

_INSTRUCTION = (
    "You are an independent reviewer from a different model. Review the following for "
    "correctness, risk, and convention. List findings by severity (critical / high / "
    "medium / low) with a one-line fix recommendation each. Be concise."
)


def _git_diff(root: Path) -> str:
    cmd = ["git", "-C", str(root), "diff"]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout


def build_prompt(root: Path, kind: str, target: str | None) -> str:
    if kind == "diff":
        return f"{_INSTRUCTION}\n\n```diff\n{_git_diff(root)}\n```"
    if kind == "file":
        if not target:
            raise ValueError("--type file needs a path target")
        return f"{_INSTRUCTION}\n\nFile `{target}`:\n\n```\n{(root / target).read_text()}\n```"
    # plan (default)
    p = plan_mod.active_plan(root)
    if p is None:
        raise FileNotFoundError("No active plan - pass --type diff, or a file with --type file")
    return f"{_INSTRUCTION}\n\nPlan:\n\n{(p.dir / 'plan.md').read_text()}"


@dataclass
class CodexReviewResult:
    report_path: Path
    model: str
    command: list[str]


def codex_review(
    root: Path,
    kind: str = "plan",
    target: str | None = None,
    model: str = DEFAULT_MODEL,
    effort: str = DEFAULT_EFFORT,
    dry_run: bool = False,
) -> CodexReviewResult:
    prompt = build_prompt(root, kind, target)
    p = plan_mod.active_plan(root)
    report_dir = (p.dir / "reports") if p else (root / "reports")
    report = report_dir / "codex-review.md"
    cmd = ["codex", "exec", "-m", model, "-c", f'reasoning.effort="{effort}"', "--full-auto", "-"]

    if dry_run:
        return CodexReviewResult(report_path=report, model=model, command=cmd)

    try:
        out = subprocess.run(cmd, input=prompt, text=True, capture_output=True, check=True)
    except FileNotFoundError as e:
        raise FileNotFoundError("`codex` CLI not found - install Codex and log in") from e
    report_dir.mkdir(parents=True, exist_ok=True)
    report.write_text(out.stdout or "(codex produced no output)\n", encoding="utf-8")
    return CodexReviewResult(report_path=report, model=model, command=cmd)
