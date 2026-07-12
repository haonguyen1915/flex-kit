"""Cross-model codex review - mocked so tests never call the real codex CLI."""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

import pytest

from flex_kit import plan as plan_mod
from flex_kit.codex_review import build_prompt, codex_review


def _plan(tmp_path: Path) -> None:
    plan_mod.create_plan(tmp_path, "task", now=datetime(2026, 6, 18, 9, 0))


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)


def test_build_prompt_file(tmp_path: Path) -> None:
    (tmp_path / "x.py").write_text("print(1)\n")
    prompt = build_prompt(tmp_path, "file", "x.py")
    assert "print(1)" in prompt and "independent reviewer" in prompt


def test_dry_run_defers_model_to_codex_by_default(tmp_path: Path) -> None:
    _plan(tmp_path)
    res = codex_review(tmp_path, dry_run=True)
    assert res.command[:2] == ["codex", "exec"]
    assert res.model is None and "-m" not in res.command  # no pin -> Codex uses its own default
    assert not res.report_path.exists()  # dry-run writes nothing


def test_dry_run_pins_an_explicit_model(tmp_path: Path) -> None:
    _plan(tmp_path)
    res = codex_review(tmp_path, model="gpt-5.5", dry_run=True)
    assert res.model == "gpt-5.5"
    assert "-m" in res.command and "gpt-5.5" in res.command


def test_runs_codex_and_writes_report(tmp_path: Path, monkeypatch) -> None:
    _plan(tmp_path)

    class _Out:
        stdout = "## Findings\n- low: a nit\n"

    seen: dict = {}

    def fake_run(cmd, input=None, **kw):  # noqa: A002 - mirrors subprocess.run
        seen["cmd"], seen["input"] = cmd, input
        return _Out()

    monkeypatch.setattr("flex_kit.codex_review.subprocess.run", fake_run)
    res = codex_review(tmp_path)

    assert res.report_path.exists()
    assert "Findings" in res.report_path.read_text()
    assert seen["cmd"][0] == "codex"
    assert "Plan:" in seen["input"]


def test_plan_kind_without_active_plan_errors(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        codex_review(tmp_path, kind="plan")


def test_codex_failure_surfaces_stderr(tmp_path: Path, monkeypatch) -> None:
    _plan(tmp_path)

    def fake_run(cmd, input=None, **kw):  # noqa: A002 - mirrors subprocess.run
        raise subprocess.CalledProcessError(returncode=1, cmd=cmd, stderr="not logged in to codex")

    monkeypatch.setattr("flex_kit.codex_review.subprocess.run", fake_run)
    with pytest.raises(RuntimeError, match="not logged in to codex"):  # stderr, not a bare code
        codex_review(tmp_path)
    assert not (tmp_path / "reports" / "codex-review.md").exists()  # no bogus report on failure


def test_diff_includes_tracked_and_untracked(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@t.t")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "tracked.py").write_text("x = 1\n")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-qm", "init")
    # uncommitted: modify a tracked file + add a brand-new untracked file
    (tmp_path / "tracked.py").write_text("x = 2\n")
    (tmp_path / "new_file.py").write_text("y = 99\n")

    prompt = build_prompt(tmp_path, "diff", None)

    assert "x = 2" in prompt  # tracked change (git diff HEAD = staged + unstaged)
    assert "new_file.py" in prompt and "y = 99" in prompt  # untracked new file included


def test_custom_instruction_overrides_the_lens(tmp_path: Path) -> None:
    (tmp_path / "x.py").write_text("print(1)\n")
    lens = "review the light-mode UI for DataGrip fidelity, light mode only"
    prompt = build_prompt(tmp_path, "file", "x.py", instruction=lens)
    assert lens in prompt
    assert "independent reviewer from a different model" not in prompt  # generic lead replaced


def test_default_instruction_is_back_compatible(tmp_path: Path) -> None:
    (tmp_path / "x.py").write_text("print(1)\n")
    prompt = build_prompt(tmp_path, "file", "x.py")  # no instruction
    assert "independent reviewer from a different model" in prompt  # generic lead kept


def test_diff_prompt_includes_review_input_context(tmp_path: Path) -> None:
    (tmp_path / "handoffs").mkdir()
    (tmp_path / "handoffs/review-input.md").write_text("Goal: ship the widget\n")

    prompt = build_prompt(tmp_path, "diff", None)

    assert "Goal: ship the widget" in prompt  # handoff scope fed to Codex
    assert "judge it critically" in prompt  # but still told to stay independent
