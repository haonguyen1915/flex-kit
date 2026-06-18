---
name: flex-review
description: Review the current change with the reviewer agent, without needing a plan. Use to get a standalone code review of the working-tree diff or a target.
argument-hint: [target]
---

Review the current change ($ARGUMENTS if given, otherwise the working-tree git
diff) - standalone, no plan required.

1. Write `handoffs/review-input.md` with the diff scope and what to focus on.
2. Spawn the `reviewer` agent; it writes `handoffs/review-verdict.md` with a
   verdict, critical/high finding counts, and fix recommendations.
3. Report the findings. Offer to fix them with the `implementer` agent, or hand
   them to the user.

This is review-only - do not modify code unless the user asks.
