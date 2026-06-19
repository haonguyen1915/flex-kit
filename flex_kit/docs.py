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

from flex_kit.frontmatter import parse_skill

DOCS_MARKER = "<!-- DOCS -->"
_TEMPLATE_DOCS_DIR = Path(__file__).parent / "templates" / "docs"


@dataclass
class Doc:
    rel: str  # path relative to the project root, e.g. "docs/api-spec.md"
    label: str  # the doc's frontmatter `description`, else its `# ` heading, else stem


_INJECT_VALUES = {"true", "yes", "1", "on"}


def _heading(body: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _doc(path: Path, project_root: Path) -> Doc | None:
    """A Doc if the file opts in with frontmatter `inject: true`, else None."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---"):
        return None
    try:
        fm, body = parse_skill(text)
    except ValueError:
        return None
    if fm.get("inject", "").strip().lower() not in _INJECT_VALUES:
        return None
    label = fm.get("description", "").strip() or _heading(body) or path.stem
    return Doc(rel=path.relative_to(project_root).as_posix(), label=label)


def discover_docs(project_root: Path, docs_dir: str) -> list[Doc]:
    """Docs under `docs_dir` that opt in with frontmatter `inject: true`.

    Default is NOT to index a doc - only `inject: true` files are injected, so
    notes/drafts/human-only files don't add noise. Missing dir -> [].
    """
    root = project_root / docs_dir
    if not root.exists():
        return []
    docs: list[Doc] = []
    for path in sorted(root.rglob("*.md")):
        if path.is_file():
            doc = _doc(path, project_root)
            if doc is not None:
                docs.append(doc)
    return docs


def doc_catalog(docs: list[Doc]) -> str:
    if not docs:
        return "_(none - add `inject: true` to a doc's frontmatter to index it)_"
    return "\n".join(f"- {d.rel} - {d.label}" for d in docs)


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
