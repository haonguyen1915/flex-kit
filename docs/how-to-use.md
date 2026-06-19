# How to use flex-kit (step by step)

## 0. The one mental model to get first

flex-kit is a **build tool + scaffolder**, not a runtime. There are three different
things and it's easy to confuse them:

| You run it... | What it is | Examples |
|---|---|---|
| **Inside the host** (Claude Code) | generated **slash commands** (the main interface) | `/flex-plan`, `/flex-status`, `/flex-next-step`, `/flex-implement`, `/flex-close` |
| **In a terminal** | the `flex-kit` CLI (same actions + setup) | `flex-kit init`, `gen`, `add`, `doctor`, `plan`, `status`, `close` |
| **Automatically** | **hooks** the host fires | session orientation, plan reminder, secret guard |

Day to day you stay in Claude Code and use the slash commands; the CLI is the same
engine for setup (`init` / `gen` / `add` / `doctor`) and for driving from a terminal
or Codex.

The golden rule:

> **You edit SOURCE in `.flexkit/`. You run `flex-kit gen`. The HOST (Claude Code /
> Codex) reads the generated `.claude/` + `.agents/` and runs everything.**
> flex-kit never runs your agents - the host does. Never hand-edit generated files.

---

## 1. Install

```bash
pipx install flex-kit          # one global binary, used in any project
flex-kit --help
```

## 2. Start (or adopt) a project

```bash
cd my-project
flex-kit init
```

This creates `.flexkit/` (your source) and generates the host surfaces:

```
.flexkit/                      # SOURCE - you edit this
  flexkit.config.json
  skills/   skill-creator/  verify-fix-loop/  decision-interview/  navigator/  planning-methodology/
  agents/   planner.md  reviewer.md  implementer.md  tester.md
  commands/ flex-plan.md  flex-implement.md  flex-fix.md  ...
.claude/                       # GENERATED - never edit
  skills/  agents/  commands/  settings.json   (hooks wired here)
.agents/skills/                # GENERATED - Codex reads skills here
.codex/agents/                 # GENERATED - Codex agents
```

Now **open Claude Code in this directory**. The hooks are already wired.

**Already have a `.flexkit/`?** (adopting a project a teammate set up, or a fresh clone)
- don't run `init` again. Just materialize and check the host surfaces:

```bash
flex-kit gen       # (re)generate .claude/ + .agents/ from the committed .flexkit/
flex-kit doctor
```

`flex-kit init` refuses when `.flexkit/` exists; `flex-kit init --force` **wipes** it and
re-scaffolds from the template (throwing away your skills/agents/commands) - use it only
to start over.

## 3. Author a skill (the core loop)

A skill teaches the agent one job. Two ways to get one:

**a) Pull a bundled pack:**
```bash
flex-kit add                   # (no args) list the available packs
flex-kit add api-design        # copy one pack into .flexkit/ + re-gen
flex-kit add --all             # copy every bundled pack, then gen once
```

**b) Write your own:**
```bash
mkdir -p .flexkit/skills/my-skill
$EDITOR .flexkit/skills/my-skill/SKILL.md
```
```markdown
---
name: my-skill
description: What it does, and exactly when it should and should not trigger. The
  host matches this against the user's request to auto-load the skill.
---

# My Skill
...the guidance the agent should follow...
```

Then **always**:
```bash
flex-kit gen       # regenerate .claude/ + .agents/ from source
flex-kit doctor    # verify everything is in sync (fails if you hand-edited generated)
```

That `edit source → gen → doctor` loop is the whole content workflow. Agents
(`.flexkit/agents/<id>.md`) and commands (`.flexkit/commands/<id>.md`) work the same.

## 4. Do real work with the OS - all inside Claude Code

Scenario: *"add a login endpoint."* Everything below is typed **in Claude Code** as
slash commands; each one drives the underlying `flex-kit` CLI for you.

```
/flex-plan add login endpoint
```
The **front door**: it routes first (if the request is really a bug or design work it
sends you to `/flex-fix` or `/flex-change`), then spawns the `planner` agent to draft
`plans/active/<id>/plan.md` - Goal, a structured `## Steps` checklist with acceptance,
Files In Scope, Risks. It ends with a checkpoint: `[A] Approve -> /flex-implement`,
`[D] Approve -> /flex-implement --full`, or `[R] Revise`.

