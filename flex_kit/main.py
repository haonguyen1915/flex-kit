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
from flex_kit.add import add_packs as run_add_packs
from flex_kit.add import installed_packs, list_packs
from flex_kit.add import remove as run_remove
from flex_kit.config import load_config
from flex_kit.docs import scaffold_docs
from flex_kit.doctor import doctor as run_doctor
from flex_kit.gen import gen as run_gen
from flex_kit.init import init as run_init
from flex_kit.init import update as run_update

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
    update: bool = typer.Option(
        False,
        "--update",
        help="Refresh base agents/skills/commands to the installed version (keeps your own).",
    ),
    also_gen: bool = typer.Option(
        False, "--gen", help="Also build host surfaces (.claude/, .agents/) after scaffolding."
    ),
) -> None:
    """Scaffold .flexkit/ from the starter template - source only, no gen.

    init does one job: set up the source. It generates nothing by default; run
    `flex-kit gen` (or pass --gen) to build the host surfaces when you're ready.

    --update refreshes only the flex-kit base items (its own agents/skills/commands) to
    the installed version, overwriting them - everything you added stays untouched.
    """
    root = project.resolve()
    if update:
        if force:
            ui.error("--update and --force cannot be combined.")
            raise typer.Exit(1)
        try:
            up = run_update(root, run_gen=also_gen)
        except FileNotFoundError as e:
            ui.error(str(e))
            raise typer.Exit(1) from None
        ui.success(f"updated {len(up.updated)} base item(s) to this version")
        for rel in up.updated:
            ui.detail("~", rel)
        if up.gen is not None:
            g = up.gen
            ui.detail("gen:", f"{g.skills} skills + {g.agents} agents + {g.commands} commands")
        elif up.updated:
            ui.hint("Run `flex-kit gen` to rebuild host surfaces.")
        return
    flexkit = root / ".flexkit"
    # --force wipes .flexkit/ wholesale; confirm first so a stray --force can't silently
    # destroy uncommitted source. Non-interactive (scripted) runs proceed with a warning.
    if force and flexkit.exists() and any(flexkit.iterdir()):
        ui.warn(f"--force deletes {flexkit} and everything under it, then re-scaffolds.")
        if sys.stdin.isatty() and sys.stdout.isatty() and not typer.confirm("Continue?"):
            ui.hint("Aborted - nothing changed.")
            raise typer.Exit(1)
    result = run_init(root, force=force, run_gen=also_gen)
    ui.success(f"created {result.flexkit_dir}")
    if result.gen is not None:
        g = result.gen
        ui.detail(
            "gen:",
            f"{g.skills} skills + {g.agents} agents + {g.commands} commands "
            f"-> [{', '.join(g.hosts)}]",
        )
        ui.hint("Edit .flexkit/skills/ then run `flex-kit gen`.")
    else:
        ui.hint("Edit .flexkit/, then run `flex-kit gen` to build host surfaces.")


def _select_packs(root: Path) -> list[str] | None:
    """Interactive multi-select of packs. Returns the chosen packs, [] if the user
    picked none / cancelled, or None when there is no interactive terminal (the caller
    then falls back to a plain listing)."""
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return None
    try:
        import questionary
    except ModuleNotFoundError:
        return None
    packs = list_packs()
    if not packs:
        return []
    installed = installed_packs(root)
    choices = [
        questionary.Choice(title=f"{p}  (added)" if p in installed else p, value=p)
        for p in packs
    ]
    picked = questionary.checkbox(
        "Select packs to add (space toggles, enter confirms):", choices=choices
    ).ask()
    return picked or []


