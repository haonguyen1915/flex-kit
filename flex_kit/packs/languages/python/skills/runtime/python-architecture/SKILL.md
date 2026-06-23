---
name: python-architecture
description: How to structure and wire a Python application at runtime - modules as layers with dependencies pointing inward, Protocol as ports, a composition root, config loaded once, and dependency injection done by hand. Use when laying out an app's packages, deciding what imports what, or wiring infrastructure to domain. Not for which design pattern to use locally (see python-design-patterns) or build files/tooling (see python-project).
---

# Python Architecture

The **runtime** shape of an app: how packages divide into layers, which way imports
point, and where everything gets wired. The one rule everything else serves:
**dependencies point inward** - the domain depends on nothing; infrastructure depends
on the domain, never the reverse.

## Modules as layers

Split by responsibility, inner to outer:

```
src/app/
├─ domain/         pure business logic + entities. Imports NOTHING from outer layers.
├─ service/        use-cases: orchestrate domain + ports. Imports domain only.
├─ adapters/       concrete I/O: db repo, http client, queue. Implements the ports.
└─ entrypoints/    cli / web / worker - the thin shell that calls a service.
```

A layer may import only *inward* (`adapters` → `service` → `domain`). If `domain`
needs to import `adapters`, the dependency is backwards - invert it with a port.

## Ports = Protocol

A **port** is an interface the inner layer *owns* and the outer layer *implements*.
Declare it where it's used (the service), as a `Protocol` - structural typing means the
adapter satisfies it without importing or subclassing anything:

```python
# service/ports.py  - owned by the inner layer
from typing import Protocol

class OrderRepo(Protocol):
    def get(self, ref: str) -> Order | None: ...
    def add(self, order: Order) -> None: ...

# service/place_order.py  - depends on the port, never a concrete repo
def place_order(repo: OrderRepo, ...) -> ...:
    ...
```

`adapters/sql_repo.py` just *has* those methods - no import of the service, no ABC.
This is dependency inversion: the arrow points from adapter → port, i.e. inward. (A
`Protocol` is the Pythonic default; reach for `abc.ABC` only when you also need shared
behavior or runtime `isinstance` enforcement.)

## Composition root

Construct concrete adapters and inject them in exactly **one** place - a `bootstrap()` /
`main()` at the entrypoint. Nothing inner constructs its own dependencies; they arrive
as arguments. DI is plain function/constructor arguments - no framework needed.

```python
# entrypoints/bootstrap.py - the ONLY place that knows concrete types
def bootstrap(repo: OrderRepo | None = None) -> Service:
    repo = repo or SqlOrderRepo(make_session())   # real default
    return Service(repo=repo)                      # inject downward
```

Tests pass a fake repo to the same seam - same code, infrastructure swapped. See
[references/layered-example.md](references/layered-example.md).

## Config

Load and validate configuration **once**, at the composition root, into a typed object
(a `pydantic` `BaseSettings` or a frozen `@dataclass`). Pass the values inward as
arguments; never read `os.environ` deep in the domain - that hides a dependency and
makes the code untestable.

## Review checklist

- [ ] imports point inward only; `domain/` imports no outer layer
- [ ] interfaces (`Protocol`) declared by the consumer, implemented by the adapter
- [ ] one composition root constructs concretes; inner layers receive deps as args
- [ ] config loaded + validated once at the edge, passed inward as a typed object
- [ ] entrypoints are thin - they call a service, they don't hold business logic

## Red Flags

- `domain/` or `service/` importing `sqlalchemy`, `requests`, `flask`, … (infra leaking in)
- a class constructing its own DB session / HTTP client instead of receiving it
- `os.environ[...]` or global config read from inside business logic
- business rules living in a Flask/FastAPI route or a CLI handler
- a circular import between two layers - the dependency direction is wrong
