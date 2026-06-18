# How to use flex-kit (step by step)

## 0. The one mental model to get first

flex-kit is a **build tool + scaffolder**, not a runtime. There are three different
things and it's easy to confuse them:

| You run it... | What it is | Examples |
|---|---|---|
| **In a terminal** | the `flex-kit` CLI | `flex-kit init`, `gen`, `plan`, `status`, `close`, `add`, `doctor` |
| **Inside the host** (Claude Code) | a generated **slash command** | `/implement` |
| **Automatically** | **hooks** the host fires | session orientation, plan reminder, secret guard |

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
  skills/   skill-creator/  verify-fix-loop/
  agents/   reviewer.md  implementer.md
  commands/ implement.md
.claude/                       # GENERATED - never edit
  skills/  agents/  commands/  settings.json   (hooks wired here)
.agents/skills/                # GENERATED - Codex reads skills here
.codex/agents/                 # GENERATED - Codex agents
```

Now **open Claude Code in this directory**. The hooks are already wired.

## 3. Author a skill (the core loop)

A skill teaches the agent one job. Two ways to get one:

**a) Pull a bundled pack:**
```bash
flex-kit add api-design        # copies api-design-pattern into .flexkit/ + re-gens
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

## 4. Do real work with the OS

Scenario: *"add a login endpoint."*

**Step 1 - make a plan (terminal):**
```bash
flex-kit plan "add login endpoint" --mode build
# created plan 260618-1641-add-login-endpoint (mode: build)
```
Open the created `plans/active/<id>/plan.md` and fill in the **Steps** checklist:
```markdown
## Steps
- [ ] add the route
- [ ] add the handler
- [ ] add tests
```

**Step 2 - check where you are (terminal):**
```bash
flex-kit status
# plan ... (mode: build, status: active)
#   steps: 0/3 done
#   next: add the route
```

**Step 3 - implement (inside Claude Code):**
Type the slash command:
```
/implement
```
The agent reads the active plan, implements the next step (or all steps with
`/implement --full`), then runs the **verify-fix loop**: it spawns the `reviewer`
subagent, and if there are critical/high findings it spawns `implementer` to fix and
re-reviews - up to a couple of rounds. As each step lands it ticks `- [x]` in
`plan.md`.

**Step 4 - close (terminal):**
```bash
flex-kit status        # 3/3 done
flex-kit close --confirm
# closed plan ... -> plans/archive/...
```

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
flex-kit add <pack>        # pull a domain pack into .flexkit/
# ...edit .flexkit/...     # author skills / agents / commands
flex-kit gen               # regenerate host surfaces  (run after every edit)
flex-kit doctor            # validate + catch drift     (run before committing)

# work
flex-kit plan "<task>"     # start tracked work
flex-kit status            # where am I?
flex-kit next-step         # what's next?
/implement                 # (in Claude Code) deliver the plan + verify-fix loop
flex-kit close --confirm   # archive when done
```

## 8. Where things live

| Path | What | Edit? |
|---|---|---|
| `.flexkit/` | your source (skills / agents / commands / config) | **yes** |
| `plans/active/` `plans/archive/` | your tracked work | yes (the plan.md) |
| `.flexkit/state.json` | active-plan pointer + hook dedup | no (managed) |
| `.claude/` `.agents/` `.codex/` | generated host surfaces | **never** (run `gen`) |

If a generated file ever looks wrong, don't fix it there - fix the source in
`.flexkit/` and run `flex-kit gen`. `flex-kit doctor` will tell you if anything drifted.