@app.command()
def add(
    pack: str = typer.Argument(None, help="Pack to add. Omit for an interactive picker."),
    project: Path = typer.Option(Path.cwd, "--project", "-p", help="Project root."),
    force: bool = typer.Option(False, "--force", help="Overwrite skills/agents of the same id."),
    also_gen: bool = typer.Option(
        False, "--gen", help="Also build host surfaces after copying into .flexkit/."
    ),
    all_packs: bool = typer.Option(False, "--all", help="Add every bundled pack."),
) -> None:
    """Add bundled packs' skills/agents into .flexkit/ (source only, no gen).

    With no pack argument, opens an interactive multi-select (one or many packs);
    falls back to a plain listing when stdout is not a terminal. Pass --gen to build
    the host surfaces in the same step, or run `flex-kit gen` afterwards.
    """
    if all_packs:
        result = run_add_all(project.resolve(), force=force, run_gen=also_gen)
        label = "--all"
    elif not pack:
        root = project.resolve()
        selected = _select_packs(root)
        if selected is None:  # not a TTY -> just list what's available
            ui.header("Available packs")
            for p in list_packs():
                ui.detail("·", p)
            ui.hint("Add with `flex-kit add <pack>`, `--all`, or run `flex-kit add` to pick.")
            return
        if not selected:
            ui.hint("No packs selected.")
            return
        result = run_add_packs(root, selected, force=force, run_gen=also_gen)
        label = ", ".join(selected)
    else:
        result = run_add(project.resolve(), pack, force=force, run_gen=also_gen)
        label = pack
    ui.success(f"add {label}: {len(result.added)} added, {len(result.skipped)} skipped")
    for rel in result.added:
        ui.detail("+", rel)
    for rel in result.skipped:
        ui.detail("=", f"{rel} (exists - use --force)")
    if result.gen is not None:
        ui.detail("gen:", f"{result.gen.skills} skills + {result.gen.agents} agents")
    elif result.added:
        ui.hint("Run `flex-kit gen` to build host surfaces.")


@app.command()
def remove(
    pack: str = typer.Argument(..., help="Pack to remove from .flexkit/."),
    project: Path = typer.Option(Path.cwd, "--project", "-p"),
    also_gen: bool = typer.Option(
        False, "--gen", help="Also rebuild host surfaces after removing from .flexkit/."
    ),
) -> None:
    """Remove a pack's skills/agents from .flexkit/ (the un-add), source only - no gen."""
    result = run_remove(project.resolve(), pack, run_gen=also_gen)
    ui.success(
        f"remove {pack}: {len(result.removed)} removed, {len(result.missing)} not present"
    )
    for rel in result.removed:
        ui.detail("-", rel)
    if result.gen is not None:
        ui.detail("gen:", f"{result.gen.skills} skills + {result.gen.agents} agents")
    elif result.removed:
        ui.hint("Run `flex-kit gen` to clean the host surfaces.")


@app.command("init-docs")
def init_docs(
    project: Path = typer.Option(Path.cwd, "--project", "-p", help="Project root."),
    force: bool = typer.Option(
        False, "--force", help="Merge missing skeleton files into an existing docs/."
    ),
) -> None:
    """Scaffold a docs/ skeleton (architecture, conventions, domain, adr) for agents."""
    root = project.resolve()
    try:
        docs_dir = load_config(root).docs_dir
    except FileNotFoundError:
        docs_dir = "docs"
    result = scaffold_docs(root, docs_dir, force=force)
    if result.bailed:
        ui.warn(f"{result.docs_dir}/ already has {result.existing_count} file(s) - skipped.")
        ui.hint("Add the missing scaffold files anyway with `flex-kit init-docs --force`.")
        return
    tag = " (force)" if force else ""
    ui.success(f"init-docs{tag}: {len(result.created)} created, {len(result.skipped)} skipped")
    for rel in result.created:
        ui.detail("+", rel)
    for rel in result.skipped:
        ui.detail("=", f"{rel} (exists)")
    ui.hint("Fill these in, then `flex-kit gen` to index them into the agents.")


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
def statusline(project: Path = typer.Option(Path.cwd, "--project", "-p")) -> None:
    """Print the status for the Claude Code status bar (wired in settings.json)."""
    # Claude pipes session JSON on stdin (model, workspace, cost, context_window).
    root = project.resolve()
    payload: dict = {}
    if not sys.stdin.isatty():
        raw = sys.stdin.read()
        if raw.strip():
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {}
    cwd = (payload.get("workspace") or {}).get("current_dir") or payload.get("cwd")
    if cwd:
        root = Path(cwd)
    # Plain print (not typer.echo): keep the ANSI colors the host renders in the bar.
    print(hooks_mod.status_line(root, payload))


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
    elif event == "subagent-start":
        hooks_mod.subagent_start(root, payload)
    elif event == "subagent-stop":
        hooks_mod.subagent_stop(root, payload)
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
