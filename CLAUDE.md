# CLAUDE.md

Operating notes for working on the **flex-kit** codebase. (For end-user docs see
`README.md`; for the design rationale see `docs/prepkit-concept-spec.md`.)

## What flex-kit is

A single-source kit for AI-agent **skills + agents + commands**: author once in a
project's `.flexkit/`, generate native surfaces for **Claude Code** and **Codex**,
validate they never drift - plus a full agent **operating system** (plans, modes,
hooks, autonomous delivery) on top. It is a faithful clone of prep-kit's operating
model with a cleaner neutral-source design; it omits prep-kit's persona,
model-routing, semantic-memory layers and ships no domain content.

## The model

```
.flexkit/skills/<id>/SKILL.md   ─gen─▶ .claude/skills/<id>/  +  .agents/skills/<id>/   (Codex-native)
.flexkit/agents/<id>.md         ─gen─▶ .claude/agents/<id>.md  +  .codex/agents/<id>.toml
```

- **Source ≠ host.** `.flexkit/` is the only source; every host dir is generated
  output. No host is privileged (this is the key improvement over prep-kit, which
  authors in `.claude/skills/`).
- **Never hand-edit generated dirs.** `doctor`'s `generated-in-sync` check
  re-renders and compares, and flags hand-edited files + orphans. `gen` overwrites
  its own output and removes only files it previously produced (tracked in
  `.flexkit/.generated.json`) - **files it never generated** (hand-authored skills,
  another tool's output) in the host dirs are **left untouched**, not wiped.
- **Codex skills go to `.agents/skills/`** (Codex natively scans it), NOT
  `.codex/skills/`. `.codex/` holds only agent `.toml`.
- **Convention-discovery, not a registry.** Skills/agents are discovered by scanning
  `.flexkit/`; per-item metadata lives in each item's frontmatter (e.g. `model`,
  `lane`), not a separate manifest.

## Module map (`flex_kit/`)

| File | Role |
|---|---|
| `main.py` | Typer CLI: init / init-docs / add / remove / gen / codex-review / doctor / plan / status / next-step / spec / close / statusline / hook |
| `config.py` | resolve config: global `~/.flex-kit/config.json` overlaid by project `.flexkit/config.json` (hosts, skillsDir, agentsDir, commandsDir, docsDir, notify, codexModel, codexEffort; legacy `flexkit.config.json` still read). `load_config` requires a project; `resolve_config` tolerates its absence (global+defaults) |
| `skills.py` / `agents.py` | discover + parse source skills / agents |
| `commands.py` | discover + parse source commands (Claude slash-command surface) |
| `docs.py` | discover `inject:`-tagged project docs + inject their index at `<!-- DOCS -->`, routed per consumer (`all` / agent id / lane); scaffold the docs/ skeleton |
| `frontmatter.py` | parse + shared transforms (em-dash normalize, strip markup, wrap) |
| `emit.py` | `OutFile` - the unit of host output |
| `build.py` | `emit_for_host(host, skills, agents, commands, docs)` - shared by gen + the sync check |
| `hosts/{claude,codex}.py` | host adapters: `emit_skill` / `emit_agent` / `emit_command` → `list[OutFile]` |
| `gen.py` / `init.py` / `add.py` | the write commands (gen tracks output in `record.py`) |
| `record.py` | the set of files gen produced (`.flexkit/.generated.json`); lets gen clean orphans without wiping unmanaged files. `init --force` carries it across the wipe so the next gen can still prune |
| `catalog.py` | the ids flex-kit can generate (bundled packs + base template); gen's safety net to recognise its own orphaned output even when the record was lost |
| `doctor.py` + `checks/` | validation; `registry.py` wires hosts + checks |
| `codex_review.py` | cross-model review: shell to `codex exec` for an independent second opinion |
| `plan.py` | plan lifecycle + `plans/active`→`archive` + `.flexkit/state.json` |
| `modes.py` | patch/build/design + escalation budgets |
| `hooks.py` | runtime hooks: session-start / user-prompt / pre-tool / subagent-start/stop + the status bar |
| `ui.py` | CLI output helpers - a thin rich wrapper (TTY-aware) |

## Operating system

On top of build/sync, flex-kit clones prep-kit's runtime - all driven by the host's
native subagents + prose, never a flex-kit engine:

