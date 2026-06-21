---
name: typescript-naming
description: TypeScript naming conventions - casing per kind, boolean predicates, no type-noise suffixes, no Async suffix, file naming by role. Use when the user names or reviews TS/JS identifiers, types, files, or event handlers, or when a name is vague or Hungarian. Not for non-TS code or type design (see typescript-types).
---

# TypeScript Naming

The type system already states the shape - spend names on intent, not on encoding the type.

## Casing

- `camelCase` - variables, functions, methods.
- `PascalCase` - types, interfaces, classes, components.
- `SCREAMING_SNAKE_CASE` - true constants; a mutable config object stays `camelCase`.

## Conventions

- Booleans are predicates: `isLoading`, `hasErrors`, `canSubmit`; avoid negatives and double
  negatives (`isReady`, not `!isNotReady`).
- No type-noise suffixes: `User`, not `UserType` / `UserInterface` / `UserData`; no `I` prefix.
- No `Async` suffix - `Promise<T>` already encodes it (`getUser`, not `getUserAsync`).
- Units on numerics: `delayMs`, not `delay: number`.

## Handlers & files

- Event props `on{Event}` (`onClick`, `onSelect`); internal functions `handle{Event}`
  (`handleClick`). Pick one per layer, don't mix.
- Files by role: components `PascalCase.tsx`/`.svelte`; modules/utils `kebab-case.ts`;
  services `kebab-case.service.ts`.

## Review checklist

- [ ] casing matches the kind (camel / Pascal / SCREAMING)
- [ ] booleans are positive predicates; no double negatives
- [ ] no type-noise suffix (`Type`/`Interface`/`Data`) or `I` prefix
- [ ] no `Async` suffix; numerics carry units
- [ ] `on*` for props vs `handle*` for internal, consistently

## Red Flags

- Hungarian encoding (`strName`, `arrUsers`, `bIsReady`)
- `IUser` / `UserInterface` / `UserType`
- a generic role noun alone (`Manager`, `Handler`, `Processor`)
- `getUserAsync` when it returns a `Promise`
- mixed `on*` and `handle*` for the same layer
