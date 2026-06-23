---
name: python-error-handling
description: How Python code should fail - a package exception hierarchy, chaining with `raise ... from`, catching narrowly at the right boundary, try/except/else/finally, and when to return a Result instead of raising. Use when writing error paths, designing exceptions, or reviewing code that catches/swallows errors. Not for general idioms (see python-idioms) or where layers sit (see python-architecture).
---

# Python Error Handling

Errors are part of the contract. Code should fail **loudly, with context, at the layer
that can decide what to do** - never swallow, never lose the cause.

## A package exception hierarchy

Give a package one base exception; raise subclasses for distinct failures. Callers can
then catch your whole package (`except ShopError`) or one precise case
(`except OrderNotFound`) - and never have to catch bare `Exception`.

```python
class ShopError(Exception): ...              # the package root
class OrderNotFound(ShopError): ...          # a specific, catchable failure
class PaymentDeclined(ShopError): ...
```

Subclass a built-in only when it *is* that thing (`ValueError`, `KeyError`); otherwise
inherit your own base.

## Chain - never lose the cause

When you translate a low-level error into a domain one, use `raise ... from` so the
original traceback survives:

```python
try:
    row = db.fetch(ref)
except sqlite3.OperationalError as exc:
    raise OrderNotFound(ref) from exc       # __cause__ keeps the real cause
```

A bare `raise` (no args) inside `except` re-raises the current exception unchanged -
use it to add a log/cleanup then propagate, not to wrap.

## Catch narrowly, at a boundary

- Catch the **most specific** type you can handle; let everything else propagate.
- Catch at a **boundary** that can actually decide (a request handler, a retry loop, the
  composition root) - not three frames deep where you only have half the context.
- Use `try/except/else/finally`: put the risky call in `try`, the success path in
  `else` (so you don't accidentally catch errors from it), cleanup in `finally`.
- `with contextlib.suppress(FileNotFoundError):` for the rare "genuinely ignore this".

## Raise vs return a Result

Raise for the **exceptional**; return a value for an **expected** outcome that the
caller routinely branches on. "User not found" on a lookup is often a normal result
(return `None` or a typed `Result`), whereas a corrupt database is exceptional (raise).
Don't use exceptions for ordinary control flow that runs on every call.

## Review checklist

- [ ] a package base exception; specific subclasses for distinct failures
- [ ] every wrap uses `raise NewError(...) from exc` - cause preserved
- [ ] `except` names a specific type, not bare `except:` / `except Exception`
- [ ] errors caught at a boundary that can act, not swallowed deep inside
- [ ] expected outcomes returned (None/Result); only the exceptional raises
- [ ] cleanup in `finally` / a context manager, not duplicated on each path

## Red Flags

- `except Exception: pass` or `except: pass` - a silently swallowed error
- `except ...: return None` that erases the cause a caller needed
- re-wrapping without `from exc` (traceback shows "During handling… another exception")
- logging an error *and* re-raising it at every layer (duplicate noise) - log once, at the edge
- exceptions used as normal control flow (raising on every lookup miss)
