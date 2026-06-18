"""Source skills have a name matching their directory and a non-empty description."""

from __future__ import annotations

from flex_kit.checks import Check, Ctx, Finding


def _run(ctx: Ctx) -> list[Finding]:
    findings: list[Finding] = []
    for s in ctx.skills:
        name = s.frontmatter.get("name")
        if not name:
            findings.append(Finding("error", f"{s.id}: frontmatter missing `name`"))
        elif name != s.id:
            findings.append(
                Finding("error", f'{s.id}: frontmatter name "{name}" != directory "{s.id}"')
            )
        if not s.frontmatter.get("description", "").strip():
            findings.append(Finding("error", f"{s.id}: frontmatter missing `description`"))
    return findings


CHECK = Check("source-valid", _run)
