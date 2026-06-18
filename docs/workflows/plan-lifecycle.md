# Workflow: plan lifecycle (`flex-kit plan` / `status` / `next-step` / `close`)

The durable backbone every other flow reads. A plan is multi-step work state that
survives context resets.

## How it starts

A terminal command or its slash wrapper:

| CLI | Slash | Does |
|---|---|---|
| `flex-kit plan "<task>" [--mode]` | `/flex-plan` | create + activate a plan |
| `flex-kit status` | `/flex-status` | show progress + effective mode |
| `flex-kit next-step` | `/flex-next-step` | show the next incomplete step |
| `flex-kit close [--confirm]` | `/flex-close` | archive the plan |

## Who does the work

The **`flex-kit` CLI** (Python) does the file operations directly. The slash commands
are thin wrappers: the host agent runs the CLI for you and adds guidance (e.g.
scaffolding the steps from the task). No subagents are involved.

## Flow

```
flex-kit plan "<task>" --mode build
  -> creates plans/active/<YYMMDD-HHmm-slug>/plan.md
     (frontmatter: id, created, mode, status; sections: Goal / Steps / Files / Done)
  -> writes .flexkit/state.json { "active_plan": "<id>" }

flex-kit status / next-step
  -> read the active plan, parse the - [ ] / - [x] checklist
  -> compute the effective mode (modes.effective_mode) and surface escalation

flex-kit close --confirm
  -> mv plans/active/<id>  ->  plans/archive/<id>
  -> remove active_plan from state.json
```

## Navigation / routing

`status` and `next-step` derive everything from `plan.md` (the checklist) +
`state.json` (which plan). The "next step" is simply the first unchecked item -
there is no router. `status` also runs `modes.effective_mode()` to show whether the
declared mode escalated (e.g. `patch -> build` when the step/file budget is exceeded).

## State / memory

| File | Role | Written by |
|---|---|---|
| `plans/active/<id>/plan.md` | the plan + step checklist | you (and the implementer ticks boxes) |
| `.flexkit/state.json` | `active_plan` pointer + `last_reminder` dedup hash | the CLI + hooks |
| `plans/archive/<id>/` | closed plans, kept for reference | `close --confirm` |

This is the project's memory: durable, inspectable, and the single source the hooks
and the delivery loop both read.

## Loop-back

No internal loop - it's a state machine: `active -> (work) -> archived`. The
iteration happens inside [delivery](delivery.md), which ticks this plan's boxes.

## Review / Codex

Not applicable - the plan lifecycle does no review. Review belongs to the
[delivery](delivery.md) and [review](review.md) flows.
