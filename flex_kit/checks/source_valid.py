"""Source skills/agents have a name matching their id and a non-empty description."""

from __future__ import annotations

from flex_kit.checks import Check, Ctx, Finding


def _check_item(kind: str, item_id: str, fm: dict, findings: list[Finding]) -> None:
    name = fm.get("name")
    if not name:
        findings.append(Finding("error", f"{kind} {item_id}: frontmatter missing `name`"))
    elif name != item_id:
        findings.append(
            Finding("error", f'{kind} {item_id}: frontmatter name "{name}" != "{item_id}"')
        )
    if not fm.get("description", "").strip():
        findings.append(Finding("error", f"{kind} {item_id}: frontmatter missing `description`"))


def _run(ctx: Ctx) -> list[Finding]:
    findings: list[Finding] = []
    for s in ctx.skills:
        _check_item("skill", s.id, s.frontmatter, findings)
    for a in ctx.agents:
        _check_item("agent", a.id, a.frontmatter, findings)
    return findings


CHECK = Check("source-valid", _run)
