---
name: typescript-types
description: TypeScript type design - unknown over any, discriminated unions, narrowing, satisfies, generics with bounds, readonly, and branded ids. Use when the user designs or reviews TS types, interfaces, generics, or fights any/casts. Not for naming (see typescript-naming) or runtime idioms (see typescript-idioms).
---

# TypeScript Types

Types are a proof, not decoration. Make illegal states unrepresentable and let the compiler
catch what tests would miss.

## Avoid `any`; prefer `unknown`

- `any` disables checking; `unknown` forces a narrow before use. Type third-party gaps with
  a guard, or `@ts-expect-error` + a one-line reason - not a blanket `any`.

## Model with unions

- **Discriminated unions** over loose objects with optional fields: `{ kind: 'ok'; value }
  | { kind: 'err'; error }`. The discriminant drives exhaustive narrowing.
- `as const` to keep literals from widening; `satisfies T` to check a value matches a shape
  *without* erasing its precise inferred type.

## Tighten the surface

- Generics carry bounds (`<T extends Id>`), not bare `<T>` everywhere - bounds catch misuse early.
- Default to `readonly` props/arrays; opt into mutability explicitly.
- **Branded ids** to stop mixing keys: `type UserId = string & { readonly __brand: 'UserId' }`.

## Review checklist

- [ ] no `any` where `unknown` + a guard would work
- [ ] variant data modeled as a discriminated union, narrowed exhaustively
- [ ] `as const` / `satisfies` used instead of casts to fix inference
- [ ] generics constrained with `extends`, not bare
- [ ] `readonly` by default; distinct id types are branded

## Red Flags

- `value as User` to silence the compiler instead of a type guard
- `Record<string, any>` for an API response
- a bare `<T>` generic on every function, no constraints
- two different ids both typed as plain `string`
- `Partial<T>` where a precise union of the valid shapes is clearer
