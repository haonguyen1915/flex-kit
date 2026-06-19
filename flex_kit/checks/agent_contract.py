"""Agent frontmatter convention: a `model` and a `lane` (build|review).

`skill_contract` already enforces the kebab name + description for agents; this adds the
agent-only fields gen tolerates (claude passes `model` through, codex defaults it, and no
host reads `lane`) but the kit's routing convention expects. A hand-authored agent that
drops them is flagged as drift, not silently diverged. Mechanical only - the prose
contract (markers, gate, handoff sections) is the `flex-agent-creator` command's job.
"""

from __future__ import annotations

from flex_kit.checks import Check, Ctx, Finding

_LANES = {"build", "review"}


def _run(ctx: Ctx) -> list[Finding]:
    findings: list[Finding] = []
    for a in ctx.agents:
        fm = a.frontmatter
        if not fm.get("model"):
            findings.append(Finding("warn", f"agent {a.id}: frontmatter missing `model`"))
        lane = fm.get("lane", "")
        if not lane:
            findings.append(Finding("warn", f"agent {a.id}: frontmatter missing `lane`"))
        elif lane not in _LANES:
            findings.append(
                Finding("warn", f"agent {a.id}: lane '{lane}' not one of build/review")
            )
    return findings


CHECK = Check("agent-contract", _run)
