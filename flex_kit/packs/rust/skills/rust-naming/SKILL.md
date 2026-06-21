---
name: rust-naming
description: Rust naming conventions - casing per item kind, intention-revealing names, boolean predicates, unit suffixes. Use when the user names or renames Rust functions, types, variables, modules, or asks to review Rust names, or when a name is vague, abbreviated, or non-idiomatic. Not for non-Rust code or API / error design.
---

# Rust Naming

A name should answer *why it exists and what it does* without a comment. Match rustc's
casing, then spend the words on intent.

## Casing (rustc-enforced)

- `snake_case` - functions, variables, modules.
- `UpperCamelCase` - types, structs, enums, traits.
- `SCREAMING_SNAKE_CASE` - constants and statics.
- Generic params single uppercase (`T`, `K`, `V`, `E`); lifetimes short lowercase (`'a`, `'ctx`).

## Intent over brevity

- Searchability scales with scope: `i` is fine in a tiny loop; a module constant needs
  `MAX_RETRY_ATTEMPTS`. Spell out `request`, `query` - not `r`, `q`.
- No noise words - `Info`, `Data`, `Manager`, `Helper` distinguish nothing; use `Summary`,
  `Detail`, `Repository`.
- One verb per concept: don't use `add` for both "concatenate" and "insert".

## Conventions

- Booleans read as predicates: `is_`, `has_`, `can_`, `should_`; avoid negatives
  (`is_enabled`, not `is_disabled`).
- Put units on numerics: `delay_ms`, `timeout_secs`, `size_bytes` (or a newtype).
- Conversion methods: `as_x` (cheap ref), `to_x` (alloc), `into_x` (consumes), `try_x` (fallible).

## Review checklist

- [ ] casing matches the item kind (rustc convention)
- [ ] names reveal intent; no single letters outside tiny scopes
- [ ] no noise words (`Data`, `Manager`, `Helper`)
- [ ] booleans are positive predicates; numerics carry units
- [ ] one verb per concept across the module

## Red Flags

- Hungarian / encoding prefixes (`str_`, `vec_`, `m_`, `I` on traits)
- single-letter names outside loops forcing mental translation
- cute names (`whack()`, `nuke()`) hiding the real operation
- a project prefix on every type (`GsdAccount`) instead of a module (`gsd::Account`)
- a numeric param with no unit (`delay: u64`)
