---
name: python-naming
description: Python naming per PEP 8 - snake_case, PascalCase, UPPER_SNAKE, leading-underscore privacy, dunder protocol methods, boolean predicates, unit suffixes. Use when the user names or reviews Python functions, classes, variables, modules, or when a name breaks PEP 8 or is abbreviated. Not for non-Python code or typing (see python-typing).
---

# Python Naming

PEP 8 fixes the casing; spend the rest on intent. Linters enforce most of this - match it
so the code reads as written by one hand.

## Casing (PEP 8)

- `snake_case` - modules, functions, variables.
- `PascalCase` - classes.
- `UPPER_SNAKE_CASE` - constants.

## Privacy & protocol

- Leading `_name` marks "internal" (convention, not enforced). Reserve `__name`
  (name-mangling) for the rare case you truly need it.
- Double-underscore `__init__`, `__repr__`, `__eq__` are the data-model protocol - don't
  invent your own dunders.

## Intent

- Booleans as predicates: `is_valid`, `has_errors`, `can_submit`; avoid negatives.
- Units on numerics: `delay_ms`, `timeout_secs`, `size_bytes`.
- No noise words (`Info`, `Data`, `Manager`, `Helper`); spell out scope names - `user`, not `usr`.
- Semantic names over numeric suffixes: `primary_user` / `secondary_user`, not `user_1` / `user_2`.

## Review checklist

- [ ] casing follows PEP 8 per kind
- [ ] `_` for internal; `__` only where mangling is needed
- [ ] booleans are positive predicates; numerics carry units
- [ ] no noise words; no module-scope abbreviations
- [ ] custom dunders not invented

## Red Flags

- `camelCase` functions or variables (not PEP 8)
- `_`-prefixed names used as the real public API
- abbreviations in module scope (`usr`, `conn`, `db`)
- numeric suffixes (`user_1`, `user_2`) instead of roles
- a hand-rolled `__special__` method name
