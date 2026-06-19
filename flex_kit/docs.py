"""Discover project docs and inject an index into agent/command bodies.

A project's specs/conventions live as plain markdown under a docs dir (default
`docs/`). Rather than copy them into the kit, the build injects a one-line-per-doc
*index* (path + title) at a `<!-- DOCS -->` marker, so an agent knows what specs
exist and can read the relevant one on demand - no context bloat from full content.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

DOCS_MARKER = "<!-- DOCS -->"
_TEMPLATE_DOCS_DIR = Path(__file__).parent / "templates" / "docs"


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


@dataclass
class ScaffoldResult:
    docs_dir: str
    created: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    bailed: bool = False  # docs/ already had content and --force was not given
    existing_count: int = 0


def scaffold_docs(project_root: Path, docs_dir: str, force: bool = False) -> ScaffoldResult:
    """Write a docs/ skeleton (architecture, conventions, domain, adr).

    Never overwrites: existing files are skipped. If `docs_dir` already has content and
    `force` is not set, bails (so an organized docs/ is not cluttered); `force` then
    additively merges only the missing skeleton files.
    """
    target = project_root / docs_dir
    result = ScaffoldResult(docs_dir=docs_dir)

    existing = [p for p in target.rglob("*") if p.is_file()] if target.exists() else []
    if existing and not force:
        result.bailed = True
        result.existing_count = len(existing)
        return result

    for src in sorted(_TEMPLATE_DOCS_DIR.rglob("*")):
        if not src.is_file():
            continue
        rel = (Path(docs_dir) / src.relative_to(_TEMPLATE_DOCS_DIR)).as_posix()
        dest = project_root / rel
        if dest.exists():
            result.skipped.append(rel)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        result.created.append(rel)
    return result
