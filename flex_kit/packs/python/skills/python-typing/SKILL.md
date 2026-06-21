---
name: python-typing
description: Python type hints - annotate public signatures, T | None for optional, Protocol for structural typing, TypedDict, Literal, and avoiding Any. Use when the user adds or reviews Python type hints, mypy errors, or designs typed interfaces. Not for naming (see python-naming) or general idioms (see python-idioms).
---

# Python Typing

Type hints are documentation the checker enforces. Annotate the surface others call;
internal trivial helpers can stay bare.

## Annotate the surface

- Type every public function signature - params and return. `def fetch_user(user_id: str)
  -> User:`. A missing return type leaves callers guessing.
- Add `from __future__ import annotations` so hints are lazy strings (forward refs work, no
  import-order pain).

## Optional & unions

- Mark nullable explicitly: `T | None` (3.10+) over `Optional[T]`; pick one style per codebase.
- `Literal["active", "inactive"]` for a closed set of constants, instead of a bare `str`.

## Structural typing

- `Protocol` for duck-typed interfaces - anything with `.read()` satisfies `SupportsRead`
  without inheriting a base.
- `TypedDict` to type the shape of a dict you pass around, without a full class.

## Avoid `Any`

- `Any` turns checking off. Prefer a `Protocol`, `TypedDict`, or `object` + a narrow. Never
  `list[Any]` / `dict[str, Any]` for data you own - model the shape.

## Review checklist

- [ ] public signatures fully annotated (params + return)
- [ ] `from __future__ import annotations` at the top
- [ ] nullable is explicit `T | None`; closed sets use `Literal`
- [ ] duck-typed interfaces are `Protocol`; dict shapes are `TypedDict`
- [ ] no `Any` for data you own (no `list[Any]` / `dict[str, Any]`)

## Red Flags

- a public function with no return annotation
- `list[Any]` / `dict[str, Any]` for your own structured data
- mixing `Optional[T]` and `T | None` across the codebase
- a base class used only to fake an interface where a `Protocol` fits
- `Any` sprinkled to silence mypy instead of narrowing
