---
name: svelte-naming
description: Svelte naming conventions - PascalCase component files, camelCase props with is/has boolean prefixes, snippet names by purpose, use* hooks, store getters without underscores. Use when the user names or reviews Svelte components, props, snippets, stores, or hooks. Not for runes (see svelte-runes) or the component API (see svelte-components).
---

# Svelte Naming

Consistent names make a component tree readable at a glance. These build on
`typescript-naming` - the Svelte-specific parts are files, snippets, stores, and hooks.

## Files

- Components are `PascalCase.svelte`, one component per file (`QueryEditor.svelte` exports
  `<QueryEditor>`). Sub-components go in a folder.
- Utils / stores / hooks are `kebab-case`: `query-builder.ts`, `connection.store.svelte.ts`.

## Props & handlers

- Props are `camelCase`; boolean props are predicates (`isLoading`, `hasError`).
- Event props `on{Event}` (`onSelect`); internal functions `handle{Event}` (`handleSelect`).

## Snippets, stores, hooks

- Snippet names describe purpose: `header`, `emptyState`, `actionBar` - not `slot1` / `content`.
- Store exposes named getters without an underscore (`connectionStore.connections`); mutations
  are verbs (`add`, `remove`, `setActive`). Keep internal `$state` encapsulated.
- Hooks follow `use{Capability}`: `useDebounce`, `useClickOutside` (file `kebab-case`, export
  `camelCase`).

## Review checklist

- [ ] components `PascalCase.svelte`, one per file
- [ ] props `camelCase`, boolean props predicate-prefixed
- [ ] `on*` props vs `handle*` internal, consistent
- [ ] snippets named by purpose; hooks `use*`
- [ ] store exposes getters/verbs, internal state not leaked

## Red Flags

- a lowercase component file (`query-editor.svelte`)
- generic snippet names (`slot`, `content`)
- a store's internal `_state` accessed from outside
- mixed `on*` / `handle*` for the same layer
- abbreviated service / store members (`conns`, `q`, `conn_id`)
