---
name: process-decision-interview
description: Run a structured choice interview to settle planning questions one at a time - the core decision before a plan is drafted, AND every open question after one is drafted. Each is re-explained plainly with options (a reason per option), a recommended pick with its why, and a write-your-own choice. Use whenever planning surfaces a choice the user must confirm.
---

# Decision / Choice Interview

A protocol the main agent runs with the user to turn open questions into settled choices
with recorded rationale - whether *before* a plan (the consequential direction) or *after*
drafting one (its open questions / confirmations). No subagent is spawned.

## When To Use

- **Pre-plan** - at the start of `/flex-change` or any ambiguous / contract-changing work,
  to settle the core decision before a spec or plan is written.
- **Post-plan** - after the `planner` drafts a plan, to resolve every `## Open Questions`
  and confirmation **before** approval.

Skip a question only when its answer is already obvious - this is for real choices, not
ceremony.

## Protocol

1. **Collect & order.** Gather the open questions; order them by consequence (most
   impactful first). Take them **one at a time** - never dump the whole list at once.
2. **For each question, in turn:**
   - **Re-explain plainly.** Restate it in plain language - what is actually being decided
     and why it matters - so the user need not open the plan to answer.
   - **Lay out options.** Give 2-4 concrete options, **each with a one-line reason** (its
     trade-off: cost, risk, reversibility, who it affects). No straw men.
   - **Challenge weak premises.** Drop any option that fails a quick probe - who the user
     is, what defines success, the cheapest reversible version.
   - **Recommend one.** Mark exactly one option **[Recommended]** and give the reason
     behind it - never present options without a lean.
   - **Offer "Other".** Always end with an **Other - your own answer** option, so the user
     is never boxed into the presented choices.
   - **Wait.** Get the user's pick before moving to the next question.
3. **Settle & record.** Log each settled choice - the *why*, not just the *what* - to the
   plan's `decisions.md` as `## YYYY-MM-DD - <decision>`.
4. **Next.** Loop to the next question until none remain, then hand the settled direction
   into the spec / plan.

## Rules

- **One question at a time** - do not bundle unrelated choices into a single ask.
- **Always recommend** one option explicitly, with its reason.
- **Always offer a write-your-own ("Other") option** - the presented set is never exhaustive.
- Record the rationale; it is what survives a reset.
