---
name: process-verify-fix-loop
description: Run a post-implementation review-and-fix loop - review the change and run tests, and if there are critical/high findings or failing tests, fix and re-verify until clean or a max iteration count. Use after implementing a scoped change, before calling the work done.
---

# Verify-Fix Loop

A reusable "verify then fix" loop that catches issues before delivery. It
coordinates the agents this project provides - `implementer`, `reviewer`, and
`tester` - through files, and relies on the host (Claude Code / Codex) to spawn
them. There is no orchestration engine here: the host runs the subagents, this
skill is the protocol the main agent follows.

## When To Use

After completing an implementation, to verify correctness and resolve findings in
a convergence-driven loop before presenting results.

## Protocol

Every `handoffs/` and `reports/` path below lives **under the active plan dir** -
`plans/active/<id>/` (get `<id>` from `flex-kit status`) - so they archive with the plan on
`/flex-close` instead of piling up at the repo root. With no active plan (a planless
`/flex-review`), they fall back to the repo root.

1. **Hand off context.** Write `handoffs/review-input.md` using the template below.
2. **Verify (in parallel).** Spawn the `reviewer` and `tester` agents together, each
   reading `handoffs/review-input.md`:
   - `reviewer` writes `handoffs/review-verdict.md` - a verdict (`approve` |
     `revise`), critical/high finding counts, and fix recommendations.
   - `tester` writes `handoffs/test-report.md` - `pass` | `fail` and any failing
     tests.
   - Each also writes a durable, timestamped copy under `reports/` -
     `reports/review-<timestamp>.md` and `reports/test-<timestamp>.md` - so the audit
     trail survives across iterations instead of living only in chat.
   - **Cross-model pass (default on; turn off with `codexReview: off`).** Also run
     `flex-kit codex-review --type diff` for a second opinion from a different model.
     Read `reports/codex-review.md` and **merge its critical/high findings into
     `handoffs/review-verdict.md`** (the host `reviewer` stays authoritative - Codex
     adds findings, never overrides). **If the `codex` CLI is unavailable, skip silently
     and continue** - the loop never blocks on Codex.
3. **Merge and decide.** A `revise` verdict OR any failing test means continue to
   step 4. `approve` with only low/medium findings AND all tests passing means the
   loop may exit - check the Exit gates first.
4. **Fix and re-verify.** Spawn the `implementer` agent with the verdict and test
   report in scope; it addresses every critical/high finding and failing test. Then
   return to step 2. After `maxIterations` cycles, stop and hand what remains to the
   user.

## Handoff template (`handoffs/review-input.md`)

```
# Review input
- Goal: <one line - what this change delivers>
- Files changed: <repo paths>
- Checks run: <command -> pass | fail>
- Key decisions: <constraints accepted, choices made>
- Read these first: <file:line references, most important first>
```

## Exit gates

Do not mark the loop complete until ALL of these hold:

- every acceptance criterion of the current plan step is met;
- deterministic checks (build / lint / type / tests) pass;
- no stubs or TODOs remain in the changed files;
- the reviewer verdict has no unaddressed critical or high findings.

## Red Flags

You are drifting if: you mark the loop complete with an unaddressed critical/high finding
or a failing test; you keep iterating past `maxIterations` instead of handing what remains
to the user; you spawned a verifier without writing `handoffs/review-input.md` first.

## Rationalizations

The loop is cheap; skipping it is where regressions ship. Reject these:

- "The change is too small to verify" -> a small diff is exactly where a silent regression
  hides.
- "The tests will pass, no need to run them" -> unrun is unknown; the gate needs the
  command's output, not a prediction.
- "I'll fix that finding later" -> 'later' ships the bug; a critical/high finding is the
  loop's job to resolve now.

## Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `reviewer` | `reviewer` | the agent that reviews and writes the verdict |
| `tester` | `tester` | the agent that runs the project's tests |
| `implementer` | `implementer` | the agent that applies fixes |
| `maxIterations` | 2 | advisory cap on fix-verify cycles before pausing for the user |
| `severityThreshold` | `high` | minimum finding severity that triggers another fix iteration |
| `codexReview` | on | cross-model Codex review (`flex-kit codex-review`) merged into the verdict; auto-skips when the `codex` CLI is absent |

## Rules

- Agents communicate only through `handoffs/` files, never directly.
- The reviewer's verdict is authoritative; a failing `tester` run is a finding.
- Mind the verifier `Status`: `BLOCKED` or `NEEDS_CONTEXT` stops the loop and surfaces to
  the user (do not keep iterating); `DONE_WITH_CONCERNS` may exit but carry the concerns
  forward.
- Never skip the handoff write - the verifiers need scoped context to be useful.
- Exit only when the Exit gates hold, or the user stops the loop.