```
/flex-status
```
Shows where you are: `plan ... (build), 0/3 steps, next: add the route`. (If the mode
escalated, e.g. `patch -> build`, it tells you.)

```
/flex-implement
```
Implements the next step - or all steps with `/flex-implement --full` - then runs the
**verify-fix loop**: spawns `reviewer` and `tester` in parallel; a `revise` verdict or a
failing test sends `implementer` to fix, then re-verifies, a couple of rounds. Each step
it finishes gets ticked `- [x]` in `plan.md`.

```
/flex-close
```
Confirms the steps are done and archives the plan to `plans/archive/`.

> The slash commands are the **host interface**; the `flex-kit` CLI (`flex-kit plan`,
> `status`, `close`, ...) is the same thing from a terminal - use it directly when
> driving from a script or from Codex.

## 5. What the hooks do (automatic - you just see it)

You don't call hooks; Claude Code fires them. With a plan active you'll see:

- **On opening a session** (and after compaction):
  `flex-kit: branch main; plan 260618-1641-add-login-endpoint (build, 1/3 steps); next: add the handler`
- **As you work**, when plan progress changes, a one-line reminder of where you are.
- **If you (or the agent) try to read `.env` / a key / a prod-secrets file**, the
  pre-tool guard blocks it.

To see a hook's output yourself:
```bash
echo '{}' | flex-kit hook session-start
```

## 6. Modes and escalation

A plan's `--mode` sets the rigor: `patch` (small), `build` (standard), `design`
(spec-first). If a `patch` plan grows past its budget, `status` warns you:

```
plan ... (mode: patch -> build, status: active)
  ! scope grew (steps=5 > 3) - consider declaring `build` mode
```

This stops a "quick fix" from silently turning into a large change.

## 7. Daily cheat sheet

```bash
# content
flex-kit add <pack>        # pull a domain pack into .flexkit/  (--all for every pack)
# ...edit .flexkit/...     # author skills / agents / commands
flex-kit gen               # regenerate host surfaces  (run after every edit)
flex-kit doctor            # validate + catch drift     (run before committing)

# work - in Claude Code (slash commands), or the same via the CLI in a terminal
/flex-plan <task>          # start tracked work        (cli: flex-kit plan "<task>")
/flex-change <task>        # design-first: plan + spec (proposal/design/tasks) before code
/flex-status /flex-next-step  # where am I? what's next?  (cli: flex-kit status / next-step)
/flex-implement            # deliver the plan: implement -> test + review -> fix -> repeat
/flex-fix <bug>            # quick bug-to-patch path (reproduce -> diagnose -> patch -> verify)
/flex-review [target]      # standalone review of the current diff (no plan needed)
/flex-close                # archive when done         (cli: flex-kit close --confirm)
```

The delivery loop (`/flex-implement`) verifies with **two agents in parallel** -
`reviewer` (correctness/convention) and `tester` (runs the project's tests) - and a
failing test counts as a finding to fix. It drives checkpoints with a small grammar:
**[A] Approve / [R] Revise** at hard gates, **[C] Continue** for soft nudges. For
large/ambiguous work, start with `/flex-change` - it runs a `decision-interview` to
settle the direction, then a spec (`spec/proposal.md` -> `design.md` -> `tasks.md`)
before implementing. For a small bug, `/flex-fix` stays in patch mode.

## 8. Where things live

| Path | What | Edit? |
|---|---|---|
| `.flexkit/` | your source (skills / agents / commands / config) | **yes** |
| `plans/active/` `plans/archive/` | your tracked work | yes (the plan.md) |
| `.flexkit/state.json` | active-plan pointer + hook dedup | no (managed) |
| `.claude/` `.agents/` `.codex/` | generated host surfaces | **never** (run `gen`) |

If a generated file ever looks wrong, don't fix it there - fix the source in
`.flexkit/` and run `flex-kit gen`. `flex-kit doctor` will tell you if anything drifted.
