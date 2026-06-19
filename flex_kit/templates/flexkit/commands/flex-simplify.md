---
name: flex-simplify
description: Run the simplifier agent over the current change to find dead code, over-abstraction, and redundancy, with concrete fixes. Use as a post-delivery quality pass.
argument-hint: [target]
---

Simplify the current change ($ARGUMENTS if given, otherwise the working-tree git diff) -
quality only, no behavior change.

1. Spawn the `simplifier` agent over the change; it reports findings (dead code,
   over-abstraction, redundancy), each with a concrete fix, plus a score.
2. Report them. Offer to apply with the `implementer`, or hand them to the user.

This is review-only - do not change code unless the user asks.
