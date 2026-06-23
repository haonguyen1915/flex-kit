"""The host surfaces must equal what `gen` would produce right now.

A mismatch means someone hand-edited a generated file or forgot to re-run gen after
editing the source - the drift this kit prevents. A file gen produced before but no
longer produces (an orphan from a rename/removal) is also flagged. Files gen never
produced - hand-authored, other tools - are left alone.
"""

from __future__ import annotations

from flex_kit.build import emit_for_host
from flex_kit.checks import Check, Ctx, Finding
from flex_kit.record import read_record


def _run(ctx: Ctx) -> list[Finding]:
    findings: list[Finding] = []
    expected: set[str] = set()

    for host_name in ctx.config.hosts:
        host = ctx.hosts[host_name]
        for f in emit_for_host(host, ctx.skills, ctx.agents, ctx.commands, ctx.docs, ctx.config):
            expected.add(f.path)
            dest = ctx.project_root / f.path
            if not dest.exists():
                findings.append(Finding("error", f"{host_name}: {f.path} missing - run gen"))
            elif f.content is not None:
                if dest.read_text(encoding="utf-8") != f.content:
                    findings.append(
                        Finding(
                            "error",
                            f"{host_name}: {f.path} drifted from source - run gen "
                            "(do not hand-edit generated)",
                        )
                    )
            elif f.copy_from is not None and dest.read_bytes() != f.copy_from.read_bytes():
                findings.append(Finding("error", f"{host_name}: {f.path} out of sync - run gen"))

    # Orphans: files gen produced last run but no longer produces, still on disk.
    for rel in sorted(read_record(ctx.project_root) - expected):
        if (ctx.project_root / rel).is_file():
            findings.append(Finding("error", f"{rel} is stray (gen would remove it) - run gen"))
    return findings


CHECK = Check("generated-in-sync", _run)
