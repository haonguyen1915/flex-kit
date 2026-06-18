---
name: verify-fix-loop
description: Run a post-implementation review-and-fix loop - review the change, and if there are critical or high findings, fix and re-review until clean or a max iteration count. Use after implementing a scoped change, before calling the work done.
---

# Verify-Fix Loop

A reusable "review then fix" loop that catches issues before delivery. It
coordinates two agents this project provides - `implementer` and `reviewer` -
through files, and relies on the host (Claude Code / Codex) to spawn them. There
is no orchestration engine here: the host runs the subagents, this skill is the
protocol the main agent follows.

## When To Use

After completing an implementation, to verify correctness and resolve findings in
a convergence-driven loop before presenting results.

## Protocol

1. **Hand off context.** Write `handoffs/review-input.md` with: the goal, files
   changed, checks already run, key decisions, and what to read first.
2. **Review.** Spawn the `reviewer` agent. It reads `handoffs/review-input.md`,
   reviews the change, and writes `handoffs/review-verdict.md` with: a verdict
   (`approve` | `revise`), critical/high finding counts, and fix recommendations.
3. **Decide.**
   - `approve`, or only low/medium findings -> exit the loop.
   - critical or high findings -> continue to step 4.
4. **Fix and re-review.** Spawn the `implementer` agent with
   `handoffs/review-verdict.md` in scope; it addresses every critical/high
   finding. Then return to step 2. After `maxIterations` cycles, stop and hand the
   remaining findings to the user.

## Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `reviewer` | `reviewer` | the agent that reviews and writes the verdict |
| `implementer` | `implementer` | the agent that applies fixes |
| `maxIterations` | 2 | advisory cap on fix-review cycles before pausing for the user |
| `severityThreshold` | `high` | minimum finding severity that triggers another fix iteration |

## Rules

- Agents communicate only through `handoffs/` files, never directly.
- The reviewer's verdict is authoritative.
- Exit only on: a clean verdict, only low/medium findings remaining, or the user
  stopping the loop.
- Do not mark the loop complete while stubs or TODOs remain in the changed files.
