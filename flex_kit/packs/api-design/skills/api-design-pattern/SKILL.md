---
name: api-design-pattern
description: REST API design conventions that apply regardless of language or framework - resource naming, HTTP methods, status codes, RFC 7807 errors, pagination, versioning, async tasks, caching, and security. Use when designing new endpoints or reviewing an API contract.
---

# API Design Pattern

Contract-design conventions for REST APIs. These are language- and
framework-agnostic: the same rules hold whether the implementation is Rust,
Python, Node, or anything else. Framework idioms (routing, serialization,
middleware) belong in a `backend-<lang>` skill, not here.

Design the contract before implementing - once published, an endpoint becomes
someone else's dependency. Design for the consumer first, the maintainer second.

## Resource naming

Resources are nouns; the HTTP method is the verb. Never put the action in the path.

```
GET    /users          POST   /users          DELETE /users/{id}     # correct
GET    /getUsers       POST   /createUser      POST   /deleteUser     # wrong
```

Archetypes:

| Archetype | Meaning | Naming | Example |
|---|---|---|---|
| Document | a single entity | singular id segment | `/users/{id}` |
| Collection | server-managed list | plural | `/users` |
| Store | client-managed list | plural | `/users/{id}/playlists` |
| Sub-resource | nested under a parent | plural | `/users/{id}/orders` |

URI rules: plural nouns, lowercase, hyphens (not underscores), no trailing slash,
no file extension, hierarchy via `/`. Express filtered/sorted/paged views with
query params - never a new path:

```
GET /devices?region=usa&brand=xyz&sort=-created_at&page=2&size=20
```

## HTTP methods

| Method | Use | Safe | Idempotent | Cacheable |
|---|---|---|---|---|
| GET | read | yes | yes | yes |
| POST | create / non-idempotent action | no | no | no |
| PUT | full replace | no | yes | no |
| PATCH | partial update | no | no | no |
| DELETE | remove | no | yes | no |

CRUD maps to `GET/POST /users`, `GET/PUT/PATCH/DELETE /users/{id}`. Non-CRUD
actions become a sub-resource (`POST /orders/{id}/cancellation`) over RPC verbs.

## Status codes

- **2xx** - `200` ok, `201` created (+ `Location`), `202` accepted (async),
  `204` no content (DELETE).
- **4xx** - `400` malformed, `401` unauthenticated, `403` unauthorized,
  `404` not found, `405` method not allowed, `409` conflict, `422` semantic
  validation, `429` rate-limited.
- **5xx** - `500` server error (never leak internals), `502`/`503`/`504` gateway
  / unavailable / timeout.

Never return `200` for everything.

## Error format (RFC 7807)

One shape for every error - `application/problem+json`:

```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "The 'email' field must be a valid email address.",
  "instance": "/users/12345",
  "errors": [{ "field": "email", "message": "Must be a valid email address" }]
}
```

Stable `type`/`title` (machine + human); `detail` for the specific case; optional
field-level `errors`.

## Pagination

Cursor pagination for large or changing sets; offset only for small, stable sets.
Always return metadata, consistently across endpoints:

```json
{ "data": [...], "pagination": { "page": 2, "size": 20, "total": 150, "totalPages": 8 } }
```

`?page=2&size=20` or `?cursor=abc123&size=20`.

## Versioning

Pick one and apply everywhere - URI path `/v1/...` (recommended), header
`X-API-Version: 1`, or content negotiation. Additive changes do not bump; breaking
changes (removed field, changed type, stricter validation) do. On deprecation,
publish a timeline and a `Sunset` header.

## Long-running tasks (async)

Operations longer than a few seconds must not block the connection:

1. `POST /reports` -> `202 Accepted` + `Location: /tasks/{id}` + `{ "status": "pending" }`.
2. Poll `GET /tasks/{id}` -> `{ "status": "in_progress", "percentage": 45 }`; use a
   `Retry-After` header to pace polling.
3. On completion -> `{ "status": "completed", "result": {...} }`.
4. `DELETE /tasks/{id}` cancels. Consider webhooks or SSE to avoid polling.

The task runs independently of the client connection.

## Caching

`Cache-Control: max-age=...` for time-based; `ETag` + `If-None-Match` and
`Last-Modified` + `If-Modified-Since` for validation; return `304 Not Modified`
when unchanged.

## Security

HTTPS only; authenticate (OAuth2 / JWT / API key); authorize per endpoint
(RBAC); validate and sanitize all input at the boundary; rate-limit per
client/key; set security headers (`X-Content-Type-Options`, CORS).

## Response shape

Collections stay minimal (id + key fields + pagination); a single resource
includes full detail (timestamps, nested config). Add HATEOAS `links` only when
discoverability is a real requirement.

## Review checklist

- [ ] Resource names are plural nouns, lowercase-hyphenated, no verbs.
- [ ] Correct method (idempotency right for PUT/DELETE) and accurate status code.
- [ ] Errors use the single RFC 7807 shape.
- [ ] Collections paginate with consistent metadata.
- [ ] Versioning is explicit; breaking vs additive change handled correctly.
- [ ] Long operations use `202` + status resource, not a blocked call.
- [ ] Auth, authorization, input validation, and rate limits are in place.
