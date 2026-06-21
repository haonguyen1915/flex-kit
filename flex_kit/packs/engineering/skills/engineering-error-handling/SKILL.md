---
name: engineering-error-handling
description: Design a system's error strategy, language-agnostic - typed results vs exceptions, an error taxonomy, fail-fast vs recover, boundaries, never swallowing context. Use when deciding how errors are represented and handled across a codebase, or reviewing that design. For a language's idiom (Rust ?/thiserror, Python exceptions), use the matching <lang>-error-handling skill.
---

# Error Handling Design

Decide how failure is represented and where it's handled *before* scattering error handling.
The failure mode is the silent swallow - an error caught, logged at debug, and turned into a
default that corrupts state downstream.

The *language idiom* for this - Rust's `?` + `thiserror`, a TypeScript result type, Python
exceptions - lives in the matching `<lang>-error-handling` skill; here is the design that
holds across all of them.

## Represent errors deliberately

- Prefer an **explicit result** (a typed return value the caller must handle) for expected,
  recoverable failures - it's part of the signature, so callers can't forget it.
- Reserve **exceptions / panics** for truly exceptional, unrecoverable conditions (bugs,
  invariant violations). Don't use them for ordinary control flow.
- Make the error a **type**, not a bare string - a code or enum the caller can branch on,
  with a human message attached. A string can only be logged, not handled.

## Error taxonomy

- Separate **caller errors** (bad input -> reject, 4xx) from **system errors** (a dependency
  failed -> retry / alert, 5xx) from **bugs** (an impossible state -> crash + fix). Each is
  handled differently.
- A stable error **code** is part of your contract - clients and logs branch on it. Adding a
  variant is safe; renaming one breaks consumers.

## Fail fast, recover deliberately

- Validate at the boundary and reject early; don't let bad data flow inward to fail
  mysteriously three layers down.
- Recover only where you can do something meaningful (a retry, a fallback, a user message).
  Elsewhere, propagate - don't catch just to re-throw something vaguer.

## Never lose context

- When propagating, **wrap with context** ("loading user 42: <cause>") and keep the cause
  chain - don't replace the original error with a generic one.
- An error dropped on the floor - swallowed in a catch, converted to a bare optional, or an
  empty handler - hides the one fact you'll need at 3am. Log the cause where you handle it,
  not everywhere.

## Boundaries

- Translate errors at each boundary: a domain error becomes an HTTP status at the API edge, a
  driver error becomes a domain error at the repository. Don't leak driver errors outward.
- Never expose internals (stack traces, raw SQL, connection details) in a user-facing error.

## Review checklist

- [ ] expected failures are typed results; exceptions reserved for the exceptional
- [ ] errors carry a code / variant callers can branch on, not just a message
- [ ] input is validated and rejected at the boundary (fail fast)
- [ ] propagation wraps with context and preserves the cause chain
- [ ] nothing is caught-and-swallowed or converted to a silent default
- [ ] errors are translated at boundaries; no internals leak to the user

## Red Flags

- a handler that logs at debug and returns a default
- the cause discarded - error converted to a bare optional, or an empty catch block
- error handling used as control flow for an ordinary, expected case
- a stringly-typed error the caller must pattern-match on text to handle
- a raw driver or stack error rendered to the end user
