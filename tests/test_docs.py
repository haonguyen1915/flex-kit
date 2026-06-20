"""Project docs are indexed (path + title) and injected into agent bodies."""

from __future__ import annotations

from pathlib import Path

from flex_kit.docs import discover_docs, inject_docs, scaffold_docs
from flex_kit.init import init


def test_discover_indexes_only_inject_true(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/api.md").write_text("---\ninject: true\ndescription: API contract\n---\n\n# API\n")
    (tmp_path / "docs/heading.md").write_text("---\ninject: true\n---\n\n# Heading Only\n")
    (tmp_path / "docs/notes.md").write_text("# Random notes\nnot for agents")  # no inject

    by_rel = {d.rel: d.label for d in discover_docs(tmp_path, "docs")}
    assert by_rel == {
        "docs/api.md": "API contract",  # label = description
        "docs/heading.md": "Heading Only",  # falls back to the `# ` heading
    }
    assert "docs/notes.md" not in by_rel  # not opted in -> excluded (no noise)


def test_discover_docs_missing_dir_is_empty(tmp_path: Path) -> None:
    assert discover_docs(tmp_path, "docs") == []


def test_inject_docs_only_when_marker_present() -> None:
    docs = discover_docs(Path("."), "does-not-exist")  # -> []
    consumer = frozenset({"reviewer"})
    assert inject_docs("no marker here", docs, consumer) == "no marker here"
    # a standalone marker line is replaced...
    assert "inject:" in inject_docs("before\n<!-- DOCS -->\nafter", docs, consumer)
    # ...but an inline mention in prose is left untouched (markers are line-level)
    prose = "see the `<!-- DOCS -->` marker"
    assert inject_docs(prose, docs, consumer) == prose


def test_inject_targets_by_agent_and_lane(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/r.md").write_text("---\ninject: reviewer\ndescription: review spec\n---\n# R\n")
    (tmp_path / "docs/b.md").write_text("---\ninject: build\ndescription: build spec\n---\n# B\n")
    (tmp_path / "docs/a.md").write_text("---\ninject: all\ndescription: everyone\n---\n# A\n")
    docs = discover_docs(tmp_path, "docs")
    marker = "<!-- DOCS -->"

    reviewer = inject_docs(marker, docs, frozenset({"reviewer", "review"}))
    assert "docs/r.md" in reviewer and "docs/a.md" in reviewer and "docs/b.md" not in reviewer

    planner = inject_docs(marker, docs, frozenset({"planner", "build"}))
    assert "docs/b.md" in planner and "docs/a.md" in planner and "docs/r.md" not in planner


def test_scaffold_docs_into_empty(tmp_path: Path) -> None:
    result = scaffold_docs(tmp_path, "docs")
    assert not result.bailed
    assert "docs/architecture.md" in result.created
    assert "docs/conventions/api.md" in result.created
    arch = (tmp_path / "docs/architecture.md").read_text()
    assert "inject: true" in arch and "# System Architecture" in arch


def test_scaffold_docs_bails_when_nonempty(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/mine.md").write_text("# My spec")
    result = scaffold_docs(tmp_path, "docs")
    assert result.bailed and result.existing_count == 1
    assert result.created == []
    assert (tmp_path / "docs/mine.md").read_text() == "# My spec"  # untouched
    assert not (tmp_path / "docs/architecture.md").exists()  # nothing added


def test_scaffold_docs_force_merges_without_overwriting(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/architecture.md").write_text("# Mine\nkeep me")
    result = scaffold_docs(tmp_path, "docs", force=True)
    assert "docs/architecture.md" in result.skipped  # existing -> skipped, never overwritten
    assert "docs/conventions/api.md" in result.created  # missing -> added
    assert (tmp_path / "docs/architecture.md").read_text() == "# Mine\nkeep me"


def test_gen_injects_doc_index_into_agents(tmp_path: Path) -> None:
    init(tmp_path)  # scaffolds + gens; planner has a <!-- DOCS --> marker
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / "docs/architecture.md").write_text(
        "---\ninject: true\ndescription: System architecture overview\n---\n\n# System Architecture\n"
    )
    from flex_kit.gen import gen

    gen(tmp_path)

    planner = (tmp_path / ".claude/agents/planner.md").read_text()
    assert "docs/architecture.md - System architecture overview" in planner
    assert "<!-- DOCS -->" not in planner  # marker was replaced
    # Codex agent gets the same index.
    codex = (tmp_path / ".codex/agents/planner.toml").read_text()
    assert "docs/architecture.md - System architecture overview" in codex
