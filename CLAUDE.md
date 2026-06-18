# CLAUDE.md

Operating notes for working on the **flex-kit** codebase. (For end-user docs see
`README.md`; for the design rationale see `docs/prepkit-concept-spec.md`.)

## What flex-kit is

A single-source kit for AI-agent **skills + agents**: author once in a project's
`.flexkit/`, generate native surfaces for **Claude Code** and **Codex**, and
validate they never drift. It is a faithful, right-sized clone of prep-kit's *core*
concept (manifest/source → build → validate), deliberately without prep-kit's
plan, hook, runtime-pack, persona, or model-routing layers.

## The model

```
.flexkit/skills/<id>/SKILL.md   ─gen─▶ .claude/skills/<id>/  +  .agents/skills/<id>/   (Codex-native)
.flexkit/agents/<id>.md         ─gen─▶ .claude/agents/<id>.md  +  .codex/agents/<id>.toml
```

- **Source ≠ host.** `.flexkit/` is the only source; every host dir is generated
  output. No host is privileged (this is the key improvement over prep-kit, which
  authors in `.claude/skills/`).
- **Never hand-edit generated dirs.** `doctor`'s `generated-in-sync` check
  re-renders and compares, and flags stray/hand-edited files.
- **Codex skills go to `.agents/skills/`** (Codex natively scans it), NOT
  `.codex/skills/`. `.codex/` holds only agent `.toml`.
- **Convention-discovery, not a registry.** Skills/agents are discovered by scanning
  `.flexkit/`; per-item metadata lives in each item's frontmatter (e.g. `model`,
  `lane`), not a separate manifest.

## Module map (`flex_kit/`)

| File | Role |
|---|---|
| `main.py` | Typer CLI: `init` / `add` / `gen` / `doctor` |
| `config.py` | load `.flexkit/flexkit.config.json` (hosts, skillsDir, agentsDir) |
| `skills.py` / `agents.py` | discover + parse source skills / agents |
| `frontmatter.py` | parse + shared transforms (em-dash normalize, strip markup, wrap) |
| `emit.py` | `OutFile` - the unit of host output |
| `build.py` | `emit_for_host(host, skills, agents)` - shared by gen + the sync check |
| `hosts/{claude,codex}.py` | host adapters: `emit_skill` / `emit_agent` → `list[OutFile]` |
| `gen.py` / `init.py` / `add.py` | the three write commands |
| `doctor.py` + `checks/` | validation; `registry.py` wires hosts + checks |

## templates vs packs

- `templates/flexkit/` = **base**, scaffolded by `init` on every project. Put here
  only domain-**neutral** "how to work" content (skill-creator, verify-fix-loop +
  reviewer/implementer). Keep it minimal - it ships always.
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

- **Zero runtime deps** beyond Typer. Pure stdlib for IO/parsing.
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
flex-kit init [dir]           # scaffold .flexkit/ + gen
flex-kit add <pack> [dir]     # copy a pack into .flexkit/ + gen
flex-kit gen [--project dir]  # source → host surfaces
flex-kit doctor [--project dir]
make install | test | check | publish
```
