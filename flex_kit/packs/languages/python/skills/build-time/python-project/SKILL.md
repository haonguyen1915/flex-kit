---
name: python-project
description: Standard Python project setup - src/ layout, pyproject.toml (PEP 621) metadata + dependencies, a build backend, a pinned venv, console entry points, and ruff/mypy/pytest config. Use when starting a Python package, fixing imports/packaging, or wiring tooling. Not for runtime app structure (see python-architecture) or runtime logging/metrics (see python-observability).
---

# Python Project

How a Python package is laid out and built - the **build-time** surface: directory
shape, `pyproject.toml`, dependencies, and the tool config that gates every commit.

## src/ layout

Put importable code under `src/`, tests as a sibling:

```
my_pkg/
├─ pyproject.toml
├─ src/my_pkg/__init__.py   __main__.py  cli.py  …
└─ tests/test_*.py
```

Prefer **src/ layout** over a top-level package: it forces you to import the *installed*
package, not the working dir, so tests run against what users actually get and "works on
my machine" import bugs surface immediately. Develop with an editable install:
`pip install -e .` (or `uv sync`). Every package directory needs `__init__.py`; a CLI
entry module is `__main__.py` (enables `python -m my_pkg`).

## pyproject.toml

One file, PEP 621 `[project]` table - never `setup.py`/`setup.cfg` for new work. Declare
a build backend so the package is installable. Skeleton (full annotated version in
[references/pyproject.md](references/pyproject.md)):

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-pkg"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["httpx>=0.27"]

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]

[project.scripts]
my-pkg = "my_pkg.cli:main"     # installs a `my-pkg` console command
```

- Pin the **floor** of runtime deps (`>=`), not an exact `==`; let a lockfile pin exacts.
- Dev/test deps go in `optional-dependencies`, not runtime `dependencies`.
- A lock (`uv.lock`, `requirements.txt` via pip-tools) pins the full graph for
  reproducible installs - commit it for apps, omit for libraries.

## Tooling (config lives in pyproject)

Co-locate tool config in `pyproject.toml` so one file governs the project. Run all three
in CI and a pre-commit gate. See [references/tooling.md](references/tooling.md).

- **ruff** - lint + format (replaces flake8/isort/black); `ruff check` + `ruff format`.
- **mypy** - static types; start `strict = true` on `src/`, loosen per-module if needed.
- **pytest** - tests; set `testpaths`, `pythonpath`/`addopts` so `pytest` just works.

## Review checklist

- [ ] importable code under `src/<pkg>/`, tests in a sibling `tests/`
- [ ] `pyproject.toml` with a `[build-system]` backend + PEP 621 `[project]` table
- [ ] runtime deps pinned to a floor; dev deps in `optional-dependencies`
- [ ] console commands declared via `[project.scripts]`, not ad-hoc shell wrappers
- [ ] ruff + mypy + pytest configured in `pyproject` and run in CI
- [ ] developed via an editable install (`pip install -e .` / `uv sync`)

## Red Flags

- a top-level package (flat layout) importing itself from the working dir, masking
  packaging bugs until release
- `setup.py`/`setup.cfg` for a brand-new project instead of `pyproject.toml`
- runtime `dependencies` swollen with `pytest`/`ruff` (dev tools shipped to users)
- exact `==` pins in `dependencies` (that's a lockfile's job; here it blocks resolution)
- a `bin/` shell script doing what `[project.scripts]` should declare
