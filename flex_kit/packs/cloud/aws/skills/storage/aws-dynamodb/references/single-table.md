# Single-table design - a worked example

One table serving several access patterns by overloading the partition/sort keys. Use this
shape only when you genuinely need to co-fetch related entities in one query.

## Access patterns (decide these first)

1. Get a user by id
2. List a user's orders, newest first
3. Get one order by id
4. List orders by status (admin) -> needs a GSI

## Key design

One table `app` with generic keys `PK` / `SK`, plus `GSI1` (`GSI1PK` / `GSI1SK`).

| Entity | PK | SK | GSI1PK | GSI1SK |
|---|---|---|---|---|
| User  | `USER#u123` | `PROFILE` | - | - |
| Order | `USER#u123` | `ORDER#2024-06-01#o456` | `STATUS#shipped` | `2024-06-01` |

- Pattern 1: `GetItem(PK=USER#u123, SK=PROFILE)`.
- Pattern 2: `Query(PK=USER#u123, SK begins_with "ORDER#")`, `ScanIndexForward=false` for newest first.
- Pattern 3: the order id is in the SK; `GetItem` by the known PK/SK.
- Pattern 4: `Query` GSI1 with `GSI1PK=STATUS#shipped`.

## Why it works

A user and all their orders share `PK=USER#u123`, so pattern 2 reads them in **one** `Query`.
The SK prefix (`ORDER#<date>#<id>`) sorts orders by date for free. The GSI re-keys the same
items by status for the admin view - no second table, no join in app code.

## The cost

Every access pattern has to be designed up front: a new query usually needs a new GSI or a key
change + backfill. That rigidity is the price of single-table's single-digit-millisecond reads.
Reach for it when co-fetch + scale demand it; otherwise a table per aggregate is clearer and
evolves more freely.
