---
name: process-decision-interview
description: Resolve the core decision behind ambiguous or cross-cutting work before planning - surface options, challenge weak premises, and settle trade-offs one at a time. Use at the start of design-first work when the right direction is not yet clear.
---

# Decision Interview

A short, structured interview that turns "we should probably do X" into a settled
direction with a recorded rationale - *before* a spec or plan is written. It is a
protocol the main agent runs with the user; no subagent is spawned.

## When To Use

At the start of `/flex-change` (or any design-mode work) when the request is
ambiguous, has competing approaches, or hides an unstated trade-off. Skip it when the
direction is already obvious - this is for resolving uncertainty, not ceremony.

## Protocol

1. **Name the decision.** State, in one line, the single most consequential choice
   this work turns on. If there are several, order them and take the first.
2. **Lay out the options.** List 2-4 real candidates, each with its main trade-off
   (cost, risk, reversibility, who it affects). No straw men.
3. **Challenge the premise.** Probe what is assumed: who is the user, what metric
   defines success, what breaks if we are wrong, what is the cheapest reversible
   version. Drop options that fail these.
4. **Settle and record.** Recommend one option with a one-line reason, get the user's
   call, and log it to the plan's `decisions.md` as `## YYYY-MM-DD - <decision>`.
5. **Hand off.** Carry the settled direction into `spec/proposal.md` (problem +
   chosen direction). Loop back to step 1 if another decision remains.

## Rules

- One decision at a time; do not bundle unrelated choices into a single yes/no.
- Always recommend explicitly - never present options without a lean.
- Record the *why*, not just the *what* - the rationale is what survives a reset.
