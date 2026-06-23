---
name: aws-dynamodb
description: Modeling and querying AWS DynamoDB - design from access patterns, partition/sort key choice, single-table vs multi-table, GSIs for alternate lookups, query (never scan), on-demand vs provisioned capacity, and idempotent conditional writes. Use when designing a DynamoDB table, choosing keys/indexes, or fixing slow scans/hot partitions. Not for relational schema design (see the database- pack) or S3 object storage (see aws-s3).
---

# AWS DynamoDB

DynamoDB is fast and scales only if you **design from access patterns, not entities**. You
can't add an arbitrary query later for free - the keys you pick decide what's cheap. List the
queries first, then model keys to serve them.

## Keys

- **Partition key (PK)** decides which partition an item lives on - pick something
  high-cardinality and evenly accessed (a user id, a tenant id) so load spreads. A low-variety
  PK (a status, a boolean) creates a **hot partition** and throttles.
- **Sort key (SK)** orders items within a partition and enables range queries (`begins_with`,
  `between`, `>`). PK + SK = a **composite key** - together they're the item's identity.
- Encode hierarchy in the SK (`ORDER#2024#INVOICE#42`) to query a prefix in one call.

## Query, never scan

- **`Query`** targets one partition key value (+ optional SK condition) - fast, charged by the
  item size read. Design keys so every request-path read is a `Query` or `GetItem`.
- **`Scan`** reads the whole table then filters - O(table). Only for admin/export jobs, never a
  request path.
- A **`FilterExpression`** runs *after* the read and **doesn't save capacity** - it just hides
  rows you already paid to read. Narrow with keys, not a filter.

## Indexes for more access patterns

- A **GSI** is a second (PK, SK) over the same data for a different lookup (e.g. by email when
  the table is keyed by id). GSIs are **eventually consistent** and cost extra storage/writes -
  add one per real query, projecting only needed attributes.
- An **LSI** shares the table's PK with an alternate SK (strongly consistent), set at table
  creation only.

## Single-table vs multi-table

- **Single-table design** packs many entity types into one table (overloaded PK/SK + a `type`
  attribute) to fetch related items in one `Query`. Powerful but harder - justify it by a real
  need to co-fetch.
- Otherwise default to **a table per aggregate**; clarity first. A worked single-table model:
  [references/single-table.md](references/single-table.md).

## Capacity & idempotent writes

- **On-demand** capacity for spiky/unknown load (pay per request); **provisioned** (+ auto
  scaling) for steady, predictable, cost-sensitive load.
- Make writes idempotent with a **condition expression**: `PutItem` with
  `attribute_not_exists(PK)` creates once; `UpdateItem` with a version check is a safe
  read-modify-write - so a retried Lambda doesn't double-apply (see aws-lambda).

## Review checklist

- [ ] access patterns listed first; keys designed to serve them
- [ ] partition key is high-cardinality and evenly accessed (no hot partition)
- [ ] every request-path read is a `Query` / `GetItem`, never a `Scan`
- [ ] `FilterExpression` not used to stand in for a missing key / index
- [ ] each alternate lookup has a GSI (eventually consistent, minimally projected)
- [ ] writes idempotent via condition expressions; capacity mode matches the load

## Red Flags

- a `Scan` + filter on a request path (cost grows with the table)
- a low-cardinality partition key (status/boolean/date) -> hot partition + throttling
- modeling tables like a relational schema and joining in app code
- a GSI per "maybe" query (storage + write amplification) instead of per real pattern
- read-modify-write with no condition expression (lost updates under concurrency)
- single-table design adopted with no access pattern that actually needs it
