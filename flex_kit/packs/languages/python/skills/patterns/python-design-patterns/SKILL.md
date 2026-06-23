---
name: python-design-patterns
description: Design patterns in their Pythonic form - strategy as a function, factory as a function, adapter, dependency injection by argument, and why singleton is an anti-pattern (a module already is one). Use when choosing a pattern for a local design problem or reviewing over-engineered class hierarchies ported from Java/C++. Not for app-wide layout/layering (see python-architecture) or micro-idioms (see python-idioms).
---

# Python Design Patterns

Most GoF patterns exist to work around limits Python doesn't have. Functions are
first-class, modules are singletons, duck typing makes interfaces implicit - so the
Pythonic form of a pattern is usually **smaller** than the textbook class diagram. Pick a
pattern for the *problem*, then write its lightest Python form.

## Strategy = a function

Don't build a `Strategy` class hierarchy to swap one algorithm. Pass a callable:

```python
from typing import Callable

def apply_discount(price: float, strategy: Callable[[float], float]) -> float:
    return price - strategy(price)

ten_pct = lambda p: p * 0.10            # or a named def
apply_discount(100, ten_pct)
```

A class strategy earns its keep only when the strategy holds state or needs several
methods - otherwise a function (or a `Protocol` if you need a typed family) is enough.

## Factory = a function

A factory is just a function that returns the right object - no `AbstractFactory` class:

```python
def get_localizer(lang: str = "en") -> Localizer:   # Localizer is a Protocol
    return {"en": EnglishLocalizer, "el": GreekLocalizer}.get(lang, EnglishLocalizer)()
```

Use it to centralize a construction choice; return a type that satisfies a `Protocol` so
callers depend on the interface, not the concrete class.

## Adapter

Wrap a foreign object so it satisfies the interface your code expects - the seam that lets
a third-party class fit a `Protocol` port (see python-architecture) without touching it.

```python
class StripeGateway:                  # satisfies your PaymentPort structurally
    def __init__(self, client): self._c = client
    def charge(self, cents: int) -> str:
        return self._c.payments.create(amount=cents).id   # adapt their API to yours
```

## Dependency injection = an argument

Pass dependencies in (constructor or parameter), don't construct them inside. This *is* DI
in Python - no container/framework needed; it's what makes code testable (inject a fake).

```python
class Clock:
    def __init__(self, now: Callable[[], datetime]) -> None:
        self._now = now              # inject real or fake time source
```

## Singleton - don't

A Python **module is already a singleton** (imported once, cached). For "one shared thing",
use a module-level value or inject it from the composition root. A `Singleton` metaclass /
`__new__` trick adds global mutable state and hidden coupling - an anti-pattern here.

## When NOT to pattern

Reach for a pattern only when variation actually exists. A single implementation behind a
factory, a one-method `Strategy` class, or an interface with one impl is **speculative
generality** - delete it. Add the abstraction when the second case arrives, not before.

## Review checklist

- [ ] strategy/callback passed as a function, not a one-method class hierarchy
- [ ] factory is a function returning a `Protocol` type, not an `AbstractFactory`
- [ ] adapters isolate third-party APIs behind your own port interface
- [ ] dependencies injected as arguments; nothing constructs its own collaborators
- [ ] no `Singleton` class - module-level value or injection instead
- [ ] each abstraction has ≥2 real implementations (else it's speculative)

## Red Flags

- a `*Factory`/`*Strategy`/`*Manager` class wrapping a single function's worth of logic
- a `Singleton` metaclass or `__new__` guard (hidden global state)
- an interface/`Protocol` with exactly one implementer and no second in sight
- deep inheritance to share behavior where composition (pass a collaborator) would do
- porting a Java/C++ pattern class-for-class instead of its Python form
