# pytest patterns

Recipes beyond the core. All use only pytest + stdlib unless noted.

## tmp_path - a real filesystem, isolated per test

`tmp_path` is a unique `pathlib.Path` per test; pytest cleans it up.

```python
def test_writes_report(tmp_path):
    out = tmp_path / "report.txt"
    write_report(out, data)
    assert out.read_text() == "expected"
```

## Fixture as setup + teardown

`yield` splits arrange from cleanup; everything after `yield` runs even if the test fails.

```python
@pytest.fixture
def db_session():
    session = make_session()
    yield session            # the test runs here
    session.rollback()       # teardown, always runs
    session.close()
```

## monkeypatch at a boundary

Replace an attribute or env var; auto-undone after the test.

```python
def test_uses_env(monkeypatch):
    monkeypatch.setenv("API_URL", "http://fake")
    monkeypatch.setattr(mod, "now", lambda: FIXED_TIME)
    ...
```

Patch where the name is *looked up*: if `app.py` does `from time import time`, patch
`app.time`, not `time.time`.

## Parametrize incl. the error case

`contextlib.nullcontext` lets one parametrized test mix passing and raising rows:

```python
from contextlib import nullcontext
import pytest

@pytest.mark.parametrize("x, expect", [
    (2, nullcontext(3.0)),
    (0, pytest.raises(ZeroDivisionError)),
])
def test_div(x, expect):
    with expect as e:
        assert 6 / x == e
```

## Spies with pytest-mock

`mocker` (from `pytest-mock`) wraps `unittest.mock` with auto-undo - use it to assert a
call happened, sparingly:

```python
def test_notifies(mocker):
    spy = mocker.spy(notifier, "order_placed")
    place_order("o1", 5, repo, notifier)
    spy.assert_called_once_with("o1")
```

## Async tests

With `pytest-asyncio` installed and `asyncio_mode = "auto"` in pyproject, just write
`async def test_...`. Otherwise mark each: `@pytest.mark.asyncio`.

```python
async def test_fetch():
    result = await fetch(client)
    assert result.ok
```

## Markers - select / skip

```python
@pytest.mark.slow
def test_big(): ...

@pytest.mark.skipif(sys.platform == "win32", reason="posix only")
def test_posix(): ...
```

Register custom markers in pyproject to avoid warnings:

```toml
[tool.pytest.ini_options]
markers = ["slow: long-running tests"]
```

Run a subset: `pytest -m "not slow"`.
