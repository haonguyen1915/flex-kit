---
name: frontend-accessibility
description: Build interfaces usable by everyone - semantic HTML first, ARIA only when needed, full keyboard operation, managed focus, sufficient contrast. Use when adding interactive UI, custom widgets, modals, or reviewing a change for accessibility. Not for visual styling (see frontend-styling).
---

# Frontend Accessibility

Accessibility is mostly free if you start from semantic HTML - and lost the moment you build
interactive widgets out of `<div>`s. The goal: every action works by keyboard, every control
announces what it is, and nothing relies on sight or a mouse alone.

## Semantic HTML first

- Use the real element: `<button>`, `<a>`, `<label>`, `<nav>`, `<input>`. They bring focus,
  keyboard, and roles for free. A clickable `<div>` brings none.
- ARIA is a patch for when no native element fits - prefer the native element; **no ARIA is
  better than wrong ARIA**.
- Associate labels with controls (`<label for>`); every input, button, and image has an
  accessible name (text, `aria-label`, or `alt`).

## Keyboard

- Every interaction works without a mouse: Tab to reach, Enter / Space to activate, Escape to
  dismiss, arrows to move within a composite (menu, tabs, listbox).
- Focus order follows reading order; no keyboard trap (you can always Tab out).
- A visible focus indicator on every focusable element - don't remove the outline without
  replacing it.

## Custom widgets

- A custom control needs the right `role`, its state (`aria-expanded`, `aria-selected`,
  `aria-checked`), and the keyboard behavior its native equivalent would have.
- Manage focus on transitions: a modal traps focus and returns it to the trigger on close; a
  dropdown returns focus to its button.

## Perception

- Don't convey meaning by color alone - pair it with text or an icon (an error is red *and*
  says "error").
- Meet contrast minimums (4.5:1 for body text); check hover / focus / active states too.
- Provide text alternatives for non-text content; mark decorative images `alt=""`.

## Review checklist

- [ ] native semantic elements used; ARIA only where no native element fits
- [ ] every control has an accessible name
- [ ] full keyboard operation: reach, activate, dismiss, navigate; no trap
- [ ] visible focus indicator; focus managed on modal / dropdown open and close
- [ ] custom widgets expose role + state + native-equivalent keyboard behavior
- [ ] meaning never by color alone; contrast >= 4.5:1 including interactive states

## Red Flags

- a clickable `<div>` / `<span>` with an onClick and no role or keyboard handler
- `outline: none` with no replacement focus style
- a modal that doesn't trap focus or return it on close
- an icon-only button with no accessible name
- error / status shown by color with no text or icon
