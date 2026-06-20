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

from flex_kit.frontmatter import parse_skill, replace_marker

DOCS_MARKER = "<!-- DOCS -->"
ALL = "all"  # a target that reaches every doc consumer
_TEMPLATE_DOCS_DIR = Path(__file__).parent / "templates" / "docs"


@dataclass
class Doc:
    rel: str  # path relative to the project root, e.g. "docs/api-spec.md"
    label: str  # the doc's frontmatter `description`, else its `# ` heading, else stem
    targets: frozenset[str]  # who gets it: {"all"}, or agent ids / lanes


_ALL_VALUES = {"true", "yes", "1", "on", ALL}
_FALSE_VALUES = {"", "false", "no", "0", "off"}


def _heading(body: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _targets(inject: str) -> frozenset[str] | None:
    """Parse the `inject` value into target keys, or None if the doc opts out.

    `true` / `all` -> every consumer. A comma list (`reviewer, build`) -> the named
    agent ids and/or lanes. Falsy or absent -> None (not indexed).
    """
    val = inject.strip().lower()
    if val in _FALSE_VALUES:
        return None
    if val in _ALL_VALUES:
        return frozenset({ALL})
    keys = frozenset(t.strip() for t in val.split(",") if t.strip())
    return keys or None


def _doc(path: Path, project_root: Path) -> Doc | None:
    """A Doc if the file opts in with frontmatter `inject:`, else None."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---"):
        return None
    try:
        fm, body = parse_skill(text)
    except ValueError:
        return None
    targets = _targets(fm.get("inject", ""))
    if targets is None:
        return None
    label = fm.get("description", "").strip() or _heading(body) or path.stem
    return Doc(rel=path.relative_to(project_root).as_posix(), label=label, targets=targets)


def discover_docs(project_root: Path, docs_dir: str) -> list[Doc]:
    """Docs under `docs_dir` that opt in with frontmatter `inject:`.

    Default is NOT to index a doc - only `inject:` files are injected, so
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


def _matches(doc: Doc, consumer: frozenset[str]) -> bool:
    """A doc reaches a consumer when it targets `all` or any of the consumer's keys
    (its agent id and lane)."""
    return ALL in doc.targets or bool(doc.targets & consumer)


def doc_catalog(docs: list[Doc], consumer: frozenset[str]) -> str:
    selected = [d for d in docs if _matches(d, consumer)]
    if not selected:
        return "_(none - tag a doc `inject: all` or `inject: <agent>` to index it here)_"
    return "\n".join(f"- {d.rel} - {d.label}" for d in selected)


def inject_docs(body: str, docs: list[Doc], consumer: frozenset[str]) -> str:
    return replace_marker(body, DOCS_MARKER, doc_catalog(docs, consumer))


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
