# Workflow: standalone review (`/flex-review`)

A code review of the current change **without** a plan - for a quick second pair of
eyes on a diff.

## How it starts

You type **`/flex-review [target]`** in Claude Code. It runs
`.claude/commands/flex-review.md`. With no target it reviews the working-tree git
diff; with a target it reviews that.

## Who does the work

| Step | Actor |
|---|---|
| Scope the diff, write the input | the **main agent** |
| Review | the **`reviewer`** subagent (host Task tool) |
| Report / optional fix | the **main agent** (and `implementer` only if you ask) |

## Flow

```
/flex-review [target]
 1. SCOPE   write handoffs/review-input.md (the diff scope + what to focus on)
 2. REVIEW  spawn `reviewer` -> handoffs/review-verdict.md (verdict + findings)
 3. REPORT  surface findings. Offer to fix with `implementer`, or hand to the user.
            (review-only: no code changes unless you ask)
```

## Navigation / routing

Linear and one-shot - there is no loop and no plan dependency. It reuses the same
`reviewer` agent and the same `handoffs/` verdict file as the delivery loop, so a
finding here reads identically to one produced during delivery.

## State / memory

| File | Role |
|---|---|
| `handoffs/review-input.md` | the diff scope handed to the reviewer |
| `handoffs/review-verdict.md` | the reviewer's verdict + findings |

If there is no active plan, these are written at the repo root's `handoffs/`. No
plan state is read or written - this flow is intentionally stateless.

## Loop-back

None by default - it's a single review pass. To act on findings you either fix them
yourself, ask for the `implementer`, or wrap the change in a plan and use
[delivery](delivery.md) (which loops review↔fix automatically).

## Review / Codex

The review is the `reviewer` subagent on the host. This is also the natural place a
future external/Codex review would hook in - it would add a second reviewer that
pipes the diff to another model and merges its findings into `review-verdict.md`. Not
built today (see [README](README.md#codex--external-review)).
