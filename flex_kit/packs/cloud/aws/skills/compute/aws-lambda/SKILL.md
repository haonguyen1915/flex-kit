---
name: aws-lambda
description: Writing AWS Lambda functions well - a thin handler over testable core logic, init (clients, config) outside the handler to cut cold starts, config from env + Secrets Manager, idempotency, a least-privilege execution role, structured CloudWatch logging, and memory/timeout tuning. Use when authoring or reviewing a Lambda, designing an event handler, or debugging cold starts/timeouts. Not for IAM policy detail (see aws-iam) or app layering (see python-architecture).
---

# AWS Lambda

A Lambda is a function AWS runs on an event. Two things decide whether it's good: the
**handler stays thin over testable logic**, and **expensive init happens once, outside the
handler** - perf, cost, and security mostly follow from those.

## Thin handler, testable core

Keep `lambda_handler` to: parse the event, call a plain function, shape the response. Put the
real work in a normal function you can unit-test without Lambda.

```python
def lambda_handler(event, context):
    order_id = event["order_id"]               # parse/validate the event
    return process_order(order_id, repo)       # delegate to testable core

def process_order(order_id, repo):             # plain function, unit-tested directly
    ...
```

## Init outside the handler (cold starts)

A **cold start** = AWS downloads the code, starts the runtime, and runs your module-level init
before the first handler call. Create clients, load config, open pools **once at module
scope** so warm invocations reuse them:

```python
import boto3, os
s3 = boto3.client("s3")            # reused across warm invocations - not per call
TABLE = os.environ["TABLE_NAME"]   # config from env, set by IaC
```

- Keep the package small; lazy-import heavy libs only on the path that needs them.
- Tune **memory** - it scales CPU too, so more memory often runs *faster and cheaper*. Set a
  **timeout** just above the p99, not the 15-minute max.

## Config & sensitive values

- Plain config -> **environment variables** (set in IaC, not hard-coded).
- Sensitive values -> **SSM Parameter Store (SecureString)** or **Secrets Manager**, read once at init;
  never bake a key into the code or a plain env var. The execution role grants read access.

## Idempotency & errors

- An event may be **delivered more than once** (retries, at-least-once sources). Make the
  handler idempotent - dedupe on an id (a conditional DynamoDB write, an idempotency key).
- Let unhandled errors **raise** so Lambda records the failure and retries / DLQs per config;
  don't swallow and return 200. Configure a **DLQ / on-failure destination** for poison events.

## Least privilege & logging

- The function's **execution role** gets only the actions it uses (see aws-iam) - one role per
  function, scoped to its tables/buckets.
- Log **structured JSON** to CloudWatch (carry a request id, not free text); Lambda Powertools
  gives a logger/tracer/metrics + a cold-start metric. Worked handler + a SAM snippet:
  [references/handler.md](references/handler.md).

## Review checklist

- [ ] handler is thin; business logic in a plain, unit-tested function
- [ ] clients/config initialized at module scope, reused across invocations
- [ ] config from env vars; sensitive values from SSM/Secrets Manager, not literals
- [ ] handler is idempotent (events can arrive more than once)
- [ ] errors raise (with a DLQ/destination), not swallowed into a 200
- [ ] execution role is least-privilege; logs are structured JSON to CloudWatch
- [ ] memory tuned (CPU scales with it); timeout near p99, not the max

## Red Flags

- creating a boto3 client / DB connection *inside* the handler (re-made every call)
- a key or token baked into the code or a plain env var
- a handler holding all the logic, impossible to test without invoking Lambda
- no idempotency on an at-least-once event source (double-processing)
- a catch-all that returns 200 on failure (Lambda never retries; the event is lost)
- timeout left at a high default "to be safe" (a hung call bills the full duration)
