"""Config resolution: defaults < global (~/.flex-kit) < project (.flexkit/)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from flex_kit.config import load_config, resolve_config
from flex_kit.main import app

_runner = CliRunner()


def _fake_editor(content: str):
    """A stand-in editor: writes `content` to the file it's told to open, then exits 0."""
    def _run(cmd, **kw):
        Path(cmd[-1]).write_text(content, encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0)
    return _run


def _write_global(data: dict) -> None:
    path = Path(os.environ["FLEXKIT_GLOBAL_CONFIG"])  # isolated per-test by conftest
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _write_project(root: Path, data: dict) -> None:
    (root / ".flexkit").mkdir(parents=True, exist_ok=True)
    (root / ".flexkit/flexkit.config.json").write_text(json.dumps(data), encoding="utf-8")


def test_defaults_when_nothing_configured(tmp_path: Path) -> None:
    cfg = resolve_config(tmp_path)  # no global, no project
    assert cfg.codex_model is None  # -> omit -m, Codex picks the latest
    assert cfg.codex_effort == "high"
    assert cfg.hosts == ["claude", "codex"]


def test_global_layer_supplies_defaults(tmp_path: Path) -> None:
    _write_global({"codexModel": "gpt-5.5", "codexEffort": "medium"})
    cfg = resolve_config(tmp_path)  # global only, no project
    assert cfg.codex_model == "gpt-5.5"
    assert cfg.codex_effort == "medium"


def test_project_overrides_global(tmp_path: Path) -> None:
    _write_global({"codexModel": "global-model", "docsDir": "global-docs"})
    _write_project(tmp_path, {"codexModel": "project-model"})
    cfg = load_config(tmp_path)
    assert cfg.codex_model == "project-model"  # project wins
    assert cfg.docs_dir == "global-docs"  # global key not overridden by project still applies


def test_load_config_requires_a_project_even_with_global(tmp_path: Path) -> None:
    _write_global({"codexModel": "gpt-5.5"})
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path)  # gen/doctor still demand a real flex-kit project


def test_resolve_config_tolerates_missing_project(tmp_path: Path) -> None:
    _write_global({"codexModel": "gpt-5.5"})
    cfg = resolve_config(tmp_path)  # no project config -> global + defaults, no raise
    assert cfg.codex_model == "gpt-5.5"


def test_config_edit_creates_and_saves_global(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("flex_kit.main.subprocess.run", _fake_editor('{"codexModel": "gpt-5.5"}\n'))
    res = _runner.invoke(app, ["config", "edit", "--global", "--editor", "fake"])
    assert res.exit_code == 0, res.output
    assert resolve_config(tmp_path).codex_model == "gpt-5.5"  # written to ~/.flex-kit, picked up


def test_config_edit_rejects_invalid_json(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("flex_kit.main.subprocess.run", _fake_editor("{ not json"))
    res = _runner.invoke(app, ["config", "edit", "--global", "--editor", "fake"])
    assert res.exit_code == 1
    assert "not valid JSON" in res.output


def test_config_show_reports_both_paths(tmp_path: Path) -> None:
    _write_global({"codexModel": "gpt-5.5"})
    res = _runner.invoke(app, ["config", "show", "--global"])
    assert res.exit_code == 0, res.output
    assert os.environ["FLEXKIT_GLOBAL_CONFIG"] in res.output  # the path is shown
    assert "gpt-5.5" in res.output  # and the content
    assert "global" in res.output and "project" in res.output  # both layers surfaced


def test_config_show_resolved_prints_merged(tmp_path: Path) -> None:
    _write_global({"codexModel": "global-model"})
    _write_project(tmp_path, {"codexModel": "project-model"})
    res = _runner.invoke(app, ["config", "show", "--resolved", "--project", str(tmp_path)])
    assert res.exit_code == 0, res.output
    assert "project-model" in res.output  # merged: project wins
