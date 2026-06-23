# Tooling - ruff, mypy, pytest

All config lives in `pyproject.toml` under `[tool.*]`, so one file governs the
project. Run all three in CI and a pre-commit gate.

## ruff - lint + format

Ruff replaces flake8 + isort + black (and many plugins) in one fast tool. By
default it enables only Pyflakes (`F`) and a pycodestyle subset (`E4`,`E7`,`E9`);
opt into more deliberately.

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
# F=pyflakes, E/W=pycodestyle, I=isort, UP=pyupgrade, B=bugbear, SIM=simplify
select = ["E", "F", "W", "I", "UP", "B", "SIM"]
ignore = []

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]   # asserts are fine in tests
```

- `ruff check .` lints; `ruff check --fix` auto-fixes; `ruff format .` formats.
- The formatter owns line wrapping, so `E501` (line-too-long) is off by default;
  add it back with `extend-select = ["E501"]` only if you want the lint too.

## mypy - static types

Start strict on your own code; loosen per-module for untyped third-party packages.

```toml
[tool.mypy]
python_version = "3.10"
strict = true                 # the bundle: disallow-untyped-defs, no-implicit-optional, …
warn_unused_ignores = true
files = ["src", "tests"]

[[tool.mypy.overrides]]
module = ["some_untyped_lib.*"]
ignore_missing_imports = true
```

`strict = true` is the high-value switch - it turns on the full bundle at once.
Relax individual flags only with a reason.

## pytest - tests

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q"            # show extra summary, quiet dots
pythonpath = ["src"]          # import the src/ package without an install (or use editable install)
```

- `testpaths` stops pytest scanning the whole tree.
- With src/ layout, either `pip install -e .` or `pythonpath = ["src"]` makes the
  package importable; prefer the editable install so tests hit the real package.

## Wiring it together

A typical gate (CI step or pre-commit):

```bash
ruff check . && ruff format --check . && mypy && pytest
```

Make targets / a `Makefile` or `pre-commit` config keep the same four commands in
one place so local and CI agree.
