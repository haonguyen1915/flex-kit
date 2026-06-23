---
name: python-idioms
description: Idiomatic Python - comprehensions, context managers, EAFP over LBYL, dataclasses, pathlib, f-strings, generators, and the mutable-default-arg trap. Use when the user writes or reviews Python code or asks "is this pythonic". Not for naming (see python-naming) or type hints (see python-typing).
---

# Python Idioms

Pythonic code uses the language's grain - comprehensions, managers, and the standard
library - instead of porting patterns from other languages.

## Expressions over loops

- Comprehensions for transform/filter: `[x * 2 for x in items]` over a `for` + `append`.
- Generators (`(… for …)`, `yield`) for large or streamed sequences - don't materialize a
  huge list you iterate once.
- f-strings for formatting: `f"user {name} ({age})"`, not `%` or `.format`.

## Resources & data

- Context managers for anything that opens/closes: `with open(...) as f:`; write
  `@contextmanager` for custom setup/teardown.
- `@dataclass` instead of a hand-written `__init__` + `__repr__` + `__eq__`.
- `pathlib.Path` over string path math: `Path(base) / name`, `.exists()`, `.read_text()`.

## Style

- **EAFP** over LBYL - `try: x[k] except KeyError:` rather than `if k in x:` (avoids the race
  and reads better).
- Catch specific exceptions, never a bare `except:` (it swallows `KeyboardInterrupt`).
- Use `logging`, not `print`, for anything diagnostic.

## Review checklist

- [ ] comprehensions / generators instead of manual accumulation loops
- [ ] `with` for resources; `@dataclass` for plain data holders
- [ ] `pathlib` and f-strings, not string paths / `%` formatting
- [ ] EAFP with specific `except`; no bare `except:`
- [ ] `logging` over `print` for diagnostics

## Red Flags

- a mutable default arg: `def f(items=[])` (shared across calls - use `None` sentinel)
- `bare except:` swallowing everything
- a `for` + `append` where a comprehension fits
- string concatenation to build filesystem paths
- `print` used as application logging
