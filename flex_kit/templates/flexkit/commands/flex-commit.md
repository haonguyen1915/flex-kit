---
name: flex-commit
description: Commit the working tree as structured, review-friendly commits - one logical purpose each, a Conventional-Commits subject, no AI attribution. Use when asked to commit pending changes.
argument-hint: [optional focus or message]
---

Commit the pending changes for: **$ARGUMENTS** (default: everything staged + unstaged,
split by purpose). Only commit when asked; never push unless told.

> If the project's `CLAUDE.md` mandates a different commit style, follow that and ignore
> the conflicting rules below.

## 1. Understand the full diff first

Run `git status`, `git diff`, `git diff --staged`, and `git log -n 10 --oneline` (to match
the repo's style). Read every change; infer the *intent* of each from the diff + this
conversation, not the filenames alone.

## 2. Split by purpose

Group hunks that serve ONE purpose into one commit; split unrelated purposes apart - use
`git add -p` for hunk-level staging. Never `git add -A` / `git add .` - it sweeps in
untracked junk (build artifacts, temp files, local config) you did not mean to commit.

Order commits **lowest-dependency-first** (schema -> domain -> services -> API -> tests ->
docs/chore for a layered repo), leaving the tree buildable at each step. A commit must not
mix feature + fix, or logic + a bulk rename.

## 3. Message - subject line only

`<type>: <message>` - imperative, lowercase, no trailing period, <= 72 chars, **no**
`(scope)`, **no body**. If the subject is not clear alone, sharpen it - don't add a body.

`type`: `feat` | `fix` | `refactor` | `chore` | `docs` | `test` | `perf` | `style` |
`build` | `ci`. Embed the area in the text (`feat: add rate limiting to login`).

**Propose the messages** before running multiple commits; pause if the intent is unclear.

## 4. Commit

Stage exactly the files/hunks for each commit, `git diff --staged` to confirm the scope,
then `git commit -m "<type>: <message>"` (single line, no body). After all commits, show
`git status` + `git log` so the user can verify.

## Rules

- **Never** add `Co-Authored-By` or any Claude / AI attribution to a message.
- No `--amend` / `--no-verify` unless explicitly asked. A failing pre-commit hook -> fix
  the root cause and make a NEW commit, don't bypass it.
- Nothing to commit -> say so, don't make an empty commit. If the diff includes files that
  should stay local (private config, generated artifacts), warn and leave them unstaged.
