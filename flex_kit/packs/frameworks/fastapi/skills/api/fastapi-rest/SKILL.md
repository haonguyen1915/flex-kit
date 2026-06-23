---
name: fastapi-rest
description: Building a RESTful API with FastAPI - APIRouter layout, path operations with response_model and status_code, separate Pydantic request/response models, Depends for shared logic, HTTPException for errors, query/path validation, and pagination. Use when designing FastAPI endpoints, structuring an app, or reviewing route code. Not for authentication (see fastapi-auth) or app-wide layering (see python-architecture).
---

# FastAPI REST

FastAPI maps HTTP to typed Python: declare the data as Pydantic models and the framework
validates, serializes, and documents it. Design endpoints around **resources + correct
status codes**, and push everything reusable into dependencies.

## App + router layout

Split routes into `APIRouter`s by resource; the app just includes them. Keep route
functions thin - parse, call a service, return (the service layer is `python-architecture`).

```python
# routers/items.py
from fastapi import APIRouter, status

router = APIRouter(prefix="/items", tags=["items"])

@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(payload: ItemCreate) -> ItemOut:
    return service.create(payload)

# main.py
app = FastAPI()
app.include_router(router)
```

## Separate request vs response models

Never reuse one model for input and output. A request model has only client-settable
fields; a response model (`response_model=`) controls what leaks out (no hashes, internal
flags). FastAPI validates the body against the request model and filters the return value
through the response model.

```python
class ItemCreate(BaseModel):          # what the client may send
    name: str
    price: float = Field(gt=0)

class ItemOut(BaseModel):             # what the API returns
    id: int
    name: str
    price: float
```

## Status codes + errors

- Return the right code: `201` create, `200` read/update, `204` delete (no body),
  `422` is automatic on validation failure.
- Raise `HTTPException(status_code=404, detail=...)` for expected failures - don't return
  an error dict with a `200`. Map domain errors to codes at the route boundary.

```python
@router.get("/{item_id}", response_model=ItemOut)
async def read_item(item_id: int) -> ItemOut:
    item = service.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="item not found")
    return item
```

## Dependencies

`Depends` injects shared logic (db session, the current user, pagination) - declared once,
reused, and testable via `app.dependency_overrides`. Use `yield` for setup/teardown.

```python
def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("")
async def list_items(db: Annotated[Session, Depends(get_db)], page: PageParams = Depends()):
    return service.list(db, page.limit, page.offset)
```

## Validation & pagination

Constrain inputs with `Field`/`Query` (`gt`, `le`, `max_length`, `Literal[...]`) so bad
data is rejected with `422` before your code runs. Make pagination a reusable model:

```python
class PageParams(BaseModel):
    limit: int = Field(50, gt=0, le=100)
    offset: int = Field(0, ge=0)
```

## Review checklist

- [ ] routes split into `APIRouter`s by resource; route functions are thin
- [ ] distinct request vs response models; `response_model` set on each route
- [ ] correct status codes (`201`/`204`/…); errors via `HTTPException`, not `200`+error body
- [ ] shared logic (db, user, paging) injected with `Depends`, not duplicated
- [ ] inputs constrained with `Field`/`Query`; pagination bounded
- [ ] `async def` only where the body actually awaits I/O

## Red Flags

- one Pydantic model used for both input and output (leaks internal fields)
- returning `{"error": ...}` with a `200` instead of raising `HTTPException`
- business logic inside the route function instead of a called service
- a route doing blocking I/O in `async def` (blocks the event loop - see python-concurrency)
- unvalidated `limit`/`offset` (unbounded query) or untyped path params
