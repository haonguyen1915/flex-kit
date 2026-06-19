---
name: flex-review
description: Review the current change with the reviewer agent, without needing a plan. Use to get a standalone code review of the working-tree diff or a target.
argument-hint: [target] [--codex]
---

Review the current change ($ARGUMENTS if given, otherwise the working-tree git
diff) - standalone, no plan required.

1. Write `handoffs/review-input.md` using the template in the `verify-fix-loop`
   skill: goal, files changed, checks already run, key decisions, and a prioritized
   read-these-first list.
2. Spawn the `reviewer` agent; it writes `handoffs/review-verdict.md` (verdict +
   critical/high counts + fix recommendations) and a durable, timestamped
   `reports/review-<timestamp>.md`.
3. `--codex`: also run `flex-kit codex-review --type diff` for an independent
   cross-model opinion and merge its critical/high findings into the verdict (skip if
   the `codex` CLI is absent).
4. Report the findings. Offer to fix them with the `implementer` agent, or hand them
   to the user.

This is review-only - do not modify code unless the user asks.
