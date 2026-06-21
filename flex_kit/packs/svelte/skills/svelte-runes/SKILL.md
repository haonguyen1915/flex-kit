---
name: svelte-runes
description: Svelte 5 runes - $state for reactive data, $derived for computed (not $effect), $effect for side effects with cleanup, $state.raw for large data. Use when the user writes or reviews Svelte 5 reactivity, or migrates $: reactive statements. Not for component props/snippets (see svelte-components) or naming (see svelte-naming).
---

# Svelte 5 Runes

Runes make reactivity explicit. The cardinal rule: **derive computed values, don't compute
them in an effect** - effects are for side effects only.

## $state and $derived

- `let count = $state(0)` - reactive value. `const doubled = $derived(count * 2)` -
  recomputes when its dependencies change.
- **Never** assign a computed value inside `$effect`; use `$derived`. Effect-as-derived loses
  optimization and risks infinite loops.
- `$state.raw(largeData)` for big, read-mostly structures - skips deep proxying overhead.

## $effect

- `$effect(() => { … })` for genuine side effects (logging, subscriptions, DOM, fetch) after
  render. Dependencies are tracked automatically when read synchronously.
- Return a cleanup function for anything you allocate - timers, listeners, subscriptions -
  or it leaks and stacks across re-runs.
- Don't create circular effects (A writes state B reads and writes back).

## Migrating

- Replace `$:` reactive statements - computed → `$derived`, side effect → `$effect`.
- Read reactive inputs synchronously inside the effect; capturing them in `setTimeout` /
  `then` reads stale values.

## Review checklist

- [ ] computed values use `$derived`, never `$effect`
- [ ] `$effect` only for side effects, with a cleanup return where it allocates
- [ ] `$state.raw` for large read-mostly data
- [ ] no `$:` (Svelte 4) left after migration
- [ ] reactive inputs read synchronously, not inside a deferred callback

## Red Flags

- `$effect(() => { total = a + b })` instead of `$derived(a + b)`
- a subscription / timer in `$effect` with no cleanup return
- a circular effect causing an infinite update loop
- `$:` reactive statements in a Svelte 5 component
- reading `$state` inside `setTimeout` / `Promise.then` and getting stale values