- **Plans** (`plan.py`): `flex-kit plan/status/next-step/close`. Durable state in
  `plans/active/<id>/plan.md`; the active plan id is in `.flexkit/state.json`.
- **Modes** (`modes.py`): the plan's declared mode; `effective_mode()` escalates it
  when step/file counts exceed the budget. `status` surfaces the escalation.
- **Hooks** (`hooks.py` + `flex-kit hook <event>`): wired into `.claude/settings.json`
  by the claude host's `emit_global()`. session-start (orient + compaction re-orient),
  user-prompt (deduped plan reminder), pre-tool (secret guard). An opt-in stop hook
  (`config.notify`) fires a desktop notification when a long flex command finishes.
  Codex has no hooks.
- **Autonomous delivery**: the bundled `implement` command (templates base) ties the
  plan + `verify-fix-loop` skill + reviewer/implementer agents into one flow.

## templates vs packs

- `templates/flexkit/` = **base**, scaffolded by `init` on every project. Put here
  only domain-**neutral** "how to work" content (the planner/implementer/reviewer/
  tester/debugger/simplifier agents, verify-fix-loop + planning-methodology skills).
  Keep it minimal - it ships always.
- `packs/<name>/` = **opt-in** domain knowledge, copied in by `add`. Design domains
  (api-design) stay language-agnostic; implementation domains split by language
  (`backend-rust`). **When unsure, put it in a pack**, not base.

## Extension axes (all additive)

- **New host**: add `flex_kit/hosts/<host>.py` (`ID`, `SKILLS_DIR`/`AGENTS_DIR`,
  `emit_skill`/`emit_agent`), register in `registry.py`.
- **New check**: add `flex_kit/checks/<check>.py` exporting `CHECK = Check(id, run)`,
  register in `registry.py`. Project-local checks auto-load from `.flexkit/checks/`.
- **New capability kind**: extend `build.py` + host `emit_*`. Today: skills, agents.

## Conventions

- **Small, purposeful runtime deps**: Typer + `rich` (CLI/UI; `rich` rides along with
  Typer) + `questionary` (interactive pickers, e.g. `flex-kit add` with no args). Keep
  the set lean - prefer stdlib for parsing/IO - but a focused dep that clearly improves
  UX is fine. CLI output goes through `flex_kit/ui.py` (a thin rich wrapper).
- Lint/type: `ruff` + `mypy` (line length 100, target py310). Run `make check`.
- Every feature ships with a test under `tests/` (pytest, fixtures under
  `tests/fixtures/`).
- Packaging: `templates/**` and `packs/**` are included in the wheel
  (`pyproject.toml` `include`). Release via the `releaser` + `make publish` (same
  pipeline as db-cli).
- Commits: Conventional Commits, `<type>: <message>`, English, **no AI
  attribution**.

## Porting content from prep-kit

prep-kit skills/workflows are coupled to its machinery (manifest/pack/plan/
facilitation/router). When porting one, **decouple it**: drop the `triggers` array,
strip references to prep-kit commands/skills/plans, and keep only the
language/host-agnostic substance. Verify with `grep -ciE "manifest|/prep-|pack|
plan|facilitation|router"` → should reach 0.

## Commands

```bash
# build / content
flex-kit init [--force] [--gen]  # scaffold .flexkit/ (source only; --gen also builds hosts)
flex-kit init --update [--gen]   # refresh base + installed packs to the installed version
flex-kit init-docs [--force]  # scaffold a docs/ skeleton (non-destructive)
flex-kit add [<pack>] [--gen] # copy pack(s) into .flexkit/ (no arg: interactive picker)
flex-kit remove <pack> [--gen]  # remove a pack from .flexkit/ (--gen also rebuilds hosts)
flex-kit gen [--dry-run]      # source → host surfaces
flex-kit doctor               # validate source + that surfaces are in sync
# plan lifecycle
flex-kit plan "<task>" [--mode patch|build|design]  # create + activate a plan
flex-kit status | next-step | spec | close [--confirm]
# review / runtime (mostly host-invoked)
flex-kit codex-review [--type plan|diff|file] [--dry-run]   # cross-model review
flex-kit statusline | hook <event>                          # status bar + hooks
make install | test | check | publish
```
