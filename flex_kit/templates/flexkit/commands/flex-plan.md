---
name: flex-plan
description: Create a tracked plan for a task and scaffold its steps. Use to start a new piece of work before implementing it.
argument-hint: [task] [--mode patch|build|design]
---

Plan the work for: **$ARGUMENTS**

This is the front door for any plan-shaped request - ambiguous or cross-cutting work
routes onward from here, so you never have to pick the lane yourself.

1. **Route.** If the intent or path is unclear, or several domains could apply, apply
   the `process-navigator` skill - it may send you to `/flex-fix`, `/flex-change`, or
   `/flex-review` instead. Skip when the path is obvious.
2. **Frame (large/ambiguous only).** For a large, ambiguous, or contract-changing plan,
   apply the `process-decision-interview` skill before drafting.
3. **Scaffold.** Run `flex-kit plan "<task>"` (add `--mode patch|build|design`; the
   `process-planning-methodology` skill's scope-challenge maps complexity to a mode). This
   writes an empty `plan.md` - don't hand-roll the folder.
4. **Draft.** Spawn the `planner` agent to fill `plan.md` (Goal, Steps, Files, Done,
   Risks, Open Questions). Then resolve every `## Open Questions` by running the
   `process-decision-interview` protocol - **one question at a time**, each re-explained
   plainly, with reasoned options, a `[Recommended]` pick + why, and an `Other` (write your
   own) choice - so the user never opens the file to answer.
5. **Log decisions.** Append each settled decision to the plan's `decisions.md` as
   `## YYYY-MM-DD - <label>` (create the file if absent).
6. **Approve.** Run `flex-kit status` to confirm, then close with a checkpoint:
   - `[A] Approve` -> `/flex-implement` (step-by-step)
   - `[D] Approve` -> `/flex-implement --full` (autonomous end-to-end)
   - `[R] Revise` -> adjust scope, mode, or steps first

   Use `[C] Continue` only as a soft nudge after approval.

Every choice (routing, plan shape, or an open question) goes through the
`process-decision-interview` protocol - asked one at a time, with reasoned options, a
`[Recommended]` pick, and an `Other` (write-your-own) option. Don't implement here.
