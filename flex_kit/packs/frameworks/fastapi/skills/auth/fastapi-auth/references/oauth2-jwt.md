# OAuth2 password flow + JWT bearer

The standard user-facing scheme: the client posts username+password to `/token`, gets a
signed JWT, and sends it as `Authorization: Bearer <token>` on every request.

Deps: `pip install pyjwt "pwdlib[argon2]"`.

## Hashing + token helpers

```python
from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash

SECRET_KEY = settings.jwt_signing_key      # openssl rand -hex 32; load from config, never inline
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()

def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)

def get_password_hash(plain: str) -> str:        # call at signup; store the result only
    return password_hash.hash(plain)

def create_access_token(data: dict, expires: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expires
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

## The /token endpoint

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()

def authenticate_user(username: str, password: str) -> User | None:
    user = users.get(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

@app.post("/token")
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        {"sub": user.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=token, token_type="bearer")
```

## The validating dependency

```python
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate the token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])   # checks signature + exp
        username = payload.get("sub")
        if username is None:
            raise unauthorized
    except InvalidTokenError:
        raise unauthorized
    user = users.get(username)
    if user is None:
        raise unauthorized
    return user
```

Notes:
- `jwt.decode` verifies the signature and `exp` - a tampered or expired token raises -> 401.
- Store only `user.hashed_password` (from `get_password_hash` at signup), never plaintext.
- To gate per route, declare scopes on the bearer + use `SecurityScopes` - see
  `keys-basic-scopes.md`.
