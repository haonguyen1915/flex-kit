"""flex-kit CLI (Typer): gen | doctor."""

from __future__ import annotations

from pathlib import Path

import typer

from flex_kit.add import add as run_add
from flex_kit.add import list_packs
from flex_kit.doctor import doctor as run_doctor
from flex_kit.gen import gen as run_gen
from flex_kit.init import init as run_init

app = typer.Typer(
    name="flex-kit",
    help="Single-source skill kit for Claude Code + Codex.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command()
def init(
    project: Path = typer.Option(Path.cwd, "--project", "-p", help="Project root."),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing .flexkit/."),
    no_gen: bool = typer.Option(False, "--no-gen", help="Scaffold only, skip gen."),
) -> None:
    """Scaffold .flexkit/ from the starter template, then gen the host surfaces."""
    root = project.resolve()
    result = run_init(root, force=force, run_gen=not no_gen)
    typer.echo(f"flex-kit init: created {result.flexkit_dir}")
    if result.gen is not None:
        g = result.gen
        typer.echo(
            f"  gen: {g.skills} skills + {g.agents} agents -> [{', '.join(g.hosts)}]"
        )
    typer.echo("Edit .flexkit/skills/ then run `flex-kit gen`.")


@app.command()
def add(
    pack: str = typer.Argument(None, help="Pack to add. Omit to list available packs."),
    project: Path = typer.Option(Path.cwd, "--project", "-p", help="Project root."),
    force: bool = typer.Option(False, "--force", help="Overwrite skills/agents of the same id."),
    no_gen: bool = typer.Option(False, "--no-gen", help="Copy only, skip gen."),
) -> None:
    """Add a bundled pack's skills/agents into .flexkit/, then gen."""
    if not pack:
        typer.echo("Available packs:")
        for p in list_packs():
            typer.echo(f"  {p}")
        return
    result = run_add(project.resolve(), pack, force=force, run_gen=not no_gen)
    typer.echo(f"flex-kit add {pack}: {len(result.added)} added, {len(result.skipped)} skipped")
    for rel in result.added:
        typer.echo(f"  + {rel}")
    for rel in result.skipped:
        typer.echo(f"  = {rel} (exists - use --force)")
    if result.gen is not None:
        typer.echo(f"  gen: {result.gen.skills} skills + {result.gen.agents} agents")


@app.command()
def gen(
    project: Path = typer.Option(Path.cwd, "--project", "-p", help="Project root."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Report without writing."),
    out: Path | None = typer.Option(None, "--out", help="Write surfaces under this root."),
) -> None:
    """Generate .claude/ and .codex/ skill surfaces from .flexkit/skills/."""
    root = project.resolve()
    result = run_gen(root, dry_run=dry_run, out_root=out.resolve() if out else None)
    tag = " (dry-run)" if dry_run else ""
    typer.echo(
        f"flex-kit gen{tag}: {result.skills} skills + {result.agents} agents "
        f"-> [{', '.join(result.hosts)}]"
    )
    for host, n in result.files_per_host.items():
        typer.echo(f"  {host}: {n} files")


@app.command()
def doctor(
    project: Path = typer.Option(Path.cwd, "--project", "-p", help="Project root."),
) -> None:
    """Validate source + that generated surfaces are in sync."""
    root = project.resolve()
    results = run_doctor(root)
    errors = warns = 0
    for res in results:
        if not res.findings:
            typer.echo(f"✓ {res.id}")
            continue
        for f in res.findings:
            if f.level == "error":
                errors += 1
                mark = "✗"
            else:
                warns += 1
                mark = "!"
            typer.echo(f"{mark} {res.id}: {f.msg}")
    typer.echo(f"\n{errors} error(s), {warns} warning(s)")
    raise typer.Exit(1 if errors else 0)


def _main() -> None:
    app()


if __name__ == "__main__":
    _main()
