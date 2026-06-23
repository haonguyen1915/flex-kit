# A worked layered app

A minimal order service showing the four layers, a port, and one composition root.
Every arrow points inward; only `bootstrap` knows concrete types.

```
src/shop/
├─ domain/order.py
├─ service/ports.py
├─ service/place_order.py
├─ adapters/sql_repo.py
└─ entrypoints/bootstrap.py   +  web.py / cli.py
```

## domain - pure, imports nothing outward

```python
# domain/order.py
from dataclasses import dataclass

@dataclass
class Order:
    ref: str
    qty: int

    def can_fulfill(self, available: int) -> bool:
        return self.qty <= available
```

## service - use-cases + the ports they own

```python
# service/ports.py
from typing import Protocol
from shop.domain.order import Order

class OrderRepo(Protocol):
    def get(self, ref: str) -> Order | None: ...
    def add(self, order: Order) -> None: ...

class Notifier(Protocol):
    def order_placed(self, ref: str) -> None: ...
```

```python
# service/place_order.py
from shop.domain.order import Order
from shop.service.ports import OrderRepo, Notifier

class DuplicateOrder(Exception): ...

def place_order(ref: str, qty: int, repo: OrderRepo, notify: Notifier) -> Order:
    if repo.get(ref) is not None:
        raise DuplicateOrder(ref)
    order = Order(ref=ref, qty=qty)
    repo.add(order)
    notify.order_placed(ref)
    return order
```

The service depends only on `domain` + the `Protocol` ports - never on sql or http.

## adapters - concrete I/O that *satisfies* the port

```python
# adapters/sql_repo.py   (structurally an OrderRepo - no import of the port needed)
from shop.domain.order import Order

class SqlOrderRepo:
    def __init__(self, session):
        self._session = session

    def get(self, ref: str) -> Order | None:
        row = self._session.get(...)
        return Order(row.ref, row.qty) if row else None

    def add(self, order: Order) -> None:
        self._session.add(...)
```

## composition root - the only place concretes are constructed

```python
# entrypoints/bootstrap.py
from dataclasses import dataclass
from shop.adapters.sql_repo import SqlOrderRepo
from shop.adapters.email import EmailNotifier
from shop.service.ports import OrderRepo, Notifier

@dataclass
class App:
    repo: OrderRepo
    notify: Notifier

def bootstrap(repo: OrderRepo | None = None, notify: Notifier | None = None) -> App:
    return App(
        repo=repo or SqlOrderRepo(make_session()),
        notify=notify or EmailNotifier(),
    )
```

```python
# entrypoints/web.py - thin: parse, call the service, format
from fastapi import FastAPI
from shop.service.place_order import place_order
from shop.entrypoints.bootstrap import bootstrap

app_deps = bootstrap()
api = FastAPI()

@api.post("/orders")
def create(ref: str, qty: int):
    order = place_order(ref, qty, app_deps.repo, app_deps.notify)
    return {"ref": order.ref}
```

## why this tests cleanly

The same `place_order` runs in every test tier - only the injected dependency changes:

```python
class FakeRepo:                       # satisfies OrderRepo structurally
    def __init__(self): self._d = {}
    def get(self, ref): return self._d.get(ref)
    def add(self, o): self._d[o.ref] = o

def test_place_order_notifies():
    notes = []
    class FakeNotifier:
        def order_placed(self, ref): notes.append(ref)
    place_order("o1", 5, FakeRepo(), FakeNotifier())
    assert notes == ["o1"]
```

No database, no mocking framework - the seam is a plain argument. That testability is
the payoff of pointing dependencies inward.
