---
name: python-observability
description: Making a running Python app observable - per-module loggers, structured logging configured once at the entry point (never in libraries), log levels, exception logging, and emitting metrics. Use when adding logging/metrics, diagnosing a production issue, or reviewing diagnostic output. Not for build/test tool config (see python-project) or exception design (see python-error-handling).
---

# Python Observability

Logging and metrics are how you understand a running system. The core rule: **libraries
emit, the application configures** - a reusable module never dictates where logs go.

## Per-module loggers

Get a logger named after the module; never log on the root logger or `print`. The
`__name__` hierarchy lets the app tune verbosity per package (`logging.getLogger("shop.db")`).

```python
import logging
logger = logging.getLogger(__name__)   # at module top

def place_order(...):
    logger.info("order placed", extra={"ref": ref, "qty": qty})
```

A **library/package** adds only a `NullHandler` so it stays silent until an app configures
logging - it must not add stream/file handlers or call `basicConfig`:

```python
logging.getLogger("shop").addHandler(logging.NullHandler())
```

## Configure once, at the entry point

Handlers, formatters, and levels are set **one time** in the application's composition root
(`main()`/bootstrap), driven by runtime config (env/settings) - this is a *runtime* concern,
distinct from build-time tool config in `pyproject`.

```python
def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
```

For production, attach a **JSON/structured** formatter so logs are queryable by field
(`python-json-logger` or a custom `Formatter`); pass context via `extra={...}`, not f-string
concatenation - structured fields survive log aggregation, interpolated strings don't.

## Levels - mean them

- `DEBUG` developer detail; `INFO` normal lifecycle events; `WARNING` something off but
  handled; `ERROR` an operation failed; `CRITICAL` the app can't continue.
- Use lazy `%`-args, not f-strings: `logger.info("user %s", uid)` - the format is skipped
  if the level is disabled.
- In an `except`, use `logger.exception("...")` (ERROR + traceback); log it **once**, at the
  boundary that handles it (see python-error-handling), not at every layer.

## Metrics

Emit counters/histograms for rates and latency (`prometheus_client`, OpenTelemetry, or
StatsD) at the same boundaries you log. Name them consistently, keep label cardinality low
(no user-ids as labels), and measure the things you'd page on: request rate, error rate,
latency. Don't reinvent a metrics store - export to the platform's collector.

## Review checklist

- [ ] `logger = logging.getLogger(__name__)` per module; no `print` for diagnostics
- [ ] libraries add only `NullHandler`; no handler/`basicConfig` outside the app entry
- [ ] logging configured once at the composition root from runtime config
- [ ] context passed via `extra={...}` / structured fields, not string-concatenated
- [ ] levels used meaningfully; `logger.exception` in handlers; logged once at the edge
- [ ] metrics at the same boundaries; low label cardinality; exported, not home-grown

## Red Flags

- `print()` (or `logging.info` on the root) used as application logging
- a library calling `basicConfig`/adding a `StreamHandler` (hijacks the app's config)
- `logger.info(f"user {uid} did {action}")` - unstructured, eager, unqueryable
- the same error logged and re-logged at every layer it passes through
- a metric label with unbounded cardinality (user id, request id, raw URL)
