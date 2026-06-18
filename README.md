# flex-kit

Author AI agent **skills and agents once**, generate native surfaces for
**Claude Code** and **Codex**, and validate they never drift.

Most teams hand-maintain two near-identical copies of every skill - one under
`.claude/skills/`, one for Codex - edit one, forget the other, and the two hosts
quietly disagree. flex-kit keeps a single neutral source (`.flexkit/`) and
generates each host's surface from it.

## Concept

```
        SOURCE (you edit)                 GENERATED (never hand-edit)
  .flexkit/skills/<id>/SKILL.md   ──gen──▶ .claude/skills/<id>/      (Claude)
  .flexkit/agents/<id>.md         ──gen──▶ .agents/skills/<id>/      (Codex - native scan dir)
                                           .claude/agents/<id>.md    (Claude agent)
                                           .codex/agents/<id>.toml   (Codex agent)
```

- **One neutral source, many host surfaces.** `.flexkit/` is the single source of
  truth; every host directory is pure generated output. No host is privileged.
- **Never hand-edit generated.** Edit the source, re-run `gen`. `doctor` fails if a
  generated file was hand-edited or the source changed without a re-gen.
- **Capabilities:** `skills` (a `SKILL.md` + optional `references/`) and `agents`
  (one source markdown → a Claude `.md` + a Codex `.toml`, with the project's skill
  catalog injected at `<!-- SKILLS -->`).
- **Codex skills land in `.agents/skills/`** - the directory Codex natively scans
  (https://developers.openai.com/codex/skills), not `.codex/skills/`.

## Install

```bash
pipx install flex-kit
```

## Quick start

```bash
flex-kit init                 # scaffold .flexkit/ (base starters) + generate
flex-kit add api-design       # add an optional domain pack, then re-generate
flex-kit gen                  # regenerate host surfaces after editing source
flex-kit doctor               # validate source + that surfaces are in sync
```

## templates (base) vs packs (opt-in)

flex-kit ships two kinds of bundled content. The dividing question:
**"would EVERY project want this, regardless of what it builds?"**

| | `flex_kit/templates/` (base) | `flex_kit/packs/` (opt-in) |
|---|---|---|
| What | how to *work* (process / meta) | domain *knowledge* (subject matter) |
| Scope | domain-neutral | domain- or language-specific |
| Delivery | always, via `flex-kit init` | on request, via `flex-kit add <pack>` |
| Examples | `skill-creator`, `verify-fix-loop` + `reviewer`/`implementer` | `api-design`, (later) `backend-rust`, `frontend-svelte` |

- **Base** = the tool's opinion about *how to work* - neutral, useful in any
  codebase. Keep it minimal (it ships always and cannot be deselected).
- **Packs** = subject-matter content only some projects need. When unsure, put it
  in a pack. Design/principle domains (api-design) stay language-agnostic; only
  implementation domains (`backend-<lang>`, `frontend-<framework>`) split by
  language. A pack is just content copied into `.flexkit/` - no runtime machinery.

## Commands

| Command | Effect |
|---|---|
| `flex-kit init` | scaffold `.flexkit/` from the base template, then `gen` |
| `flex-kit add <pack>` | copy a bundled pack's skills/agents into `.flexkit/`, then `gen` |
| `flex-kit gen` | source → host surfaces (`.claude/`, `.agents/skills/`, `.codex/agents/`) |
| `flex-kit doctor` | run validation checks (source-valid, skill-contract, skill-refs, generated-in-sync) |

## How it stays extensible

Three growth axes, each additive - no change to the core:

| Add a... | Drop a file in... | Register in |
|---|---|---|
| **host** (e.g. cursor) | `flex_kit/hosts/<host>.py` | `flex_kit/registry.py` |
| **capability kind** | extend `flex_kit/build.py` + host `emit_*` | - |
| **check** | `flex_kit/checks/<check>.py` | `flex_kit/registry.py` |
| **project-specific check** | `<project>/.flexkit/checks/*.py` | auto-discovered |

A host adapter exposes `ID`, `SKILLS_DIR`/`AGENTS_DIR`, and `emit_skill` /
`emit_agent` returning `list[OutFile]`. A check is `CHECK = Check(id, run)` where
`run(ctx) -> list[Finding]`.

## Scope

flex-kit clones prep-kit's **core concept** (single source → generate per host →
validate), kept intentionally small. Out of scope: plan lifecycle, hooks, packs as
a runtime system, personas, model-routing. See
[`docs/prepkit-concept-spec.md`](docs/prepkit-concept-spec.md).

## Develop

```bash
make install   # poetry install
make test      # pytest
make check     # ruff + mypy + pytest
make publish   # build + poetry publish (PyPI)
```
