# flex-kit demo

Seven runnable scenarios that show flex-kit's core operating model end-to-end.
Everything below is **real output** from `flex-kit` (no mockups).

```bash
make install          # put `flex-kit` on PATH (or: pipx install .)
./demo/run.sh         # rebuilds demo/sandbox/proj from scratch and runs all 7
```

`demo/sandbox/` is generated and git-ignored — explore it after a run, delete it
any time. No `codex` CLI needed (scenario 5c uses `--dry-run`).

The one rule everything below rests on: **`.flexkit/` is the only thing you author;
every host dir (`.claude/`, `.codex/`, `.agents/`) is generated output you never
hand-edit.**

---

## 1. `init` — one neutral source → two host surfaces

```
$ flex-kit init -p proj
flex-kit init: created proj/.flexkit
  gen: 4 skills + 3 agents + 9 commands -> [claude, codex]
```

One source tree produces both hosts:

| You author (`.flexkit/`) | Claude gets (`.claude/`) | Codex gets (`.agents/` + `.codex/`) |
|---|---|---|
| `skills/<id>/SKILL.md` | `skills/<id>/SKILL.md` | `.agents/skills/<id>/SKILL.md` (Codex-native) |
| `agents/<id>.md` | `agents/<id>.md` | `.codex/agents/<id>.toml` |
| `commands/<id>.md` | `commands/<id>.md` | — (Codex has no commands) |
| — | `settings.json` (hooks wiring) | — |

## 2. Same source, two dialects + the drift guard

The reviewer agent, authored once, renders into each host's format:

```
# .claude/agents/reviewer.md          # .codex/agents/reviewer.toml
---                                     name = "reviewer"
name: reviewer                          description = "Review a code change…"
description: Review a code change…      model = "gpt-5.5"          # opus -> gpt-5.5
model: opus                             model_reasoning_effort = "medium"
---
```

`doctor` re-renders from source and compares — so a hand-edit to a generated file
is caught immediately:

```
$ printf '<!-- sneaky hand edit -->' >> .claude/agents/reviewer.md
$ flex-kit doctor
✗ generated-in-sync: claude: .claude/agents/reviewer.md drifted from source - run gen (do not hand-edit generated)
1 error(s), 0 warning(s)

$ flex-kit gen          # regenerate from source
$ flex-kit doctor
0 error(s), 0 warning(s)
```

## 3. Plan lifecycle — durable, file-backed state

```
$ flex-kit plan "Add OAuth login" --mode build
created plan 260618-2142-add-oauth-login (mode: build)

# (edit plan.md: tick one step, add two more)

$ flex-kit status
plan 260618-2142-add-oauth-login  (mode: build, status: active)
  steps: 1/3 done
  next: add /auth routes

$ flex-kit next-step
add /auth routes

$ flex-kit close            # guarded: won't archive unfinished work
plan …: 2 step(s) incomplete. Re-run with --confirm to archive.
```

Progress lives in `plans/active/<id>/plan.md`, not chat — it survives a context reset.

## 4. Mode escalation — scope can't balloon silently

A plan declares a mode (`patch`/`build`/`design`); the **effective** mode is computed
from its real size. A `patch` that grows past its budget (3 steps / 2 files) escalates:

```
$ flex-kit plan "Tiny typo fix" --mode patch     # then add 5 steps
$ flex-kit status
plan …-tiny-typo-fix  (mode: patch -> build, status: active)
  ! scope grew (steps=5 > 3) - consider declaring `build` mode
```

## 5. Hooks runtime — what the host fires automatically

```
# 5a  session open -> orientation injected into context
$ flex-kit hook session-start
flex-kit: branch master; plan …-tiny-typo-fix (build, 0/5 steps); next: s1

# 5b  before any tool call -> secret/credential guard
$ echo '{"tool_input":{"file_path":".env.production"}}' | flex-kit hook pre-tool
{"hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": "flex-kit guard: blocked access to a secret/credential path", …}}
$ echo '{"tool_input":{"file_path":"src/app.py"}}'      | flex-kit hook pre-tool
                                                          # (blank = allowed)

# 5c  cross-model review (a different model's second opinion)
$ flex-kit codex-review --dry-run
[dry-run] codex exec -m gpt-5.5 -c reasoning.effort="high" --full-auto -  ->  …/reports/codex-review.md
```

These are wired into `.claude/settings.json` by `init`/`gen`; the host invokes them.

## 6. `add` — opt-in domain packs (domain is NOT in base)

Base ships only neutral "how to work" content. Domain knowledge is opt-in:

```
$ flex-kit add                  # list packs
Available packs:
  api-design
$ flex-kit add api-design
flex-kit add api-design: 1 added, 0 skipped
  + skills/api-design-pattern
  gen: 5 skills + 3 agents      # the pack's skill is now in source + both hosts
```

## 7. Design-first — settle a spec before code

For ambiguous/cross-cutting work: a `design`-mode plan scaffolds a spec to fill and
approve before implementing.

```
$ flex-kit plan "Redesign billing API" --mode design
$ flex-kit spec
scaffolded spec/ for plan 260618-2142-redesign-billing-api

plans/active/…-redesign-billing-api/
  plan.md
  spec/proposal.md     # Problem -> Chosen Direction
  spec/design.md       # System Shape, Contracts, Validation Plan, Risks
  spec/tasks.md        # the checklist that becomes plan steps
```

---

### Where each scenario lives in the code

| Scenario | Module | Workflow doc |
|---|---|---|
| 1, 2 | `gen.py`, `hosts/{claude,codex}.py`, `checks/generated_in_sync.py` | [1-build-sync](../docs/workflows/1-build-sync.md) |
| 3 | `plan.py` | [2-plan-lifecycle](../docs/workflows/2-plan-lifecycle.md) |
| 4 | `modes.py` | (surfaced by `status`) |
| 5 | `hooks.py`, `codex_review.py` | [3-hooks-runtime](../docs/workflows/3-hooks-runtime.md), [5-codex-review](../docs/workflows/5-codex-review.md) |
| 6 | `add.py` | [1-build-sync](../docs/workflows/1-build-sync.md) |
| 7 | `plan.py` (`scaffold_spec`) | [7-design-first](../docs/workflows/7-design-first.md) |
