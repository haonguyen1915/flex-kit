---
name: typescript-idioms
description: Idiomatic TypeScript - async/await over .then, optional chaining and nullish coalescing, exhaustive switch, unions over enums, named imports, as const. Use when the user writes or reviews TS/JS runtime code or asks "is this idiomatic". Not for type design (see typescript-types) or naming (see typescript-naming).
---

# TypeScript Idioms

Lean on the modern language: less ceremony, fewer footguns, and let the compiler check the
edges.

## Async

- `async/await` over `.then()` chains for sequential work; `Promise.all` for independent
  work in parallel. Don't mix a top-level `.then()` inside an `async` function.

## Null & access

- Optional chaining `obj?.prop` and nullish coalescing `x ?? fallback` (right side only on
  `null`/`undefined`, *not* on falsy `0`/`""`).
- Standardize on `undefined` for absence; don't mix `null` and `undefined`.
- Guard array access: `items[i]?.prop ?? fallback`, not an unchecked `items[i]`.

## Control flow & modules

- Exhaustive `switch` on a discriminated union - the compiler flags a missed case (add a
  `never` default to enforce it).
- Prefer string-literal **unions over `enum`** - structural, simpler, tree-shakeable.
- Named imports/exports (no `import *`) for tree-shaking and traceable dependencies.
- `as const` for literal config; destructure complex shapes once into named consts.

## Review checklist

- [ ] `await` (or `Promise.all`) instead of `.then` chains in async code
- [ ] `?.` / `??` used; absence is consistently `undefined`
- [ ] array access guarded, not unchecked
- [ ] `switch` on unions is exhaustive (`never` default)
- [ ] string-literal unions instead of `enum`; named imports, no `import *`

## Red Flags

- a `.then()` chain inside an `async` function
- `x ?? y` swapped for `x || y` where `0` / `""` is valid
- `enum` for a closed set a union would model
- `import * as X` hiding the actual dependencies
- `items[i].prop` with no bounds / nullish guard
