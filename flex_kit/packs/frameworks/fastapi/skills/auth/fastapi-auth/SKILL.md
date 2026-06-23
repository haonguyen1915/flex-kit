---
name: fastapi-auth
description: Authentication in FastAPI - choosing and implementing OAuth2 password flow with JWT bearer tokens, API keys, HTTP Basic, and scope-based access (RBAC), plus the shared rules (401 vs 403, WWW-Authenticate, hash-not-plaintext, constant-time compare, expiring tokens). Use when adding auth to FastAPI routes, picking an auth scheme, or reviewing FastAPI security code. Not for general REST shape (see fastapi-rest).
---

# FastAPI Auth

Authentication in FastAPI is a **dependency**: a security scheme pulls a token/key off the
request, a function validates it and returns the user, and routes depend on that function.
Pick the scheme by the caller; obey the cross-cutting rules below whichever you pick.

## Choose the scheme

| Caller | Scheme | Extractor |
|---|---|---|
| End users / SPA / mobile | **OAuth2 password + JWT bearer** | `OAuth2PasswordBearer` |
| Service-to-service / internal | **API key** | `APIKeyHeader` / `APIKeyQuery` |
| Tooling / simple internal | **HTTP Basic** | `HTTPBasic` |
| Per-route permissions | **OAuth2 scopes (RBAC)** | `SecurityScopes` + `Security(...)` |

Default to OAuth2 + JWT for user-facing APIs. Full code per scheme in `references/`.

## The dependency shape (every scheme shares it)

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    user = decode_and_load(token)        # validate; raise 401 if bad
    return user

@router.get("/me")
async def me(user: Annotated[User, Depends(get_current_user)]) -> UserOut:
    return user
```

Protect a whole router with `dependencies=[Depends(get_current_user)]`; take the user as a
parameter on a route only when you need its value.

## Cross-cutting rules (all schemes)

- **Never store a plaintext password.** Hash with a modern KDF (`pwdlib` -> argon2/bcrypt),
  store only the hash, verify on login.
- **401 vs 403.** `401 Unauthorized` = missing/invalid identity (send a `WWW-Authenticate`
  header); `403 Forbidden` = valid identity but not allowed (wrong scope/role). Don't mix them.
- **Constant-time compare.** Check API keys / basic passwords with `compare_digest`, never
  `==` - `==` leaks length and content through response timing.
- **Expiring tokens.** Give JWTs a near-future `exp`; verify signature **and** `exp` on every
  request; use refresh tokens for longevity.
- **The signing key (`SECRET_KEY`) and API keys load from config/environment**, never literals
  in source; keep them out of the repo and logs, and rotate on leak.
- **Authn once, authz per route.** Authenticate with `get_current_user`; gate permissions
  per route with scopes (`Security(get_current_user, scopes=[...])`).

## Review checklist

- [ ] auth is a `Depends`/`Security` dependency; routes never parse tokens inline
- [ ] passwords hashed with a real KDF; plaintext never stored or logged
- [ ] `401` (+ `WWW-Authenticate`) for bad identity, `403` for insufficient scope
- [ ] key/password checks use `compare_digest`, not `==`
- [ ] JWTs are signed, expiring, and verified (signature + `exp`) each request
- [ ] signing key + API keys come from config, not literals in source
- [ ] per-route permission enforced via `SecurityScopes` / `Security`

## Red Flags

- a signing key or API key hard-coded as a literal in source
- a plaintext password stored, compared, or written to a log
- `==` used to check an API key or password (timing leak - use `compare_digest`)
- a JWT with no `exp`, or one whose signature/expiry is never verified
- `403` returned for "not logged in", or `401` for "logged in but not permitted"
- token parsing copy-pasted into each route instead of one shared dependency
