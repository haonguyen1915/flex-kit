---
name: flex-plan
description: Create a tracked plan for a task and scaffold its steps. Use to start a new piece of work before implementing it.
argument-hint: [task] [--mode patch|build|design]
---

Plan the work for: **$ARGUMENTS**

This is the front door for any plan-shaped request - ambiguous or cross-cutting work
routes onward from here, so you never have to pick the lane yourself.

1. **Route.** If the intent or path is unclear, or several domains could apply, apply
   the `navigator` skill - it may send you to `/flex-fix`, `/flex-change`, or
   `/flex-review` instead. Skip when the path is obvious.
2. **Frame (large/ambiguous only).** For a large, ambiguous, or contract-changing plan,
   apply the `decision-interview` skill before drafting.
3. **Scaffold.** Run `flex-kit plan "<task>"` (add `--mode patch|build|design`; the
   `planning-methodology` skill's scope-challenge maps complexity to a mode). This
   writes an empty `plan.md` - don't hand-roll the folder.
4. **Draft.** Spawn the `planner` agent to fill `plan.md` (Goal, Steps, Files, Done,
   Risks, Open Questions). Mirror any `## Open Questions` back as `Questions for You` -
   numbered, with 2-4 concrete options each - don't make the user open the file.
5. **Log decisions.** Append each settled decision to the plan's `decisions.md` as
   `## YYYY-MM-DD - <label>` (create the file if absent).
6. **Approve.** Run `flex-kit status` to confirm, then close with a checkpoint:
   - `[A] Approve` -> `/flex-implement` (step-by-step)
   - `[D] Approve` -> `/flex-implement --full` (autonomous end-to-end)
   - `[R] Revise` -> adjust scope, mode, or steps first

   Use `[C] Continue` only as a soft nudge after approval.

When a choice comes up (routing or plan shape), present 2-4 numbered options and
recommend one; the user can pick a number or answer free-form. Don't implement here.
