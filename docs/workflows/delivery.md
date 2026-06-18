# Workflow: delivery (`/flex-implement`)

The main multi-agent loop: implement the active plan, verify it (review + tests in
parallel), fix what's wrong, repeat until clean, then close.

## How it starts

You type **`/flex-implement`** (or `/flex-implement --full`) inside Claude Code. That
runs the generated `.claude/commands/flex-implement.md` prose - the main host agent
reads it and drives the flow below. (There is no engine; the agent executes the
protocol.)

## Who does the work

| Step | Actor |
|---|---|
| Orientation, decisions, spawning | the **main host agent** (following the command) |
| Writing the code | the **`implementer`** subagent (host Task tool) |
| Reviewing the change | the **`reviewer`** subagent |
| Running the tests | the **`tester`** subagent |

The `verify-fix-loop` skill is the protocol the main agent applies in step 4.

## Flow

```
/flex-implement [--full]
 1. ORIENT      run `flex-kit status` + `flex-kit next-step` (CLI).
                no active plan -> stop, suggest /flex-plan.
 2. SCOPE GATE  status shows mode escalated (patch -> build)? surface + confirm
                before long autonomous execution.
 3. IMPLEMENT   default: spawn `implementer` for the next step.
                --full : walk every incomplete step, ticking - [x] in plan.md.
 4. VERIFY      (verify-fix-loop) spawn `reviewer` AND `tester` in parallel:
                  reviewer -> handoffs/review-verdict.md (approve|revise + findings)
                  tester   -> handoffs/test-report.md   (pass|fail)
 5. DECIDE      revise verdict OR any failing test -> step 6.
                approve + low/medium only + tests pass -> step 7.
 6. FIX         spawn `implementer` with the verdict + test report -> back to step 4.
                cap: 2 iterations (--full: 3), then hand the rest to the user.
 7. CLOSE OUT   all steps - [x] and clean -> summarize, offer /flex-close.
```

## Navigation / routing

- **What to do next** comes from `flex-kit next-step` reading the plan checklist - not
  from a router skill. The plan *is* the routing.
- **Which skills the subagents use** is decided by the host: each subagent's body
  lists the available skills (injected at `<!-- SKILLS -->`), and the host loads the
  one whose `description` matches the task. No navigator/dispatch skill is needed.

## State / memory

| File | Role |
|---|---|
| `plans/active/<id>/plan.md` | the steps; `- [x]` ticked as each lands (durable progress) |
| `.flexkit/state.json` | which plan is active |
| `plans/active/<id>/handoffs/review-input.md` | scope handed to the verifiers |
| `plans/active/<id>/handoffs/review-verdict.md` | reviewer verdict (authoritative) |
| `plans/active/<id>/handoffs/test-report.md` | tester pass/fail |

Because progress lives in `plan.md` (not chat), the loop survives a context reset: a
new session re-orients from the plan (see [hooks-runtime](hooks-runtime.md)).

## Loop-back

The fix↔verify cycle is step 6 → step 4. It exits only on: a clean verdict with
passing tests, only low/medium findings remaining, or hitting `maxIterations` (then
the user decides). Each iteration re-writes `review-verdict.md` / `test-report.md`,
so the decision is always made from the latest files, never from memory.

## Review / Codex

Review is the **`reviewer` subagent** spawned on the host; its verdict file is
authoritative and a failing `tester` run counts as a finding to fix. There is no
external/Codex cross-model review step today - see
[README](README.md#codex--external-review).
