---
name: svelte-components
description: Svelte 5 component API - $props() with an interface, $bindable() for two-way binding, snippets over slots, callback props over createEventDispatcher, onclick over on:click. Use when the user writes or reviews a Svelte 5 component's props, events, or content composition. Not for reactivity (see svelte-runes) or naming (see svelte-naming).
---

# Svelte 5 Components

Svelte 5 replaces the Svelte 4 component API. Props, events, and content all flow through
runes and snippets now - use them, don't mix in the old syntax.

## Props

- `let { label, disabled = false }: Props = $props()` with an `interface Props { … }` -
  not `export let`.
- `$bindable()` for a two-way prop: `let { value = $bindable() } = $props()` so a parent can
  `bind:value`. Without it, `bind:` fails silently.
- Don't mutate a prop directly; copy into local `$state` if you need a local edit.

## Events

- Pass **callback props**, not `createEventDispatcher`: accept `onSelect?: (id: string) =>
  void` and call it. Simpler, typed, traceable.
- Use HTML attributes `onclick={handle}` - not the Svelte 4 `on:click` directive.

## Content composition

- **Snippets** replace slots: `{#snippet header()}…{/snippet}` passed as a prop, rendered
  with `{@render header()}`.
- Default content is the `children` snippet: `let { children }: { children?: Snippet } =
  $props()` → `{@render children?.()}`.

## Review checklist

- [ ] `$props()` with an interface, not `export let`
- [ ] two-way props use `$bindable()`
- [ ] events are callback props, not `createEventDispatcher`
- [ ] `onclick` attribute, not `on:click` directive
- [ ] snippets (`{@render}`) instead of `<slot>`; props not mutated in place

## Red Flags

- `export let` mixed with `$props()` in the same component
- `createEventDispatcher` for child→parent communication
- `<slot>` / named slots instead of snippets
- `on:click` directives in a Svelte 5 component
- a child assigning to a prop instead of local state
