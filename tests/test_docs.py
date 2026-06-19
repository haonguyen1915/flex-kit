"""Project docs are indexed (path + title) and injected into agent bodies."""

from __future__ import annotations

from pathlib import Path

from flex_kit.docs import discover_docs, inject_docs, scaffold_docs
from flex_kit.init import init


def test_discover_docs_reads_path_and_title(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/api-spec.md").write_text("# API Spec\n\nrules...")
    (tmp_path / "docs/notitle.md").write_text("no heading here")

    docs = discover_docs(tmp_path, "docs")
    by_rel = {d.rel: d.title for d in docs}
    assert by_rel["docs/api-spec.md"] == "API Spec"
    assert by_rel["docs/notitle.md"] == "notitle"  # falls back to filename stem


def test_discover_docs_missing_dir_is_empty(tmp_path: Path) -> None:
    assert discover_docs(tmp_path, "docs") == []


def test_inject_docs_only_when_marker_present() -> None:
    docs = discover_docs(Path("."), "does-not-exist")  # -> []
    assert inject_docs("no marker here", docs) == "no marker here"
    assert "no project docs" in inject_docs("before <!-- DOCS --> after", docs)


def test_scaffold_docs_into_empty(tmp_path: Path) -> None:
    result = scaffold_docs(tmp_path, "docs")
    assert not result.bailed
    assert "docs/architecture.md" in result.created
    assert "docs/conventions/api.md" in result.created
    assert (tmp_path / "docs/architecture.md").read_text().startswith("# System Architecture")


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
    (tmp_path / "docs/architecture.md").write_text("# System Architecture\n")
    from flex_kit.gen import gen

    gen(tmp_path)

    planner = (tmp_path / ".claude/agents/planner.md").read_text()
    assert "docs/architecture.md - System Architecture" in planner
    assert "<!-- DOCS -->" not in planner  # marker was replaced
    # Codex agent gets the same index.
    codex = (tmp_path / ".codex/agents/planner.toml").read_text()
    assert "docs/architecture.md - System Architecture" in codex
