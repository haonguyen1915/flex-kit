"""The host surfaces must equal what ``gen`` would produce right now.

A mismatch means someone hand-edited a generated file or forgot to re-run gen
after editing the source - the drift this kit exists to prevent.
"""

from __future__ import annotations

from flex_kit.checks import Check, Ctx, Finding
from flex_kit.render import render_skill_content


def _run(ctx: Ctx) -> list[Finding]:
    findings: list[Finding] = []
    for host_name in ctx.config.hosts:
        host = ctx.hosts[host_name]
        for skill in ctx.skills:
            dest_dir = ctx.project_root / host.BASE_DIR / skill.id
            skill_file = dest_dir / "SKILL.md"
            if not skill_file.exists():
                findings.append(Finding("error", f"{host_name}/{skill.id}: missing - run gen"))
                continue
            if skill_file.read_text(encoding="utf-8") != render_skill_content(host, skill):
                findings.append(
                    Finding(
                        "error",
                        f"{host_name}/{skill.id}: SKILL.md drifted from source - run gen "
                        "(do not hand-edit generated)",
                    )
                )
            for rel in skill.references:
                dest = dest_dir / rel
                if not dest.exists() or dest.read_bytes() != (skill.dir / rel).read_bytes():
                    findings.append(
                        Finding("error", f"{host_name}/{skill.id}: reference {rel} out of sync - run gen")
                    )
    return findings


CHECK = Check("generated-in-sync", _run)
