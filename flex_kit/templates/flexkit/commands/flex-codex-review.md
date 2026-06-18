---
name: flex-codex-review
description: Get an independent cross-model review from Codex (a different model) of the active plan or the current diff. Use for a second opinion from outside the host.
argument-hint: [--type plan|diff|file] [target]
---

Get an independent review from Codex (a different model than this host):

1. Run `flex-kit codex-review $ARGUMENTS`. It sends the active plan (default), the git
   diff (`--type diff`), or a file (`--type file <path>`) to `codex exec` and saves
   the report under the plan's `reports/codex-review.md`.
2. Read the saved report and summarize Codex's findings by severity.
3. Offer to act on them: update the plan/code, or merge the critical/high findings
   into `handoffs/review-verdict.md` so the verify-fix loop's `implementer` fixes them.

Requires the `codex` CLI installed and logged in. Use `--dry-run` to preview the
command without calling Codex.
