---
name: frontend-styling
description: Style UI maintainably - design tokens over magic values, a theme covering light and dark, composition over high-specificity overrides, responsive by default. Use when adding styles, defining a theme or tokens, or reviewing CSS for hardcoded values or specificity wars. Not for component structure (see frontend-component-design).
---

# Frontend Styling

Style sprawls when every component invents its own colors, spacings, and breakpoints. The
fix is a small set of **tokens** everything references, so a change happens in one place and
the UI stays consistent.

## Tokens, not magic values

- Reference design tokens (CSS variables / theme values) for color, spacing, radius, and
  typography - not hardcoded hex, px, or one-off values scattered across components.
- A new token is defined once in the theme; components consume it. Avoid arbitrary values
  (`color: #3b82f6`, `margin: 13px`) inline.

## Theming

- A token has a value per theme - define it for **both light and dark** (and any other
  theme) so nothing breaks when the theme flips.
- Derive variants (hover, disabled, muted) from the base token with opacity / shade, not a
  new hardcoded color.

## Composition over override

- Compose from utility classes / base styles; reach for high-specificity selectors and
  `!important` last - they start specificity wars.
- Keep a component's styles scoped to it; avoid global selectors that style other components
  by accident.

## Responsive & layout

- Design responsive by default - use fluid layout (flex / grid, relative units) over fixed
  pixel widths; test the breakpoints the project defines.
- Don't hardcode a breakpoint per component; use the shared scale.

## Review checklist

- [ ] color / spacing / radius / type come from tokens, not hardcoded values
- [ ] new tokens defined once; no arbitrary inline values
- [ ] every token / variant covers light AND dark (and other themes)
- [ ] variants derive from base tokens (opacity / shade), not new hex
- [ ] composition over `!important` / specificity hacks; styles scoped, not leaking
- [ ] responsive via the shared scale, not per-component hardcoded breakpoints

## Red Flags

- hardcoded hex / px where a token exists
- a color defined for light mode with no dark-mode counterpart
- `!important` or deeply nested selectors to win a specificity fight
- a global selector that styles components it doesn't own
- fixed pixel widths that break on small screens
