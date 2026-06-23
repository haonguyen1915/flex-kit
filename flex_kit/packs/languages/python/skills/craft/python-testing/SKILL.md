---
name: python-testing
description: How to test Python with pytest - test layout, fixtures + conftest, parametrize for cases, monkeypatch/fakes at seams, pytest.raises, and what is worth testing vs not. Use when writing or reviewing tests, setting up pytest, or deciding test coverage. Not for app wiring that makes code testable (see python-architecture) or build config (see python-project).
---

# Python Testing

Tests exist to let you change code with confidence. Test **behavior at the seams you
designed** (services, ports), not implementation detail - so a refactor that preserves
behavior keeps the tests green.

## Layout

`tests/` mirrors `src/`; files are `test_*.py`, functions `test_*`. Use plain `assert` -
pytest rewrites it to show the actual values. Shared setup goes in `conftest.py`, which
pytest auto-discovers (no import); a `conftest.py` deeper in the tree adds fixtures for
that subtree only.

```
tests/
├─ conftest.py          # shared fixtures, auto-discovered
├─ test_orders.py
└─ integration/
   └─ test_db.py
```

## Fixtures over setup boilerplate

A fixture is a named, reusable arrange step requested as a function argument. Give it the
narrowest `scope` that works (`function` default; `session` for expensive shared state).

```python
@pytest.fixture
def repo() -> FakeRepo:
    return FakeRepo()

def test_place_order(repo):
    place_order("o1", 5, repo, FakeNotifier())
    assert repo.get("o1") is not None
```

## Parametrize - one test, many cases

Don't copy-paste a test for each input. `@pytest.mark.parametrize` runs the body once per
row and reports each separately:

```python
@pytest.mark.parametrize("qty, available, ok", [(5, 10, True), (10, 5, False)])
def test_can_fulfill(qty, available, ok):
    assert Order("o", qty).can_fulfill(available) is ok
```

## Seams, not mocks-everywhere

Prefer a hand-written **fake** that satisfies a `Protocol` port over a mock (see
python-architecture) - it's typed and survives refactors. Use `monkeypatch` to replace an
attribute/env var at a boundary (auto-undone after the test); use the `mocker` fixture
(pytest-mock) for spies/asserting calls. Patch where the name is *used*, not where defined.

Assert on errors with `pytest.raises`:

```python
with pytest.raises(OrderNotFound):
    place_order("dup", 1, repo_with_dup, notifier)
```

More patterns (tmp_path, fixtures-as-context, async, markers) in
[references/pytest-patterns.md](references/pytest-patterns.md).

## What to test (and not)

- **Do**: public behavior, edge cases, each branch of a decision, the error paths,
  regressions (a test that fails before the fix).
- **Don't**: private helpers directly, third-party libraries, trivial getters, or the
  exact internal calls (that locks in implementation and breaks on refactor).

## Review checklist

- [ ] tests mirror `src/`; `test_*` names; plain `assert`
- [ ] shared arrange in fixtures / `conftest.py`, scoped as narrowly as possible
- [ ] multiple cases via `parametrize`, not copy-pasted test bodies
- [ ] fakes at `Protocol` seams; `monkeypatch`/`mocker` only at real boundaries
- [ ] error paths asserted with `pytest.raises`
- [ ] tests assert behavior/output, not internal call sequences

## Red Flags

- mocking the unit under test instead of its dependencies
- a test that mirrors the implementation line-for-line (breaks on any refactor)
- `time.sleep` / real network / real DB in a unit test (slow, flaky - fake the seam)
- no failing-first test for a bug fix (you didn't prove the bug or the fix)
- one giant test asserting twenty things - split by behavior or parametrize
