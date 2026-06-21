---
name: frontend-performance
description: Keep the UI fast - minimize render work, memoize deliberately, virtualize large lists, lazy-load and split bundles, and avoid layout thrash. Use when a view is janky or slow, or when reviewing a change that touches rendering, lists, or bundle size.
---

# Frontend Performance

Most UI slowness is wasted work: re-rendering what didn't change, mounting thousands of rows
at once, or shipping a megabyte of JS to show a button. Measure first - then cut the work,
don't guess.

## Render less

- Don't create functions / objects inside hot render paths or loops where they make children
  re-render; hoist stable references.
- Memoize a derived value or a child **only when it is measurably expensive** - memoization
  has its own cost; blanket-memoizing everything slows things down and adds noise.
- Compute a derived value once (a derived / computed), not re-derived in the template on
  every render.

## Big lists & DOM

- **Virtualize** long lists (render only the visible rows) instead of mounting thousands of
  nodes; use the framework's virtual list, don't hand-roll scroll math.
- Key list items by a stable id, not the index - index keys break reconciliation on reorder.
- Batch DOM reads and writes; reading layout (`offsetHeight`) right after a write forces a
  synchronous reflow (layout thrash). Cache repeated DOM queries.

## Load less

- Code-split by route / feature and lazy-load below-the-fold or rarely-used chunks; don't
  ship the admin panel to every visitor.
- Defer expensive work until it is needed (compute when a modal opens, not on mount).
- Watch bundle size: a heavy dependency for one small feature is a cut candidate.

## Effects & async

- Read reactive inputs synchronously; subscriptions / timers / observers get a cleanup so
  they don't leak or stack up.
- Debounce or throttle high-frequency handlers (scroll, resize, search input).

## Review checklist

- [ ] no new functions / objects in a hot render path causing child re-renders
- [ ] memoization applied only where measurably expensive, not blanket
- [ ] long lists are virtualized; list keys are stable ids, not indexes
- [ ] no layout thrash (read-after-write); repeated DOM queries cached
- [ ] code-split + lazy-load for routes / heavy or rare features
- [ ] effects clean up; high-frequency handlers debounced / throttled

## Red Flags

- a list of thousands of rows rendered without virtualization
- list items keyed by index
- memoizing everything "to be safe" (cost without benefit)
- a heavy library imported for one trivial use
- a scroll / resize handler with no throttle; an effect with no cleanup
- reading `offsetHeight` / `getBoundingClientRect` immediately after a style write
