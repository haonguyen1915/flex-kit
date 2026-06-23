---
name: architecture-design-patterns
description: Design patterns and anti-over-engineering heuristics, language-agnostic - when to apply a pattern (and when not), SOLID pragmatically, coupling/cohesion, composition over inheritance, GoF patterns with real triggers. Use when choosing a pattern, reviewing a structure, or resisting premature abstraction. Not for naming or a language's idioms (see the language pack).
---

# Design Patterns

Patterns are names for recurring shapes of code. They earn their keep only when the problem
they solve actually exists. The dominant failure is the opposite: applying a pattern to
prevent a problem that never arrives - trading present simplicity for speculative
abstraction. Start simple; extract the shape when it appears a third time.

## When to apply a pattern

- **Rule of three.** One or two call sites: don't extract - indirection costs more than it
  saves. Wait until the same shape appears in three independent places.
- **Name the problem first.** If you can't state the problem in one sentence ("this `if` on
  `kind` grows an arm per type"), the pattern isn't needed yet. YAGNI: build for now,
  refactor when reality diverges from the guess.
- **Reduce complexity, don't move it.** A pattern that centralizes real logic (validation, a
  protocol) earns its place; one that just wraps a constructor relocated complexity without
  removing it.
- **Match the codebase over the textbook.** Consistency with how this project already does it
  beats textbook elegance. A lone factory in a codebase of plain constructors is churn.

## SOLID, pragmatically

- **Single responsibility** - one reason to change. Split a type that changes for two
  *unrelated* reasons (domain logic vs serialization); don't split when both share a source.
- **Open/closed** - add behavior with new code, not by rewriting existing code. Reach for
  composition + injection, not an inheritance hierarchy.
- **Liskov** - a subtype must work anywhere its base does without breaking the contract. A
  violation usually means inheritance was the wrong tool.
- **Interface segregation** - clients shouldn't depend on methods they don't call. Split a
  broad interface whose callers each use only one slice.
- **Dependency inversion** - depend on abstractions; pass dependencies in, never reach for a
  global or singleton. This is what makes code testable.

## Coupling & cohesion

- **High cohesion** - keep a feature's pieces together. A module owning a vertical slice
  (logic + persistence + API) beats one feature scattered across `controllers/`, `services/`,
  `models/`.
- **Low coupling** - depend on an interface, not a concrete type; cross-module talk goes
  through events / ports, not by reaching into internals.
- **Acyclic dependencies** - no `A -> B -> A`. Break a cycle by having one side expose an
  interface the other depends on.
- **Boundaries follow the domain, not the layer** - "user management" owns its own logic,
  storage, and API; don't carve modules by technical role alone.

## Composition over inheritance

- Inheritance locks an object into one hierarchy; composition lets it *have* a logger, a retry
  policy, a cache - and gain another without a redesign.
- Define the interface a consumer needs, then pass in something that implements it - real in
  production, a fake in tests.
- Avoid god objects and hierarchies past ~3 levels deep; both are hard to test and change.
- Use inheritance only when substitutability is genuine ("every B truly is an A").

## GoF patterns - real triggers

Reach for one only at its trigger; otherwise a plain function / struct is simpler.

| Pattern | Use when (the real trigger) |
|---|---|
| **Factory** | creation picks a subtype or runs non-trivial init - not to hide a constructor |
| **Builder** | an object has many optional fields or cross-field validation (8+); not for a 3-field DTO |
| **Singleton** | avoid - use injection; a "needed global" is usually a missing boundary |
| **Adapter** | make a fixed external interface fit yours ("can't change it, my code expects another shape") |
| **Decorator** | add logging / caching / validation around a core op without changing it |
| **Facade** | hide a many-entry subsystem behind one simple surface - not to wrap a single object |
| **Strategy** | a big `if/else` on a parameter chooses among algorithms - swap to strategy objects |
| **Observer / pub-sub** | one change must fan out to many, decoupled (events, model -> view) |
| **State** | behavior changes by state with clear transitions (orders, payments, workflows) |
| **Command** | operations need queuing, undo, or logging as first-class objects |

## Review checklist

- [ ] solves a problem that exists *now*, not a hypothetical future one
- [ ] the shape repeats 3+ times (not speculative abstraction)
- [ ] reduces total complexity rather than relocating it
- [ ] module boundaries follow the domain; dependencies are acyclic
- [ ] composed, not inherited - or inheritance is justified by real substitutability
- [ ] testable without mocking internals or globals
- [ ] consistent with the codebase's existing style

## Red Flags

- a wrapper class that only delegates to the thing it wraps
- factory-for-a-factory: creation machinery heavier than what it creates
- a builder for a trivial object; a singleton or a mutable global
- an interface with 15+ methods no client uses in full
- an inheritance hierarchy deeper than 3 levels, or a circular dependency
- elaborate test setup needed to verify one behavior (the design is too coupled)
