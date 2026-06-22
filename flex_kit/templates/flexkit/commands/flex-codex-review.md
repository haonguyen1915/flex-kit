---
name: flex-codex-review
description: Get an independent cross-model review from Codex (a different model) of the active plan or the current diff. Use for a second opinion from outside the host.
argument-hint: [--type plan|diff|file] [--base <ref>] [-i "<lens>"] [target] [--model M]
---

Get an independent review from Codex - a different model than this host.

1. **Run.** `flex-kit codex-review $ARGUMENTS` sends the active plan (default), the git
   diff (`--type diff`), or a file (`--type file <path>`) to `codex exec` and saves the
   report to the active plan's `reports/codex-review.md` (repo-root `reports/` if no
   plan). For a PR/branch use `--type diff --base <ref>` (reviews `<ref>...HEAD`). Steer
   the lens with `-i "<instruction>"` (e.g. `-i "review the light-mode UI for DataGrip
   fidelity, light mode only"`) - default is the generic correctness/risk/convention
   prompt. Override with `--model <m> --effort <e>`; `--dry-run` previews the command.
2. **Summarize.** Read the saved report and report Codex's findings by severity. This is
   a *second opinion* from another model - weigh it against the host `reviewer`, don't
   auto-apply (a different model can be confidently wrong).
3. **Decide.** Offer:
   - `[A] Address` - merge the critical/high findings into `handoffs/review-verdict.md`
     so the verify-fix loop's `implementer` fixes them (or fix them directly).
   - `[I] Ignore` - acknowledge but don't act; note why in one line.
   - `[R] Re-run` - adjust `--type` / `--model` / `--effort` and run again.

Requires the `codex` CLI installed and logged in.
