---
name: engineering-error-handling
description: Design how a system represents, propagates, and recovers from failure - typed results vs exceptions, an error taxonomy, fail-fast vs recover, and never swallowing context. Use when adding error paths, defining an error type, or reviewing how a change handles failure.
---

# Error Handling Design

Decide how failure is represented and where it's handled *before* scattering try/catch. The
failure mode is the silent swallow - an error caught, logged at debug, and turned into a
default that corrupts state downstream.

## Represent errors deliberately

- Prefer **explicit results** (`Result<T, E>` / a typed return) for expected, recoverable
  failures - they're part of the signature, so callers can't forget them.
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
- A `catch` that drops the error, a `?` / `.ok()` that discards the cause, an empty handler -
  all hide the one fact you'll need at 3am. Log the cause where you handle it, not everywhere.

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

- a `catch` / `except` that logs at debug and returns a default
- a `?` or `.ok()` discarding the cause; an empty catch block
- error handling used as control flow for an ordinary, expected case
- a stringly-typed error the caller must pattern-match on text to handle
- a raw driver or stack error rendered to the end user
