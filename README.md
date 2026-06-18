# flex-kit

Author AI agent skills **once**, generate native surfaces for **Claude Code** and
**Codex**, and validate they never drift.

Most teams end up hand-maintaining two near-identical copies of every skill - one
under `.claude/skills/`, one under `.codex/skills/`. Edit one, forget the other,
and the two hosts quietly disagree. flex-kit keeps a single neutral source and
generates each host's surface from it.

## Install

```bash
pipx install flex-kit
```

## Use

In a project, create the source + a tiny config:

```
.flexkit/
  flexkit.config.json        # { "hosts": ["claude", "codex"], "skillsDir": ".flexkit/skills" }
  skills/
    <skill-id>/SKILL.md      # neutral source: name + single-line description + body
    <skill-id>/references/   # copied verbatim to every host
```

Then:

```bash
flex-kit gen      # .flexkit/skills/* -> .claude/skills/* + .codex/skills/*
flex-kit doctor   # validate source + that generated surfaces are in sync
```

`gen` owns `.claude/skills/` and `.codex/skills/` - **never hand-edit those**;
edit the source and re-run `gen`. `doctor`'s `generated-in-sync` check fails if a
generated file was edited by hand or the source changed without a re-gen.

## How it stays extensible

Three growth axes, each additive - no change to the core:

| Add a... | Drop a file in... | Register in |
|---|---|---|
| **host** (e.g. cursor) | `flex_kit/hosts/<host>.py` | `flex_kit/registry.py` |
| **check** | `flex_kit/checks/<check>.py` | `flex_kit/registry.py` |
| **project-specific check** | `<project>/.flexkit/checks/*.py` | auto-discovered |

A host adapter is `ID`, `BASE_DIR`, and `render_frontmatter(fm) -> str`. A check is
`CHECK = Check(id, run)` where `run(ctx) -> list[Finding]`.

## Develop

```bash
make install   # poetry install
make test      # pytest
make check     # ruff + mypy + pytest
make publish   # build + poetry publish (PyPI)
```
