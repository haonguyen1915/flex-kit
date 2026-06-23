---
name: architecture-layering
description: Structure code by layers with dependencies pointing inward - domain core, infrastructure at the edge, ports and adapters. This is the principle behind Clean Architecture, Hexagonal (ports & adapters), and Onion architecture. Use when organizing modules, placing a new file, applying Clean/Hexagonal/Onion architecture, or reviewing whether a dependency crosses a layer the wrong way. Not for choosing a pattern (see architecture-design-patterns), a language's concrete layout/DI (see the language pack's <lang>-architecture), or framework wiring.
---

# Layering

Arrange code so business rules don't depend on details. The one rule: **dependencies point
inward**. The domain is the core and knows nothing of the database, the web, or the
framework; those live at the edge and depend on the core, never the reverse.

## The dependency rule

- Inner layers (domain, use cases) must not import outer layers (DB, HTTP, UI). Source-code
  dependencies cross boundaries inward only.
- The flow is `apis -> services / use-cases -> domain <- providers / repositories`. Anything
  inward-importing-outward is a leak to flag.
- Frameworks are details kept at the edge - the core shouldn't be pinned to one.

## Layers

- **Domain** - entities, value objects, business rules. Pure, no I/O.
- **Use cases / services** - orchestrate the domain for one application action; depend on
  *ports*, not concrete infrastructure.
- **Adapters** - controllers (in) and repositories / gateways (out) that translate between
  the outside world and the use cases.
- **Infrastructure** - the DB driver, HTTP server, queue client; wired in at the edge.

## Ports & adapters

- A **port** is an interface the inner layer owns ("save this order"); an **adapter** is the
  outer implementation (Postgres, an HTTP client). The use case depends on the port.
- This inverts the dependency: infrastructure implements an interface the domain defines, so
  the domain stays ignorant of it - and the core becomes testable with a fake adapter.

## Named styles - one principle, many names

Clean Architecture, Hexagonal, and Onion are the **same dependency rule** drawn
differently - learn the rule, not four diagrams.

- **Clean Architecture** (Martin) - concentric rings, `entities -> use cases -> interface
  adapters -> frameworks`. The rings are the layers above; the "dependency rule" is
  deps-inward.
- **Hexagonal / Ports & Adapters** (Cockburn) - the app is a hexagon; each side is a port,
  with a *driving* adapter (UI, test) or *driven* adapter (DB, queue) plugged in.
- **Onion** (Palermo) - domain at the centre, infrastructure as the outer shell.

"Make it hexagonal / clean" means: invert the dependencies onto ports the core owns - the
tool is already above. Don't treat them as different architectures to choose between.

## Crossing boundaries

- Pass simple data across a boundary (a DTO / plain struct), not an ORM row or a framework
  request object - those carry the outer layer inward.
- Map at the edge: a repository turns a DB row into a domain object; a controller turns a
  request into a use-case input.

## Pragmatism

- Layers are a tool, not a tax. A tiny app doesn't need four folders; don't add a port with a
  single adapter that will only ever have one. Add a boundary when something real crosses it.

## Review checklist

- [ ] every dependency points inward; no inner layer imports an outer one
- [ ] the domain has no I/O, framework, or persistence types
- [ ] use cases depend on ports (interfaces), not concrete infrastructure
- [ ] data crossing a boundary is a plain DTO, not an ORM row / request object
- [ ] mapping happens at the edge (repository, controller)
- [ ] the layering is justified by a real boundary, not ceremony

## Red Flags

- a domain file importing the ORM, the web framework, or the HTTP client
- a controller calling the database directly, skipping the use case
- one ORM entity used as the domain model and the API response shape at once
- a port with exactly one adapter that will never have another (premature)
- business rules implemented inside a SQL query or a controller
