"""Cross-model codex review - mocked so tests never call the real codex CLI."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from flex_kit import plan as plan_mod
from flex_kit.codex_review import build_prompt, codex_review


def _plan(tmp_path: Path) -> None:
    plan_mod.create_plan(tmp_path, "task", now=datetime(2026, 6, 18, 9, 0))


def test_build_prompt_file(tmp_path: Path) -> None:
    (tmp_path / "x.py").write_text("print(1)\n")
    prompt = build_prompt(tmp_path, "file", "x.py")
    assert "print(1)" in prompt and "independent reviewer" in prompt


def test_dry_run_builds_codex_command(tmp_path: Path) -> None:
    _plan(tmp_path)
    res = codex_review(tmp_path, dry_run=True)
    assert res.command[:2] == ["codex", "exec"]
    assert res.model == "gpt-5.5"
    assert not res.report_path.exists()  # dry-run writes nothing


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
