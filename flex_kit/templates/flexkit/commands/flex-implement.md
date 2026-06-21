---
name: flex-implement
description: Deliver the active plan - the next step, or all steps with --full - then run the verify-fix loop (review + tests) until the change is clean. Use to implement planned work autonomously.
argument-hint: [--full] [--codex]
---

Deliver the active plan. The host runs this flow; flex-kit supplies the plan, the
agents (`implementer`, `reviewer`, `tester`), and the `process-verify-fix-loop` protocol.
There is no engine here - you, the agent, follow the steps and spawn the subagents.

## Interaction grammar

Drive every pause with one of these, so a reply is never ambiguous:

- **[A] Approve / [R] Revise** - a *hard checkpoint*: stop and wait for an explicit
  `a` / `r` before continuing. Use where getting it wrong is expensive (see below).
- **[C] Continue** - a *soft nudge* between already-approved steps; proceed on `c`.

When a hard checkpoint is required depends on the plan's mode:

- `patch` - none, unless the task unexpectedly grows past patch scope.
- `build` - before: creating/revising a spec, changing a contract or schema, a
  cross-cutting change, or a long autonomous run (`--full`).
- `design` - the design was already approved at `/flex-change`; re-confirm before
  code only if the design changed.

## Flow

1. **Orient.** Run `flex-kit status` and `flex-kit next-step`. No active plan -> stop
   and ask the user to create one with `/flex-plan "<task>"`.
2. **Scope gate.** If `flex-kit status` shows the mode escalated (e.g.
   `patch -> build`), STOP - do not keep implementing under the old mode. Surface the
   drift and ask `[A] Approve` the larger mode / `[R] Revise` the plan before going on.
3. **Implement.**
   - Default: the next incomplete step. Spawn the `implementer` agent.
   - `--full`: walk every incomplete step in order; mark each `- [x]` in `plan.md` as
     it lands. `--full` is itself a long autonomous run -> clear the build-mode
     checkpoint first.
   - Append any non-obvious choice to `plans/active/<id>/decisions.md` as
     `## YYYY-MM-DD - <label>` so the rationale survives a reset.
4. **Verify-fix loop.** Apply the `process-verify-fix-loop` skill: spawn `reviewer` AND
   `tester` in parallel. A `revise` verdict OR a failing test means fix and re-verify
   (spawn `implementer` with the verdict + test report). Cap at 2 iterations
   (`--full`: 3); at the cap, present what remains with `[A] / [R]` and hand off.
   - `--codex`: turn on the skill's `codexReview` - also run `flex-kit codex-review
     --type diff` for a cross-model second opinion and merge its critical/high findings
     into the verdict (host `reviewer` stays authoritative; skip if `codex` is absent).
5. **Close out.** When every step is `- [x]`, the verdict is clean, and tests pass,
   summarize what shipped (offer to commit if the user wants) and present
   `[A] Approve -> /flex-close` or `[R] Revise`.

## Rules

- Never start without an active plan; never implement under a stale mode (step 2).
- The reviewer's verdict is authoritative and a failing `tester` run is a finding -
  do not self-approve, do not pre-filter findings before presenting them.
- Keep each step's change minimal; do not leave stubs or TODOs in delivered code.
