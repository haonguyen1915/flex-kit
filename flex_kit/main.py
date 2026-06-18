"""flex-kit CLI (Typer): gen | doctor."""

from __future__ import annotations

from pathlib import Path

import typer

from flex_kit.doctor import doctor as run_doctor
from flex_kit.gen import gen as run_gen

app = typer.Typer(
    name="flex-kit",
    help="Single-source skill kit for Claude Code + Codex.",
    no_args_is_help=True,
    add_completion=False,
)


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
