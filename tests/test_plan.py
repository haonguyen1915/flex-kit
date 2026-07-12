"""Plan lifecycle: create -> track active -> status/next-step -> close/archive."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from flex_kit import plan as plan_mod
from flex_kit.main import app

_runner = CliRunner()


def test_long_title_yields_a_short_folder_slug() -> None:
    long_title = "Tier 2 FE component tests audit coverage gaps and fill them all in"
    slug = plan_mod._slugify(long_title)
    assert len(slug) <= 40
    assert not slug.endswith("-") and "--" not in slug  # cut on a clean word boundary


def test_find_root_walks_up_to_the_flexkit_dir(tmp_path: Path) -> None:
    (tmp_path / ".flexkit").mkdir()
    deep = tmp_path / "src" / "pkg" / "mod"
    deep.mkdir(parents=True)
    assert plan_mod.find_root(deep) == tmp_path.resolve()  # found from a nested subdir
    assert plan_mod.find_root(tmp_path) == tmp_path.resolve()


def test_find_root_is_none_without_a_project(tmp_path: Path) -> None:
    assert plan_mod.find_root(tmp_path) is None  # no .flexkit/ up the tree


def test_plan_refuses_while_another_is_active(tmp_path: Path) -> None:
    plan_mod.create_plan(tmp_path, "first task", now=datetime(2026, 6, 18, 9, 0))
    res = _runner.invoke(app, ["plan", "second task", "--project", str(tmp_path)])
    assert res.exit_code != 0  # refused - finish the active one first
    assert plan_mod.active_plan(tmp_path).title == "first task"  # unchanged

    forced = _runner.invoke(app, ["plan", "second task", "--force", "--project", str(tmp_path)])
    assert forced.exit_code == 0  # --force overrides


def test_create_sets_active_and_parses(tmp_path: Path) -> None:
    when = datetime(2026, 6, 18, 9, 5)
    p = plan_mod.create_plan(tmp_path, "Add Auth Flow", mode="design", now=when)
    assert p.id == "260618-0905-add-auth-flow"
    assert p.mode == "design"
    assert (tmp_path / "plans/active" / p.id / "plan.md").exists()

    active = plan_mod.active_plan(tmp_path)
    assert active is not None and active.id == p.id


def test_status_and_next_step_track_checklist(tmp_path: Path) -> None:
    p = plan_mod.create_plan(tmp_path, "task", now=datetime(2026, 6, 18, 9, 0))
    md = p.dir / "plan.md"
    md.write_text(md.read_text().replace("- [ ] first step", "- [x] one\n- [ ] two\n- [ ] three"))

    active = plan_mod.active_plan(tmp_path)
    assert active is not None
    assert active.done_count == 1
    assert len(active.steps) == 3
    assert active.next_step is not None and active.next_step.text == "two"


def test_only_steps_section_checkboxes_are_counted(tmp_path: Path) -> None:
    # Checkboxes under ## Done Criteria (or any non-Steps section) must NOT count as steps.
    p = plan_mod.create_plan(tmp_path, "task", now=datetime(2026, 6, 18, 9, 0))
    (p.dir / "plan.md").write_text(
        "# Plan: task\n\n- id: x\n- mode: build\n- status: active\n\n"
        "## Steps\n\n- [x] step one\n- [ ] step two\n\n"
        "## Done Criteria\n\n- [ ] criteria a\n- [ ] criteria b\n- [ ] criteria c\n"
    )
    active = plan_mod.active_plan(tmp_path)
    assert active is not None
    assert len(active.steps) == 2  # 2 Steps, not 5 (the 3 Done-Criteria boxes excluded)
    assert active.done_count == 1
    assert active.next_step is not None and active.next_step.text == "step two"


def test_close_requires_confirm_then_archives(tmp_path: Path) -> None:
    p = plan_mod.create_plan(tmp_path, "task", now=datetime(2026, 6, 18, 9, 0))

    plan_mod.close_plan(tmp_path, confirm=False)  # no-op without confirm
    assert (tmp_path / "plans/active" / p.id).exists()
    assert plan_mod.active_plan(tmp_path) is not None

    plan_mod.close_plan(tmp_path, confirm=True)
    assert not (tmp_path / "plans/active" / p.id).exists()
    assert (tmp_path / "plans/archive" / p.id).exists()
    assert plan_mod.active_plan(tmp_path) is None


def test_close_without_active_errors(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        plan_mod.close_plan(tmp_path, confirm=True)


def test_scaffold_spec_creates_three_files(tmp_path: Path) -> None:
    plan_mod.create_plan(tmp_path, "big feature", mode="design", now=datetime(2026, 6, 18, 9, 0))
    p = plan_mod.scaffold_spec(tmp_path)
    for name in ("proposal.md", "design.md", "tasks.md"):
        assert (p.dir / "spec" / name).exists()
    assert "## Chosen Direction" in (p.dir / "spec/proposal.md").read_text()


def test_scaffold_spec_without_active_errors(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        plan_mod.scaffold_spec(tmp_path)
