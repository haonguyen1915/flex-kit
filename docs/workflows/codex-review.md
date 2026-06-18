# Workflow: cross-model review (`/flex-codex-review`)

An **independent second opinion from a different model**: send the active plan, the
diff, or a file to the Codex CLI and get its review back. Every other flow reviews
with the host's own `reviewer` subagent; this one reaches *outside* the host.

## How it starts

You type **`/flex-codex-review [--type plan|diff|file] [target]`** in Claude Code. It
runs `.claude/commands/flex-codex-review.md`, which calls the CLI:
`flex-kit codex-review ...`.

## Who does the work

| Step | Actor |
|---|---|
| Build the prompt + run codex | the **`flex-kit` CLI** (`codex_review.py`) |
| The review itself | the **Codex CLI** (`codex exec`) - a *different model* (default `gpt-5.5`) |
| Summarize + act on findings | the **main host agent** |

This is not a host subagent - it shells out to a separate process running another
model. Requires the `codex` CLI installed and logged in.

## Flow

```
/flex-codex-review [--type plan|diff|file] [target]
 1. BUILD PROMPT   plan (default): the active plan.md
                   --type diff   : the working-tree git diff
                   --type file P : the file P
                   wrapped in an "independent reviewer, report by severity" instruction
 2. RUN CODEX      subprocess: codex exec -m <model> -c reasoning.effort="<effort>" --full-auto -
                   (prompt piped on stdin; --dry-run prints the command instead)
 3. CAPTURE        write Codex's stdout to plans/active/<id>/reports/codex-review.md
 4. ACT            the agent summarizes findings and offers to address them, or to
                   merge critical/high ones into handoffs/review-verdict.md
```

## Navigation / routing

Linear, one-shot. `--type` selects what gets sent; there is no loop. It deliberately
mirrors the `reviewer` subagent's output shape (findings by severity) so its results
slot into the same place.

## State / memory

| File | Role |
|---|---|
| `plans/active/<id>/reports/codex-review.md` | Codex's review, saved for reference |
| (`reports/codex-review.md` at repo root if no active plan) | same, plan-less |

It reads the active plan (for the `plan` type) but writes only its report - no plan
state is mutated.

## Loop-back

None internally. To act on Codex's findings you either fix them, or merge the
critical/high ones into `handoffs/review-verdict.md`, which feeds the
[delivery](delivery.md) loop's `implementer` for an automated fix↔verify cycle.

## Review / Codex

This *is* the Codex review flow. The mechanism is `codex exec` (Codex's
non-interactive mode): flex-kit pipes the content in on stdin and captures the
model's review on stdout. Faithful to prep-kit's `/prep-codex-review`, implemented as
a Python subprocess instead of a Node script.
