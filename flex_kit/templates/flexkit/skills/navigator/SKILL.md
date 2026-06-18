---
name: navigator
description: Route a task to the right path before planning - classify intent (deliver / fix / design / review / research), pick the command and any domain skills that apply, and recommend a mode. Use at the start of work when the intent or the right path is not obvious, especially across multiple domains.
---

# Navigator

A routing protocol the main agent runs *before* committing to a path. It does not do
the work - it decides which path does. There is no router engine: you, the agent, read
the task and the available-skills catalog already in your context and choose, then
recommend one option with a reason. Skip it when the path is already obvious - this is
for resolving ambiguity, not ceremony.

## When To Use

- The task could be more than one kind of work (a bug fix vs a feature vs a redesign).
- Several domains or installed packs could plausibly own it and it is unclear which
  skill applies.
- The ask is vague ("improve X", "look at Y") with no path implied.

Skip it for a clearly-scoped request that already names its own path.

## Protocol

1. **Classify intent.** Put the task in one lane and route accordingly:
   - *deliver* a planned change -> `/flex-plan`, then `/flex-implement`
   - *fix* a specific bug -> `/flex-fix` (patch mode)
   - *design* ambiguous or cross-cutting work -> `/flex-change` (runs decision-interview)
   - *review* existing work -> `/flex-review` (or `/flex-codex-review` for a 2nd model)
   - *research / explain* only -> answer directly, no plan
2. **Pick the skills.** Scan the skills available to you (this project's skills,
   including any added with `flex-kit add`). Name the ones whose `description` matches
   this task so the work uses them instead of reinventing. If two overlap, say which
   fits better and why. If nothing matches, say so rather than forcing a skill.
3. **Suggest a mode.** patch (tiny, <=2 files) / build (standard) / design (needs a
   spec). Default to build when unsure.
4. **Recommend one path.** State the single best route as
   "`<command>` in `<mode>`, using `<skills>`" with a one-line reason. Offer an
   alternative only when the call is genuinely close.

## Rules

- Route to the lightest sound path - do not send a one-file fix through `/flex-change`.
- Always recommend explicitly; never list options without a lean.
- Match on the `description` in the catalog, not a guess.
- Advisory only: the user can override the route.
