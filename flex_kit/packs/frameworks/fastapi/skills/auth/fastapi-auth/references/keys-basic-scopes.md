# API key, HTTP Basic, and scopes (RBAC)

Three more schemes - for non-user callers and per-route permissions. All are FastAPI
dependencies, same shape as OAuth2.

## API key (service-to-service)

```python
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
import secrets

api_key_scheme = APIKeyHeader(name="X-API-Key")

async def require_api_key(key: Annotated[str, Depends(api_key_scheme)]) -> str:
    if not secrets.compare_digest(key, settings.api_key):     # constant-time
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid API key")
    return key

@router.get("/internal", dependencies=[Depends(require_api_key)])
async def internal(): ...
```

`APIKeyQuery` reads the key from a query param instead - prefer the header; query strings
land in access logs and browser history.

## HTTP Basic (simple internal / tooling)

```python
import secrets
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

basic = HTTPBasic()

def require_basic(credentials: Annotated[HTTPBasicCredentials, Depends(basic)]) -> str:
    ok_user = secrets.compare_digest(credentials.username, settings.basic_user)
    ok_pass = secrets.compare_digest(credentials.password, settings.basic_pass)
    if not (ok_user and ok_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
```

`compare_digest` (not `==`) keeps the check constant-time, so timing can't reveal the value.

## OAuth2 scopes (RBAC)

Build on the JWT scheme: declare scopes on the bearer, embed the granted scopes in the
token, and require specific ones per route. Insufficient scope is `403`, not `401`.

```python
from typing import Annotated
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"items:read": "Read items", "items:write": "Create/modify items"},
)

async def get_current_user(
    scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    auth = f'Bearer scope="{scopes.scope_str}"' if scopes.scopes else "Bearer"
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_scopes = payload.get("scopes", [])
        user = users.get(payload.get("sub"))
        if user is None:
            raise InvalidTokenError
    except InvalidTokenError:
        raise HTTPException(401, "Could not validate the token",
                            headers={"WWW-Authenticate": auth})
    for scope in scopes.scopes:                      # 403: authenticated but missing a scope
        if scope not in token_scopes:
            raise HTTPException(status_code=403, detail="Not enough permissions",
                                headers={"WWW-Authenticate": auth})
    return user

@router.post("/items")
async def create(
    user: Annotated[User, Security(get_current_user, scopes=["items:write"])],
): ...
```

`Security(..., scopes=[...])` on each route declares what it needs; `get_current_user`
enforces it. Grant the token's scopes at login from the user's role.
