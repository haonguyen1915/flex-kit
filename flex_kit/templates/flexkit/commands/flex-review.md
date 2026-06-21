---
name: flex-review
description: Review a code change - the working tree, a branch/PR, a commit, or a commit range - with the reviewer agent, no plan needed. Use for a standalone code review.
argument-hint: [target | <sha> | since <sha>] [--codex]
---

Standalone code review of **$ARGUMENTS** - no plan required.

## 1. Detect scope

Pick the diff from what the user asked; ask with clickable options if it's unclear:

| The user said... | Review |
|---|---|
| nothing / "my changes" / "working tree" | uncommitted: staged + unstaged + untracked (default) |
| a branch / "this PR" / "vs main" | the branch vs its base (`git diff <base>...HEAD`) |
| a commit SHA / "commit <sha>" | that one commit (`git show <sha>`) |
| "since <sha>" / "<sha> to HEAD" | the range (`git diff <sha>..HEAD`) |

## 2. Review

1. Write the scope into `handoffs/review-input.md` using the `process-verify-fix-loop` skill's
   template (goal, files changed, checks run, read-these-first).
2. Spawn the `reviewer` agent -> `handoffs/review-verdict.md` (verdict + findings) and a
   durable `reports/review-<timestamp>.md`.
3. `--codex`: also run `flex-kit codex-review --type diff` and merge its critical/high
   findings (host `reviewer` stays authoritative; skip if `codex` is absent).

## 3. Report

Present the findings grouped, most severe first:

- **Summary** - one line + the scope reviewed.
- **Stats** - commits / files / LOC in scope.
- **✅ Positives** - what the change improves (removed leaks, cleaner contracts).
- **🔴 Bugs** - wrong behavior or regressions.
- **🟡 Risks** - could break under load, concurrency, or edge cases.
- **⚠️ Must fix** - spec or convention violations (cite the doc/skill).
- **💡 Nice to have** - improvements, not blockers.
- **🟢 Coverage gaps** - changed behavior with no test.
- **📌 Pre-existing debt** - predates this change; flag, don't block.
- **Verdict** - approve / revise, with the critical + high count.

Keep a band even when empty (`None observed`) so the reader knows you checked it. Offer to
fix the findings with the `implementer`, or hand them to the user. Review-only - don't
change code unless asked.
