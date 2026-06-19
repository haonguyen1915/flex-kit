"""flex-kit CLI (Typer): gen | doctor."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer

from flex_kit import codex_review as codex_review_mod
from flex_kit import hooks as hooks_mod
from flex_kit import plan as plan_mod
from flex_kit import ui
from flex_kit.add import add as run_add
from flex_kit.add import add_all as run_add_all
from flex_kit.add import list_packs
from flex_kit.add import remove as run_remove
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
    ui.success(f"created {result.flexkit_dir}")
    if result.gen is not None:
        g = result.gen
        ui.detail(
            "gen:",
            f"{g.skills} skills + {g.agents} agents + {g.commands} commands "
            f"-> [{', '.join(g.hosts)}]",
        )
    ui.hint("Edit .flexkit/skills/ then run `flex-kit gen`.")


@app.command()
def add(
    pack: str = typer.Argument(None, help="Pack to add. Omit to list available packs."),
    project: Path = typer.Option(Path.cwd, "--project", "-p", help="Project root."),
    force: bool = typer.Option(False, "--force", help="Overwrite skills/agents of the same id."),
    no_gen: bool = typer.Option(False, "--no-gen", help="Copy only, skip gen."),
    all_packs: bool = typer.Option(False, "--all", help="Add every bundled pack, then gen once."),
) -> None:
    """Add a bundled pack's skills/agents into .flexkit/, then gen."""
    if all_packs:
        result = run_add_all(project.resolve(), force=force, run_gen=not no_gen)
        label = "--all"
    elif not pack:
        ui.header("Available packs")
        for p in list_packs():
            ui.detail("·", p)
        ui.hint("Add one with `flex-kit add <pack>`, or all with `flex-kit add --all`.")
        return
    else:
        result = run_add(project.resolve(), pack, force=force, run_gen=not no_gen)
        label = pack
    ui.success(f"add {label}: {len(result.added)} added, {len(result.skipped)} skipped")
    for rel in result.added:
        ui.detail("+", rel)
    for rel in result.skipped:
        ui.detail("=", f"{rel} (exists - use --force)")
    if result.gen is not None:
        ui.detail("gen:", f"{result.gen.skills} skills + {result.gen.agents} agents")


@app.command()
def remove(
    pack: str = typer.Argument(..., help="Pack to remove from .flexkit/."),
    project: Path = typer.Option(Path.cwd, "--project", "-p"),
    no_gen: bool = typer.Option(False, "--no-gen", help="Delete only, skip gen."),
) -> None:
    """Remove a pack's skills/agents from .flexkit/ (the un-add), then gen."""
    result = run_remove(project.resolve(), pack, run_gen=not no_gen)
    ui.success(
        f"remove {pack}: {len(result.removed)} removed, {len(result.missing)} not present"
    )
    for rel in result.removed:
        ui.detail("-", rel)
    if result.gen is not None:
        ui.detail("gen:", f"{result.gen.skills} skills + {result.gen.agents} agents")


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
    ui.success(
        f"gen{tag}: {result.skills} skills + {result.agents} agents "
        f"+ {result.commands} commands -> [{', '.join(result.hosts)}]"
    )
    for host, n in result.files_per_host.items():
        ui.detail(f"{host}:", f"{n} files")


