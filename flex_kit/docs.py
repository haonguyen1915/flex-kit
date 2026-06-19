"""Discover project docs and inject an index into agent/command bodies.

A project's specs/conventions live as plain markdown under a docs dir (default
`docs/`). Rather than copy them into the kit, the build injects a one-line-per-doc
*index* (path + title) at a `<!-- DOCS -->` marker, so an agent knows what specs
exist and can read the relevant one on demand - no context bloat from full content.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DOCS_MARKER = "<!-- DOCS -->"


@dataclass
class Doc:
    rel: str  # path relative to the project root, e.g. "docs/api-spec.md"
    title: str  # the file's first `# ` heading, or its filename stem


def _title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def discover_docs(project_root: Path, docs_dir: str) -> list[Doc]:
    """All `.md` under `docs_dir`, as (repo-relative path, title). Missing dir -> []."""
    root = project_root / docs_dir
    if not root.exists():
        return []
    return [
        Doc(rel=path.relative_to(project_root).as_posix(), title=_title(path))
        for path in sorted(root.rglob("*.md"))
        if path.is_file()
    ]


def doc_catalog(docs: list[Doc]) -> str:
    if not docs:
        return "_(no project docs found)_"
    return "\n".join(f"- {d.rel} - {d.title}" for d in docs)


def inject_docs(body: str, docs: list[Doc]) -> str:
    if DOCS_MARKER not in body:
        return body
    return body.replace(DOCS_MARKER, doc_catalog(docs))
