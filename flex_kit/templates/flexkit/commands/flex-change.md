---
name: flex-change
description: Start design-first work - create a plan in design mode, scaffold a spec (proposal/design/tasks), and settle the design before implementing. Use for ambiguous or cross-cutting work.
argument-hint: [task]
---

Start design-first work for: **$ARGUMENTS**

1. Run `flex-kit plan "<task>" --mode design`.
2. Run `flex-kit spec` to scaffold `spec/proposal.md`, `spec/design.md`,
   `spec/tasks.md` under the active plan.
3. Fill them in order: **proposal** (problem + chosen direction) -> **design**
   (system shape, data/contracts, validation plan, risks) -> **tasks** (the
   checklist).
4. Get the user's approval on the design **before** implementing.
5. Derive the plan `## Steps` from `spec/tasks.md`, then run `/flex-implement`.