@app.command("codex-review")
def codex_review(
    target: str = typer.Argument(None, help="A file path (with --type file)."),
    type_: str = typer.Option("plan", "--type", help="plan | diff | file."),
    model: str = typer.Option(codex_review_mod.DEFAULT_MODEL, "--model"),
    effort: str = typer.Option(codex_review_mod.DEFAULT_EFFORT, "--effort"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print the command, don't run codex."),
    project: Path = typer.Option(Path.cwd, "--project", "-p"),
) -> None:
    """Send the active plan, the diff, or a file to Codex (codex exec) for review."""
    res = codex_review_mod.codex_review(
        project.resolve(), kind=type_, target=target, model=model, effort=effort, dry_run=dry_run
    )
    if dry_run:
        ui.info(f"[dry-run] {' '.join(res.command)}  ->  {res.report_path}")
    else:
        ui.success(f"codex review ({res.model}) saved -> {res.report_path}")


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
            ui.success(res.id)
            continue
        for f in res.findings:
            if f.level == "error":
                errors += 1
                ui.error(f"{res.id}: {f.msg}")
            else:
                warns += 1
                ui.warn(f"{res.id}: {f.msg}")
    ui.blank()
    summary = f"{errors} error(s), {warns} warning(s)"
    (ui.error if errors else ui.success)(summary)
    raise typer.Exit(1 if errors else 0)


@app.command()
def plan(
    title: str = typer.Argument(..., help="What the plan delivers."),
    mode: str = typer.Option("build", "--mode", help="patch | build | design."),
    project: Path = typer.Option(Path.cwd, "--project", "-p"),
) -> None:
    """Create a tracked plan under plans/active/ and make it the active plan."""
    try:
        p = plan_mod.create_plan(project.resolve(), title, mode=mode)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e
    ui.success(f"created plan {p.id}  (mode: {p.mode})")
    ui.hint(f"edit {p.dir}/plan.md, then `flex-kit status`")


@app.command()
def status(project: Path = typer.Option(Path.cwd, "--project", "-p")) -> None:
    """Show the active plan and step progress."""
    p = plan_mod.active_plan(project.resolve())
    if p is None:
        ui.info('No active plan. Create one with `flex-kit plan "<task>"`.')
        return
    v = p.mode_verdict
    mode_str = p.mode if v.effective == v.declared else f"{v.declared} -> {v.effective}"
    ui.header(f"plan {p.id}  (mode: {mode_str}, status: {p.status})")
    if v.reason:
        ui.warn(f"scope grew ({v.reason}) - consider declaring `{v.effective}` mode")
    ui.detail("steps:", f"{p.done_count}/{len(p.steps)} done")
    nxt = p.next_step
    ui.detail("next:", nxt.text if nxt else "all steps done - `flex-kit close`")


@app.command("next-step")
def next_step(project: Path = typer.Option(Path.cwd, "--project", "-p")) -> None:
    """Print the next incomplete step of the active plan."""
    # Plain stdout: this line is read raw by the slash command / scripts.
    p = plan_mod.active_plan(project.resolve())
    nxt = p.next_step if p else None
    typer.echo(nxt.text if nxt else "(no next step)")


@app.command()
def spec(project: Path = typer.Option(Path.cwd, "--project", "-p")) -> None:
    """Scaffold spec/{proposal,design,tasks}.md for the active plan (design-first)."""
    p = plan_mod.scaffold_spec(project.resolve())
    ui.success(f"scaffolded spec/ for plan {p.id}")
    ui.hint(f"fill {p.dir}/spec/proposal.md -> design.md -> tasks.md")


@app.command()
def close(
    confirm: bool = typer.Option(False, "--confirm", help="Archive the plan."),
    project: Path = typer.Option(Path.cwd, "--project", "-p"),
) -> None:
    """Archive the active plan (use --confirm to move it to plans/archive/)."""
    p = plan_mod.close_plan(project.resolve(), confirm=confirm)
    if confirm:
        ui.success(f"closed plan {p.id} -> {plan_mod.ARCHIVE_DIR}/{p.id}")
    else:
        left = len(p.steps) - p.done_count
        ui.warn(f"plan {p.id}: {left} step(s) incomplete. Re-run with --confirm to archive.")


@app.command()
def hook(
    event: str = typer.Argument(..., help="session-start | pre-tool"),
    project: Path = typer.Option(Path.cwd, "--project", "-p"),
) -> None:
    """Runtime hook entrypoint, invoked by the host via .claude/settings.json."""
    # Plain stdout / JSON: this is consumed by the host, never styled.
    root = project.resolve()
    payload: dict = {}
    if not sys.stdin.isatty():
        raw = sys.stdin.read()
        if raw.strip():
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {}

    if event == "session-start":
        typer.echo(hooks_mod.session_start(root))
    elif event == "user-prompt":
        line = hooks_mod.user_prompt(root)
        if line:
            typer.echo(line)
    elif event == "pre-tool":
        reason = hooks_mod.pre_tool_decision(payload)
        if reason:
            typer.echo(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": reason,
                        }
                    }
                )
            )


def _main() -> None:
    app()


if __name__ == "__main__":
    _main()
