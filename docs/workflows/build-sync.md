# Workflow: build / sync (`flex-kit gen` / `doctor`)

The content workflow: turn the neutral source in `.flexkit/` into host-native
surfaces, and validate they never drift. This is the foundation every other flow
sits on.

## How it starts

A terminal command (also run for you by `flex-kit init` and `flex-kit add`):

```bash
flex-kit gen       # source -> host surfaces
flex-kit doctor    # validate source + that surfaces are in sync
```

## Who does the work

The **`flex-kit` CLI**. No agents - `gen` discovers + emits, `doctor` runs checks.
Per-host output is produced by **host adapters** (`flex_kit/hosts/claude.py`,
`codex.py`), each emitting only the capability kinds it supports.

## Flow - gen

```
flex-kit gen
 1. load .flexkit/flexkit.config.json (hosts, source dirs)
 2. discover skills (.flexkit/skills/), agents (.flexkit/agents/), commands (.flexkit/commands/)
 3. for each host:
      clean its owned dirs (skills/agents/commands)
      emit_skill   -> .claude/skills/   + .agents/skills/ (Codex-native)
      emit_agent   -> .claude/agents/*.md + .codex/agents/*.toml   (skills catalog injected)
      emit_command -> .claude/commands/*.md      (Claude only)
      emit_global  -> .claude/settings.json      (hooks wiring; Claude only)
```

## Flow - doctor

```
flex-kit doctor   (tool checks + project checks from .flexkit/checks/)
  source-valid       every skill/agent/command: name == id, non-empty description
  skill-contract     description length (20..1024), kebab name
  skill-refs         markdown links in bodies resolve
  generated-in-sync  re-emit in memory and compare to disk; flag drift + stray files
```

## Navigation / routing

`gen` iterates `hosts x capabilities`; each host adapter is asked only for the kinds
it implements (`hasattr(host, "emit_agent")` / `emit_command` / `emit_global`). Adding
a host or a capability kind is additive - no routing logic changes.

## State / memory

| Path | Role | Edit? |
|---|---|---|
| `.flexkit/skills` `/agents` `/commands` | **source** of truth | yes |
| `.claude/` `.agents/` `.codex/` | **generated** surfaces | never (run `gen`) |

There is no build cache or digest file; `gen` always re-emits, and `doctor`'s
`generated-in-sync` check *is* the drift guard (re-render + compare), simpler than a
stored-digest scheme.

## Loop-back

The author loop is manual and tight: **edit `.flexkit/` -> `flex-kit gen` -> `flex-kit
doctor`**. `doctor` failing (drift, stray file, bad frontmatter) sends you back to fix
the source and re-gen. Never edit generated files - `generated-in-sync` will catch it.

## Review / Codex

Not applicable - this flow has no review step. It is purely deterministic generation
and validation.
