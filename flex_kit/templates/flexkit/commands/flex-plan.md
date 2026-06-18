---
name: flex-plan
description: Create a tracked plan for a task and scaffold its steps. Use to start a new piece of work before implementing it.
argument-hint: [task] [--mode patch|build|design]
---

Create a plan for: **$ARGUMENTS**

1. Run `flex-kit plan "<task>"` in the terminal (add `--mode patch|build|design` if
   the task implies a size; default is `build`).
2. Open the created `plans/active/<id>/plan.md` and replace the placeholder step with
   a concrete `## Steps` checklist (`- [ ] ...`) derived from the task, and fill in
   `## Goal` and `## Files In Scope`.
3. Run `flex-kit status` to confirm, then suggest `/flex-implement` to deliver it.
