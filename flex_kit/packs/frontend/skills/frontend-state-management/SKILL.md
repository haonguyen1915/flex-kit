---
name: frontend-state-management
description: Decide where UI state lives and how it flows - local vs shared vs server state, derived over duplicated, a single source of truth, and avoiding prop drilling. Use when adding state, choosing a store, or untangling state that's duplicated or out of sync.
---

# Frontend State Management

Most state bugs are really *placement* bugs: the same fact stored in two places that drift,
or state hoisted into a global that one component needed locally. Decide where each piece of
state belongs before reaching for a store.

## Classify the state

- **Local** - used by one component (an input's text, a toggle). Keep it in the component;
  don't globalize it.
- **Shared (client)** - used across components (the open route, a theme, a selection). Lift
  to the nearest common ancestor, or a store if many distant consumers need it.
- **Server** - data owned by the backend (lists, entities). It is a *cache*, not state you
  own - use a server-cache layer (a query library) with keys, staleness, and invalidation,
  not a hand-rolled global.

## Single source of truth

- Each fact lives in exactly one place; everything else **derives** from it. Don't copy
  server data into a local field that then drifts.
- **Derive, don't duplicate** - a filtered list, a total, an `isValid` flag are computed
  from source state, not stored alongside it and kept in sync by hand.

## Flow & boundaries

- Read-only derivations are pure; side effects (fetch, subscribe, persist) live in effects,
  not in render or in a derivation.
- Avoid prop drilling 4+ levels - use composition (pass the rendered child) or context for
  genuinely cross-cutting values (theme, auth), not for everything.
- A store is for *shared* state with many consumers; don't put one component's local state
  in a global store because it's convenient.

## Mutations

- Change state through one path (an action / reducer / setter), not from scattered call
  sites - one writer makes changes traceable.
- After a server mutation, invalidate the cache that reads it; don't manually patch a copy.

## Review checklist

- [ ] each state lives at the lowest scope its consumers share (not globalized by default)
- [ ] server data is a cache (keys + invalidation), not hand-rolled global state
- [ ] derived values are computed, not duplicated and synced by hand
- [ ] one source of truth per fact
- [ ] cross-cutting context used sparingly; prop drilling not 4+ levels
- [ ] mutations go through one writer; server mutations invalidate their cache

## Red Flags

- the same data stored in a store and a local field, kept in sync manually
- a local toggle lifted into a global store
- server data copied into client state then patched on every change
- a derived value (total, filtered list) stored instead of computed
- effects (fetch / subscribe) running inside render or a pure derivation
