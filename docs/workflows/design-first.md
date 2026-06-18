# Workflow: design-first (`/flex-change` + `flex-kit spec`)

For ambiguous or cross-cutting work: settle a spec (proposal → design → tasks) and
get approval **before** writing code. The build then follows the delivery loop.

## How it starts

You type **`/flex-change <task>`** in Claude Code. It runs
`.claude/commands/flex-change.md`, which drives the steps below; the spec scaffolding
itself is a CLI call (`flex-kit spec`).

## Who does the work

| Step | Actor |
|---|---|
| Create the plan + scaffold spec | the **main agent** running CLI (`flex-kit plan` / `flex-kit spec`) |
| Fill proposal / design / tasks | the **main agent**, with the user approving |
| Implement (after approval) | the [delivery](delivery.md) loop (`implementer` / `reviewer` / `tester`) |

No subagents run during the design phase - it is the main agent + the user.

## Flow

```
/flex-change <task>
 1. PLAN     flex-kit plan "<task>" --mode design          (CLI)
 2. SCAFFOLD flex-kit spec                                  (CLI)
             -> plans/active/<id>/spec/{proposal,design,tasks}.md
 3. FILL     proposal.md  (Problem -> Chosen Direction)
             design.md    (System Shape, Data And Contracts, Validation Plan, Risks)
             tasks.md      (the checklist)
 4. APPROVE  the user signs off on the design  <-- hard gate
 5. HAND OFF derive plan.md ## Steps from spec/tasks.md
 6. BUILD    /flex-implement   -> the delivery loop
```

## Navigation / routing

The order is fixed by the command prose: proposal → design → tasks → approval →
implement. Step 4 is a **hard checkpoint** - the flow does not proceed to code until
the user approves. `design` mode (set in step 1) is what signals "spec required"; the
delivery loop's scope gate also respects it.

## State / memory

| File | Role |
|---|---|
| `plans/active/<id>/plan.md` | the plan (mode `design`); steps come from tasks.md |
| `plans/active/<id>/spec/proposal.md` | problem + chosen direction |
| `plans/active/<id>/spec/design.md` | system shape, contracts, validation plan, risks |
| `plans/active/<id>/spec/tasks.md` | the task checklist that becomes plan steps |

The spec is durable on disk, so the design survives resets and is the reference the
delivery loop builds against.

## Loop-back

Within the design phase there is no automated loop - the user iterates on the spec
files directly. After approval the flow joins the [delivery](delivery.md) loop, which
owns the implement↔verify cycle.

## Review / Codex

The design itself is reviewed by the **user** at the step-4 gate (no subagent). Once
implementation starts, review is the `reviewer` subagent as in the delivery loop. No
external/Codex review step today.
