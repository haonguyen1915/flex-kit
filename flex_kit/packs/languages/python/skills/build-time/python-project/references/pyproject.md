# pyproject.toml - annotated

The single source of project config (PEP 621). One file replaces `setup.py`,
`setup.cfg`, `requirements.txt`, and most tool dotfiles.

```toml
# --- how the package is built (required to be installable) ---
[build-system]
requires = ["hatchling"]          # the build backend's own deps
build-backend = "hatchling.build" # hatchling | setuptools | pdm-backend | flit-core | maturin (Rust ext)

# --- project metadata (PEP 621) ---
[project]
name = "my-pkg"                   # the distribution name (pip install my-pkg)
version = "0.1.0"                 # or dynamic = ["version"] to read from VCS/__init__
description = "One-line summary."
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"                   # SPDX expression (PEP 639)
authors = [{ name = "You", email = "you@example.com" }]
classifiers = ["Programming Language :: Python :: 3"]

# runtime deps - pin a FLOOR, never an exact ==; a lockfile pins exacts
dependencies = [
  "httpx>=0.27",
  "pydantic>=2",
]

# extras: installed only on request (pip install my-pkg[dev])
[project.optional-dependencies]
dev = ["pytest>=8", "ruff", "mypy"]

[project.urls]
Homepage = "https://github.com/you/my-pkg"
Issues = "https://github.com/you/my-pkg/issues"

# console commands: `name = "module.path:callable"` -> installs an executable
[project.scripts]
my-pkg = "my_pkg.cli:main"

# GUI variant (no console window on Windows)
[project.gui-scripts]
# my-pkg-gui = "my_pkg.gui:main"

# plugin hooks other packages discover at runtime
[project.entry-points."my_pkg.plugins"]
# default = "my_pkg.plugins.default"
```

## Choices that matter

- **Backend**: `hatchling` is a good modern default (fast, no boilerplate).
  `setuptools` for legacy/C-extension needs; `maturin` for Rust extensions.
- **version**: hard-coded `version = "…"` is simplest. `dynamic = ["version"]` +
  a VCS plugin (hatch-vcs) derives it from git tags - one source of truth.
- **Floors not exacts**: `dependencies` express compatibility (`>=0.27`); a
  lockfile (`uv.lock`, pip-tools `requirements.txt`) pins the resolved graph for
  reproducible deploys. Apps commit the lock; libraries don't.

## Layout this assumes

```
my_pkg/
├─ pyproject.toml
├─ uv.lock                 # app: commit; library: omit
├─ README.md
├─ src/
│  └─ my_pkg/
│     ├─ __init__.py
│     ├─ __main__.py       # `python -m my_pkg`
│     └─ cli.py            # main() referenced by [project.scripts]
└─ tests/
   └─ test_*.py
```
