---
name: flex-fix
description: Quick bug-to-patch path - reproduce, diagnose the root cause, patch in patch mode, then verify. Use for a small, well-scoped bug fix rather than a full plan.
argument-hint: [bug description]
---

Fix a bug fast and tight: **$ARGUMENTS**

1. **Reproduce.** Establish the failing behavior - a failing test, a command, or
   exact steps. If you cannot reproduce it, say so and ask for detail; do not guess.
2. **Diagnose.** Spawn the `debugger` agent to find the *root cause* (not the symptom);
   it reproduces, tests ranked hypotheses, and reports the cause + recommended fix
   without changing code. State the root cause in one line.
3. **Plan (patch).** Run `flex-kit plan "<bug>" --mode patch` and write the fix as one
   or two concrete steps. If it grows past patch scope (more than ~2 files, or a
   contract change), STOP - this is not a quick fix; switch to `/flex-change`.
4. **Patch.** Spawn the `implementer` for the minimal change. Add or adjust a test
   that fails before the fix and passes after.
5. **Verify.** Apply the `process-verify-fix-loop` skill (`reviewer` + `tester`). When clean,
   summarize the root cause and fix, then offer `/flex-close`.

Keep it minimal: a patch that needs a spec or touches contracts is no longer a fix.
