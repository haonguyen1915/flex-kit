---
name: rust-idioms
description: Idiomatic Rust - ownership and borrowing, Option/Result handling, iterators over manual loops, traits and conversions, when to clone. Use when the user writes or reviews Rust code, asks "is this idiomatic", or fights the borrow checker. Not for naming (see rust-naming) or error-type design (see rust-error-handling).
---

# Rust Idioms

Idiomatic Rust leans on the type system and ownership rather than working around them.
Reach for the borrow checker's grain, not against it.

## Ownership & borrowing

- Take `self` to consume, `&mut self` to modify, `&self` to read - pick the weakest that works.
- Pass `&T` / `&str` / `&[T]` to read; return owned values; don't return a reference to a local.
- Builders consume and return `self` for chaining.

## Option & Result

- `Option<T>` for present/absent; `Result<T, E>` for fallible. Match or combinator
  (`map`, `and_then`, `unwrap_or`) - don't `.unwrap()` in production code.
- Use `?` to propagate; `if let` / `let else` to handle one arm cleanly.

## Iterators over loops

- Prefer `iter().map().filter().collect()` to a manual `for` + `push`; it fuses and reads better.
- `iter()` borrows, `iter_mut()` borrows mutably, `into_iter()` consumes - pick by what you need next.

## Traits & conversions

- Implement `From`/`TryFrom` (and get `Into`/`TryInto` free); accept `impl AsRef<str>` /
  `impl IntoIterator` to be flexible at call sites.
- Define a small capability trait when you have 2+ implementations; default methods only when truly generic.
- Clone deliberately - cheap in a constructor, a smell in a hot loop. Prefer borrowing.

## Review checklist

- [ ] the weakest sufficient receiver (`&self` over `&mut self` over `self`)
- [ ] no `.unwrap()` / `.expect()` in production paths
- [ ] iterator chains instead of manual index loops
- [ ] conversions via `From`/`TryFrom`; flexible `impl AsRef`/`IntoIterator` args
- [ ] clones justified, not scattered through a hot path

## Red Flags

- `.unwrap()` / `.expect()` outside tests or provably-infallible code
- returning a reference to a value owned by the function
- a manual `for` loop building a `Vec` that `map`/`filter`/`collect` would express
- an over-generic trait with no bounds, producing cryptic errors
- `.clone()` sprinkled to silence the borrow checker instead of restructuring
