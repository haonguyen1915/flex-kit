# asyncio patterns

Common shapes beyond `gather`/`TaskGroup`. All stdlib `asyncio`.

## Entry point

One `asyncio.run()` at the top; never call it twice or nest it. Everything below is
`async def` and awaited.

```python
async def main() -> None:
    ...

if __name__ == "__main__":
    asyncio.run(main())
```

## Bounded fan-out with a semaphore

Unbounded `create_task` over 10k urls opens 10k sockets. Cap concurrency:

```python
async def fetch_capped(urls, client, limit=20):
    sem = asyncio.Semaphore(limit)
    async def one(u):
        async with sem:
            return await client.get(u)
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(one(u)) for u in urls]
    return [t.result() for t in tasks]
```

## Timeouts and cancellation

`asyncio.timeout` (3.11+) cancels the block if it overruns; handle the resulting error.

```python
try:
    async with asyncio.timeout(5):
        data = await slow_call()
except TimeoutError:
    data = fallback()
```

Cancellation propagates as `CancelledError` - let it bubble; only catch it to do cleanup,
then re-raise. Never swallow it (it breaks shutdown).

## Don't block the loop

Anything CPU-bound or sync-blocking starves every other task. Offload it:

```python
# blocking I/O in a sync lib  →  a thread
rows = await asyncio.to_thread(db.execute, query)

# CPU-bound  →  a process pool, driven from async
loop = asyncio.get_running_loop()
with ProcessPoolExecutor() as pool:
    result = await loop.run_in_executor(pool, heavy_compute, payload)
```

## Async resources

Use `async with` / `async for` for async context managers and iterators - the sync forms
won't await setup/teardown.

```python
async with httpx.AsyncClient() as client:      # async __aenter__/__aexit__
    async for chunk in client.stream(...):
        ...
```

## Bridging threads → the loop

From a non-async thread, submit work to a running loop and wait on the returned
`concurrent.futures.Future`:

```python
fut = asyncio.run_coroutine_threadsafe(handle(event), loop)
result = fut.result(timeout=10)
```

## Locks across awaits

asyncio is single-threaded, but state can change while you're suspended at `await`. Guard a
multi-step invariant:

```python
lock = asyncio.Lock()
async def transfer(a, b, amt):
    async with lock:                # no other task interleaves these awaits
        await a.debit(amt)
        await b.credit(amt)
```
