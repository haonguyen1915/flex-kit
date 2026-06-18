"""Plan lifecycle: create -> track active -> status/next-step -> close/archive."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from flex_kit import plan as plan_mod


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
