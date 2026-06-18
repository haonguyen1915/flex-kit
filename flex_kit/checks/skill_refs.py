"""Markdown links in a skill body that point at local files must resolve."""

from __future__ import annotations

import re

from flex_kit.checks import Check, Ctx, Finding

_LINK = re.compile(r"\]\(([^)]+\.md)\)")
_EXTERNAL = re.compile(r"^[a-z]+://", re.IGNORECASE)


def _run(ctx: Ctx) -> list[Finding]:
    findings: list[Finding] = []
    for s in ctx.skills:
        for target in _LINK.findall(s.body):
            if _EXTERNAL.match(target) or target.startswith("#"):
                continue
            clean = target.removeprefix("./").split("#")[0]
            if not (s.dir / clean).exists():
                findings.append(Finding("error", f"{s.id}: broken reference -> {target}"))
    return findings


CHECK = Check("skill-refs", _run)
