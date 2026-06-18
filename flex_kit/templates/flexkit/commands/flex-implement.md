---
name: flex-implement
description: Deliver the active plan - the next step, or all steps with --full - then run the verify-fix loop until the change is clean. Use to implement planned work autonomously.
argument-hint: [--full]
---

Deliver the active plan. The host runs this flow; flex-kit supplies the plan, the
agents (`implementer`, `reviewer`), and the `verify-fix-loop` protocol. There is no
engine here - you, the agent, follow the steps and spawn the subagents.

## Flow

1. **Orient.** Run `flex-kit status` and `flex-kit next-step`. If there is no active
   plan, stop and ask the user to create one with `/flex-plan "<task>"`.
2. **Check scope.** If `flex-kit status` shows the mode escalated (e.g.
   `patch -> build`), surface it and confirm before long autonomous execution.
3. **Implement.**
   - Default: implement the next incomplete step. Spawn the `implementer` agent.
   - `--full`: walk every incomplete step in order. As each lands, mark its
     checkbox `- [x]` in the active `plan.md`.
4. **Verify-fix loop.** After implementing, apply the `verify-fix-loop` skill:
   spawn `reviewer`; if the verdict is `revise` (critical/high findings), spawn
   `implementer` with the verdict to fix, then re-review. Cap at 2 iterations
   (`--full`: 3), then hand any remaining findings to the user.
5. **Close out.** When every step is `- [x]` and the loop is clean, summarize what
   shipped and offer `/flex-close` to archive the plan.

## Rules

- Never start without an active plan.
- Keep each step's change minimal; mark the plan checkbox as each step completes.
- The reviewer's verdict is authoritative - do not self-approve.
- Do not leave stubs or TODOs in delivered code.
