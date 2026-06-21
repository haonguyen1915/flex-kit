---
name: frontend-component-design
description: Design UI components that compose, framework-agnostic - prop contracts, single responsibility, controlled vs uncontrolled, container/presentational split, reuse over reinvention. Use when shaping or reviewing a component's responsibilities, props, or boundaries. For a framework's component API (Svelte $props, React props), use the framework pack.
---

# Frontend Component Design

A component is a unit of UI with a contract (its props) and a responsibility. The failure
mode is the god component - one that fetches, transforms, renders, and manages five concerns
at once, impossible to reuse or test. Keep each component about one thing.

## One responsibility

- A component renders one thing or coordinates a few children - not data fetching + business
  logic + layout + state all at once. Split it when it grows past one reason to change.
- **Presentational vs container** - separate components that *look* (pure, props-in,
  events-out) from those that *wire* (fetch, hold state, pass down). Presentational
  components are reusable and trivially testable.

## Prop contracts

- Props are the public API - keep them minimal, named for intent, typed. Avoid boolean soup
  (`isOpen, isLoading, isDisabled, isPrimary`); a `variant` / `status` enum reads better.
- Pass data down, events up. A child reports via callback props (`onSelect`); it doesn't
  reach up or mutate a parent's state.
- Prefer composition (children / slots) over a dozen configuration props - let callers pass
  the content rather than toggling every variation through flags.

## Controlled vs uncontrolled

- **Controlled** - the parent owns the value; the child renders it and reports changes. Use
  when the value must sync with other state.
- **Uncontrolled** - the component owns its internal state. Use for self-contained widgets;
  don't lift state higher than it needs to go.
- Pick one per prop; a value that is sometimes controlled, sometimes not is a bug source.

## Reuse over reinvention

- Check the existing component library before building a button / modal / dropdown again -
  reinventing one diverges behavior and accessibility.
- Extract a shared component only when the same shape appears 3+ times (rule of three);
  premature shared components calcify the wrong abstraction.

## Review checklist

- [ ] one responsibility; not fetching + logic + layout + state in one component
- [ ] props are minimal, intent-named, typed; no boolean soup where an enum fits
- [ ] data flows down, events flow up via callback props
- [ ] controlled / uncontrolled is consistent per prop
- [ ] an existing component is reused instead of reinvented
- [ ] composition (slots / children) preferred over many config flags

## Red Flags

- a component that fetches data, holds business logic, and renders layout at once
- 8+ boolean props toggling appearance
- a child mutating a parent's state or reaching into a global
- a re-implemented modal / dropdown / tooltip the library already provides
- state lifted to the top of the tree that only one leaf uses
