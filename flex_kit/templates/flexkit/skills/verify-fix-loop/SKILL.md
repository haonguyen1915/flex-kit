---
name: verify-fix-loop
description: Run a post-implementation review-and-fix loop - review the change, and if there are critical or high findings, fix and re-review until clean or a max iteration count. Use after implementing a scoped change, before calling the work done.
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

1. **Hand off context.** Write `handoffs/review-input.md` with: the goal, files
   changed, checks already run, key decisions, and what to read first.
2. **Verify (in parallel).** Spawn the `reviewer` and `tester` agents together,
   each reading `handoffs/review-input.md`:
   - `reviewer` writes `handoffs/review-verdict.md` - a verdict (`approve` |
     `revise`), critical/high finding counts, and fix recommendations.
   - `tester` writes `handoffs/test-report.md` - `pass` | `fail` and any failing
     tests.
3. **Merge and decide.** A `revise` verdict OR any failing test means continue to
   step 4. `approve` with only low/medium findings and all tests passing means exit.
4. **Fix and re-verify.** Spawn the `implementer` agent with the verdict and test
   report in scope; it addresses every critical/high finding and failing test. Then
   return to step 2. After `maxIterations` cycles, stop and hand what remains to the
   user.

## Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `reviewer` | `reviewer` | the agent that reviews and writes the verdict |
| `tester` | `tester` | the agent that runs the project's tests |
| `implementer` | `implementer` | the agent that applies fixes |
| `maxIterations` | 2 | advisory cap on fix-verify cycles before pausing for the user |
| `severityThreshold` | `high` | minimum finding severity that triggers another fix iteration |

## Rules

- Agents communicate only through `handoffs/` files, never directly.
- The reviewer's verdict is authoritative.
- Exit only on: a clean verdict, only low/medium findings remaining, or the user
  stopping the loop.
- Do not mark the loop complete while stubs or TODOs remain in the changed files.
