---
name: rust-error-handling
description: Rust error handling idioms - Result and the ? operator, thiserror for libraries vs anyhow for apps, cause-named error enums, and #[from] conversions. Use when the user defines a Rust error type, propagates errors, picks thiserror/anyhow, or reviews Rust error paths. Not for the general error-design principles (see engineering-error-handling) or non-Rust code.
---

# Rust Error Handling

This is the Rust *expression* of `engineering-error-handling` - the same taxonomy and
fail-fast principles, applied with Rust's `Result`, `?`, and error enums.

## Result & ?

- Every fallible function returns `Result<T, E>` - never a bare `bool` for success/failure.
- Propagate with `?`; it preserves the cause and removes nested `match`. Reserve `panic!`/
  `unwrap` for bugs and provable invariants, not expected failure.

## Error types: thiserror vs anyhow

- **Libraries → `thiserror`.** Define a `#[derive(thiserror::Error)]` enum so callers can
  match and recover specific variants. Don't force `anyhow` on your consumers.
- **Applications / binaries → `anyhow`.** Use `anyhow::Result` at the top level for easy
  context; convert to a domain error at API boundaries.

## Error enums

- Name variants by **cause**, not symptom: `ConnectionRefused`, `Unauthorized` - not
  `BadConnection`. Each variant is a distinct, recoverable failure mode.
- Annotate `#[from]` on wrapping variants to auto-convert with `?` and drop `.map_err` noise.
- Add context with `.context("…")` (anyhow) or a dedicated variant; keep the cause chain.

## Review checklist

- [ ] fallible functions return `Result`, propagate with `?`
- [ ] no `unwrap`/`expect` in production paths (only tests / proven invariants)
- [ ] libraries use `thiserror`; apps use `anyhow` - not the reverse
- [ ] variants named by cause; `#[from]` used for conversions
- [ ] context added on propagation; cause chain preserved

## Red Flags

- `anyhow` in a library crate (forces it on every caller)
- a fallible op returning `bool` or a bare `String` instead of a typed error
- `match … { _ => panic!() }` swallowing real errors
- error variants named by symptom, or a new wrapper enum at every layer
- `unwrap()` on a `Result` that can fail at runtime
