"""Quality contract for skill/agent frontmatter: kebab name + sane description.

The description drives implicit triggering on both hosts (Codex shows it; Claude
matches on it), so it must be present, non-trivial, and not bloated. Prep-kit's
body conventions (`## Gotchas`, a `triggers` array) are its own opinion and do
not fit flex-kit's name+description model, so they are intentionally not enforced.
"""

from __future__ import annotations

import re

from flex_kit.checks import Check, Ctx, Finding

_KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_MIN_DESC = 20
_MAX_DESC = 1024


def _check_item(kind: str, item_id: str, fm: dict, findings: list[Finding]) -> None:
    name = fm.get("name", "")
    if name and not _KEBAB.match(name):
        findings.append(Finding("error", f"{kind} {item_id}: name '{name}' is not kebab-case"))

    desc = fm.get("description", "").strip()
    if desc and len(desc) < _MIN_DESC:
        findings.append(
            Finding("error", f"{kind} {item_id}: description too short ({len(desc)} < {_MIN_DESC})")
        )
    if len(desc) > _MAX_DESC:
        findings.append(
            Finding(
                "warn",
                f"{kind} {item_id}: description is long ({len(desc)} > {_MAX_DESC} chars) - "
                "keep it trigger-focused",
            )
        )


def _run(ctx: Ctx) -> list[Finding]:
    findings: list[Finding] = []
    for s in ctx.skills:
        _check_item("skill", s.id, s.frontmatter, findings)
    for a in ctx.agents:
        _check_item("agent", a.id, a.frontmatter, findings)
    return findings


CHECK = Check("skill-contract", _run)
