---
name: flex-plan
description: Create a tracked plan for a task and scaffold its steps. Use to start a new piece of work before implementing it.
argument-hint: [task] [--mode patch|build|design]
---

Create a plan for: **$ARGUMENTS**

1. **Route first (if unclear).** If the task's intent or the right path is not obvious
   - or several domains could apply - apply the `navigator` skill. It may send you to
   `/flex-fix` (a bug), `/flex-change` (design-first), or `/flex-review` instead of a
   plain plan, and names the domain skills that apply. Skip when the path is clear.
2. Run `flex-kit plan "<task>"` in the terminal (add `--mode patch|build|design` if
   the task implies a size; default is `build`).
3. Open the created `plans/active/<id>/plan.md` and replace the placeholder step with
   a concrete `## Steps` checklist (`- [ ] ...`) derived from the task, and fill in
   `## Goal` and `## Files In Scope`.
4. Run `flex-kit status` to confirm, then suggest `/flex-implement` to deliver it.
