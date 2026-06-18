# Scope Challenge

Three questions before planning - answer them before investing research time.

1. **What exists that can be reused?** Check existing code and prior plans. If 80% is
   already done, scope down to the remaining 20%.
2. **What is the minimum viable scope?** Defer what isn't essential. "If we could ship
   only one thing, what would it be?"
3. **What is the actual complexity?** Simple (1-2 files, clear path), moderate (3-6
   files or real unknowns), complex (7+ files, cross-cutting, multiple unknowns).

Map complexity to mode:

- `patch` - simple work only
- `build` - moderate work by default
- `design` - complex, ambiguous, or contract-changing work

## User Decision

Present three options:

- **[E] Expansion** - explore fully, accept the higher scope
- **[H] Hold** - execute as currently scoped
- **[R] Reduction** - cut to essential only

Respect the chosen scope. Raise scope concerns once, then commit - don't silently add
"nice-to-have" steps. Re-challenge only if the complexity estimate proves wrong, a
dependency blocks the critical path, or the user asks.
