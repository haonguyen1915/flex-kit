---
name: flex-change
description: Start design-first work - create a plan in design mode, scaffold a spec (proposal/design/tasks), and settle the design before implementing. Use for ambiguous or cross-cutting work.
argument-hint: [task]
---

Start design-first work for: **$ARGUMENTS**

Design-first fits ambiguous or cross-cutting work. If this is really a small bug or a
clear plannable change, route to `/flex-fix` or `/flex-plan` instead (the `navigator`
skill helps decide). Otherwise:

1. **Frame the decision.** If the request is ambiguous or has competing approaches,
   apply the `decision-interview` skill first - surface the real trade-off and settle
   a direction before writing anything. Skip only when the direction is already clear.
2. Run `flex-kit plan "<task>" --mode design`.
3. Run `flex-kit spec` to scaffold `spec/proposal.md`, `spec/design.md`,
   `spec/tasks.md` under the active plan.
4. Fill them in order: **proposal** (problem + chosen direction) -> **design**
   (system shape, data/contracts, validation plan, risks) -> **tasks** (the
   checklist). Log key decisions to `decisions.md` as `## YYYY-MM-DD - <label>`.
5. **Hard checkpoint.** Present the design with `[A] Approve / [R] Revise` and do
   **not** implement until the user approves.
6. On approval, spawn the `planner` agent to derive the plan `## Steps` from
   `spec/tasks.md`, then run `/flex-implement`.
