---
name: python-concurrency
description: Choosing and using the right Python concurrency model - asyncio for I/O-bound, threads for blocking I/O, processes for CPU-bound - around the GIL, plus safe state sharing and structured tasks (TaskGroup, gather, to_thread). Use when code does many I/O calls, parallel CPU work, or you see a race/blocked event loop. Not for general idioms (see python-idioms).
---

# Python Concurrency

Pick the model by what the work is **waiting on**, because the GIL shapes the answer: one
thread runs Python bytecode at a time, so threads don't speed up pure-Python CPU work -
only I/O (where the GIL is released) or separate processes do.

## Choose the model

| Workload | Use | Why |
|---|---|---|
| Many network/disk calls, async libs | **asyncio** | one thread, thousands of awaits; no thread overhead |
| Blocking I/O in sync libraries | **threads** (`ThreadPoolExecutor`) | the GIL releases during the blocking call |
| CPU-bound (parse, crunch, compress) | **processes** (`ProcessPoolExecutor`) | each process has its own GIL → real parallelism |

Default to asyncio for I/O-heavy services; reach for processes only when profiling shows
CPU is the bottleneck. Don't use threads for CPU-bound Python - the GIL serializes it.

## asyncio - structured tasks

Prefer **`asyncio.TaskGroup`** (3.11+) over bare `create_task`: it awaits every child on
exit and cancels siblings if one fails, surfacing errors as an `ExceptionGroup` (no
silently-dropped task). `gather` is the older flat form.

```python
async def fetch_all(urls, client):
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(client.get(u)) for u in urls]
    return [t.result() for t in tasks]   # all done, or the group raised
```

Run a **blocking** call from async code with `asyncio.to_thread(fn, *args)` - never call a
sync-blocking function directly in a coroutine; it stalls the whole event loop.

```python
data = await asyncio.to_thread(legacy_blocking_read, path)
```

More: cancellation/timeouts, semaphore-bounded fan-out, sync↔async bridges in
[references/async-patterns.md](references/async-patterns.md).

## CPU-bound - processes

`ProcessPoolExecutor` sidesteps the GIL by running in child processes. Arguments and
results must be **picklable**, and the entry point must be guarded:

```python
from concurrent.futures import ProcessPoolExecutor

def main():
    with ProcessPoolExecutor() as pool:
        results = list(pool.map(is_prime, numbers))

if __name__ == "__main__":   # required: children re-import the module
    main()
```

## Sharing state safely

- **asyncio**: a single thread, so no data races *between awaits at a point* - but state
  can change across an `await`. Guard a multi-step critical section with `asyncio.Lock`.
- **threads**: shared mutable state needs an `threading.Lock`, or pass data through a
  `queue.Queue` (thread-safe) instead of sharing. Prefer immutable messages over locks.
- **processes**: no shared memory by default - pass data in/out (pickled). Don't reach
  for shared memory unless you measured it's needed.
- Cross-thread → event loop: `asyncio.run_coroutine_threadsafe(coro, loop)`.

## Review checklist

- [ ] model matches the bottleneck: asyncio/threads for I/O, processes for CPU
- [ ] no CPU-bound Python on a thread pool expecting speedup (GIL serializes it)
- [ ] async tasks under a `TaskGroup` (errors surface; siblings cancel) not orphaned
- [ ] blocking calls in async code wrapped in `asyncio.to_thread`, not run inline
- [ ] shared mutable state guarded by a lock, or replaced by a queue / immutable message
- [ ] `ProcessPoolExecutor` work is picklable and under `if __name__ == "__main__"`

## Red Flags

- a `requests`/`time.sleep`/sync-DB call inside a coroutine (blocks the event loop)
- threads spun up to parallelize a pure-Python computation (no gain - GIL)
- `create_task(...)` whose result/exception is never awaited (silently dropped)
- shared dict/list mutated from multiple threads with no lock
- `multiprocessing` passing an unpicklable arg (lambda, open socket, local closure)
