---
name: engineering-concurrency
description: Design correct concurrent and async code, language-agnostic - sharing state safely, lock discipline, races, deadlock, cancellation. Use when designing or reviewing concurrency: shared mutable state, a lock held across an await, race conditions, deadlocks. For a language's primitives (Rust async/Send-Sync, Go channels), use the language pack.
---

# Concurrency Design

Concurrency bugs are the ones that pass every test and fail in production. The safest
concurrent code shares nothing mutable; when you must share, make the rules explicit and
local, not spread across call sites.

## Share less

- Prefer **immutability** and **message passing** (channels / queues) over shared mutable
  state - data you don't share can't race.
- If state is shared, give it **one owner** that serializes access, rather than many call
  sites locking it ad hoc.
- Confine mutable state to a single task / thread where you can; pass copies or ownership, not
  references to mutate.

## Lock discipline

- Hold a lock for the **shortest** critical section; never do I/O or call unknown code while
  holding it.
- **Never hold a lock across an `await`** / blocking call - the task can suspend while holding
  it and deadlock.
- Acquire multiple locks in a **consistent global order** everywhere; inconsistent order is
  the classic deadlock.
- Guard *all* access to a piece of shared state with the *same* lock - one unguarded path
  defeats the rest.

## Async pitfalls

- A function is only as async as its slowest blocking call - don't block the event loop /
  runtime with sync I/O inside async code.
- Read shared inputs **synchronously**; capturing them inside a deferred callback (a timer, a
  continuation, a detached task) reads a stale or racing value by the time it runs.
- `await` in a loop serializes; fan out with a join / gather when the work is independent -
  but bound the concurrency so you don't exhaust connections.

## Races & atomicity

- A check-then-act on shared state (read, decide, write) is a race unless the whole sequence
  is atomic (a lock, a compare-and-swap, a transaction).
- Two parallel collections meant to stay aligned by index *will* drift - model them as one.

## Cancellation & failure

- A task cancelled or failing mid-operation must leave shared state consistent - release
  locks, roll back, close handles on every exit path, including the error path.
- Decide what a partial failure means: does one failed task abort the batch, or is it
  isolated? Make it explicit, not accidental.

## Review checklist

- [ ] shared mutable state is minimized; prefer immutability / message passing
- [ ] no lock or guard is held across an `await` or blocking call
- [ ] multiple locks are always acquired in one consistent order
- [ ] all access to a shared value uses the same guard
- [ ] check-then-act on shared state is made atomic
- [ ] cleanup (unlock, rollback, close) runs on every path, including cancellation / error

## Red Flags

- a lock / guard held across an `await` or a network call
- the same shared value locked on some paths, accessed freely on others
- a deferred callback (timer / continuation) capturing a shared value that may change underneath
- two parallel arrays / vectors expected to stay the same length
- a new field in a shared struct that isn't safe to send across threads
- an error path that returns while a lock is still held
