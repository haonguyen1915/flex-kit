"""The host surfaces must equal what `gen` would produce right now.

A mismatch means someone hand-edited a generated file, added a stray file, or
forgot to re-run gen after editing the source - the drift this kit prevents.
"""

from __future__ import annotations

from flex_kit.build import emit_for_host
from flex_kit.checks import Check, Ctx, Finding


def _run(ctx: Ctx) -> list[Finding]:
    findings: list[Finding] = []
    for host_name in ctx.config.hosts:
        host = ctx.hosts[host_name]
        expected: set[str] = set()

        for f in emit_for_host(host, ctx.skills, ctx.agents, ctx.commands):
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

        # Stray files: anything in the host's owned roots that gen would not write.
        roots = [getattr(host, a, None) for a in ("SKILLS_DIR", "AGENTS_DIR", "COMMANDS_DIR")]
        for base in filter(None, roots):
            root = ctx.project_root / base
            if not root.exists():
                continue
            for p in root.rglob("*"):
                if p.is_file():
                    rel = p.relative_to(ctx.project_root).as_posix()
                    if rel not in expected:
                        findings.append(
                            Finding("error", f"{host_name}: {rel} is stray (not produced by gen)")
                        )
    return findings


CHECK = Check("generated-in-sync", _run)
