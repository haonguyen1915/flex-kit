"""Mode escalation: a plan that grows past its budget escalates."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from flex_kit import modes
from flex_kit import plan as plan_mod


def test_small_patch_stays_patch() -> None:
    v = modes.effective_mode("patch", n_steps=2, n_files=1)
    assert v.effective == "patch" and v.reason is None


def test_patch_escalates_to_build_on_steps() -> None:
    v = modes.effective_mode("patch", n_steps=5)
    assert v.effective == "build" and "steps=5" in v.reason


def test_patch_escalates_to_build_on_files() -> None:
    v = modes.effective_mode("patch", n_steps=1, n_files=3)
    assert v.effective == "build" and "files=3" in v.reason


def test_build_escalates_to_design() -> None:
    v = modes.effective_mode("build", n_steps=20)
    assert v.effective == "design"


def test_patch_can_escalate_two_steps_to_design() -> None:
    v = modes.effective_mode("patch", n_steps=20)
    assert v.effective == "design"


def test_create_plan_rejects_invalid_mode(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        plan_mod.create_plan(tmp_path, "task", mode="huge")


def test_plan_parses_files_and_computes_verdict(tmp_path: Path) -> None:
    p = plan_mod.create_plan(tmp_path, "task", mode="patch", now=datetime(2026, 6, 18, 9, 0))
    md = p.dir / "plan.md"
    md.write_text(
        md.read_text()
        .replace("- [ ] first step", "- [ ] a\n- [ ] b\n- [ ] c\n- [ ] d")
        .replace("_- path/to/file_", "- src/a.py\n- src/b.py\n- src/c.py")
    )
    reread = plan_mod.active_plan(tmp_path)
    assert reread is not None
    assert len(reread.files) == 3
    assert reread.mode_verdict.effective == "build"  # 4 steps > 3 escalates patch
