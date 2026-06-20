"""Warn when a doc's `inject:` target names no agent/lane, or an agent that can't
receive it.

`inject: <agent>` / `inject: <lane>` routes a doc only to matching consumers. A typo
(`inject: reviewr`) or a target agent that lacks a `<!-- DOCS -->` marker would silently
reach nobody - this surfaces it. `inject: all` is always fine.
"""

from __future__ import annotations

from flex_kit.checks import Check, Ctx, Finding
from flex_kit.docs import ALL, DOCS_MARKER


def _run(ctx: Ctx) -> list[Finding]:
    agents = {a.id: a for a in ctx.agents}
    lanes = {a.frontmatter.get("lane", "") for a in ctx.agents} - {""}
    findings: list[Finding] = []
    for d in ctx.docs:
        if ALL in d.targets:
            continue
        for t in sorted(d.targets):
            if t in lanes:
                continue
            if t in agents:
                if DOCS_MARKER not in agents[t].body:
                    findings.append(
                        Finding(
                            "warn",
                            f"doc {d.rel}: target '{t}' is an agent with no "
                            f"`<!-- DOCS -->` marker - the doc won't reach it",
                        )
                    )
                continue
            findings.append(
                Finding("warn", f"doc {d.rel}: inject target '{t}' matches no agent or lane")
            )
    return findings


CHECK = Check("doc-targets", _run)
