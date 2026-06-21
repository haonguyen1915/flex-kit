---
name: architecture-domain-modeling
description: Model a domain so code mirrors the business - entities vs value objects, aggregates and invariants, bounded contexts, ubiquitous language. Use when designing domain types, or when business rules leak into controllers, DB rows, or the UI. Not for DB schema design (see database-) or a language's type syntax.
---

# Domain Modeling

Model the domain in types so the rules live in one place and the code reads like the
business. The failure mode is an *anemic model* - data bags with all the logic in services -
which scatters invariants and lets any caller build an invalid state.

## Entities vs value objects

- **Entity** - has identity that persists through change (a `User`, an `Order`); two entities
  with the same fields are still different. Identity = a stable id, not the fields.
- **Value object** - defined entirely by its values, immutable, no identity (`Money`,
  `DateRange`, `Email`). Equal fields means equal. Prefer them - they're safe to share.
- Kill primitive obsession: a raw `string` email or `int` cents invites bad data. Wrap it in
  a value object that validates on construction.

## Aggregates & invariants

- An **aggregate** is a cluster of objects changed as a unit, with one **root** as the only
  entry point. Outside code holds the root and never reaches inside.
- Invariants (rules that must always hold) are enforced inside the aggregate on every
  mutation - not in a service a caller might skip. An invalid aggregate cannot exist.
- Keep aggregates small. If two things needn't be consistent in the same transaction, they
  are separate aggregates referencing each other by id.

## Bounded contexts

- The same word means different things in different contexts ("customer" in billing vs
  support). Don't force one shared model - draw a boundary and translate at the edge.
- Each context owns its model and language; integrate through explicit contracts (events,
  APIs), not a shared database.

## Ubiquitous language

- Name types and methods with the domain's own words; if the business says "settle", the code
  says `settle()`, not `updateStatus(2)`.
- A term the code and the experts use differently is a bug waiting to happen - align them.

## Keep the domain pure

- Domain types hold business logic and invariants only - no SQL, no HTTP, no framework
  annotations, no serialization flags leaking in.
- Persistence and transport map *to* the domain at the boundary; the domain doesn't know they
  exist.

## Review checklist

- [ ] behavior lives on the types that own the data, not in anemic service bags
- [ ] invariants are enforced inside an aggregate root, impossible to bypass
- [ ] value objects wrap meaningful primitives (money, ids, email) + validate on construction
- [ ] aggregates are small; cross-aggregate links are by id, not object reference
- [ ] names match the domain's language
- [ ] no infrastructure (DB / HTTP / framework types) leaks into domain types

## Red Flags

- an entity that is just public fields with all logic in a `*Service`
- a setter that can put the object into an invalid state
- a primitive `string` / `int` standing in for money, ids, emails, or dates
- one giant model shared across unrelated contexts
- domain types importing the ORM, the web framework, or serialization annotations
