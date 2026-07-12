"""Config resolution: defaults < global (~/.flex-kit) < project (.flexkit/), TOML files."""

from __future__ import annotations

import json
import os
import subprocess
import tomllib
from pathlib import Path

import pytest
from typer.testing import CliRunner

import flex_kit
from flex_kit.config import Config, _from_raw, dumps_toml, load_config, resolve_config
from flex_kit.main import app

_TEMPLATE = Path(flex_kit.__file__).parent / "templates/flexkit/config.toml"

_runner = CliRunner()


def _fake_editor(content: str):
    """A stand-in editor: writes `content` to the file it's told to open, then exits 0."""
    def _run(cmd, **kw):
        Path(cmd[-1]).write_text(content, encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0)
    return _run


def _write_global(data: dict) -> None:
    path = Path(os.environ["FLEXKIT_GLOBAL_CONFIG"])  # isolated per-test by conftest (.toml)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps_toml(data), encoding="utf-8")


def _write_project(root: Path, data: dict) -> None:
    (root / ".flexkit").mkdir(parents=True, exist_ok=True)
    (root / ".flexkit/config.toml").write_text(dumps_toml(data), encoding="utf-8")


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
    monkeypatch.setattr("flex_kit.main.subprocess.run", _fake_editor('codexModel = "gpt-5.5"\n'))
    res = _runner.invoke(app, ["config", "edit", "--global", "--editor", "fake"])
    assert res.exit_code == 0, res.output
    assert resolve_config(tmp_path).codex_model == "gpt-5.5"  # written to ~/.flex-kit, picked up


def test_config_edit_rejects_invalid_toml(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("flex_kit.main.subprocess.run", _fake_editor("= not toml"))
    res = _runner.invoke(app, ["config", "edit", "--global", "--editor", "fake"])
    assert res.exit_code == 1
    assert "not valid TOML" in res.output


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
    assert "codexModel" in res.output and "codex_model" not in res.output  # file keys, not internal


def test_project_template_parses_to_config_defaults() -> None:
    # The scaffolded template must encode exactly the defaults - no silent drift from Config.
    raw = tomllib.loads(_TEMPLATE.read_text(encoding="utf-8"))
    assert _from_raw(raw) == Config()  # codexModel is commented out -> absent -> None default


def test_config_edit_seeds_documented_skeleton(tmp_path: Path, monkeypatch) -> None:
    # A no-op editor: the file keeps whatever `config edit` seeded.
    monkeypatch.setattr(
        "flex_kit.main.subprocess.run", lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0)
    )
    res = _runner.invoke(app, ["config", "edit", "--global", "--editor", "true"])
    assert res.exit_code == 0, res.output
    text = Path(os.environ["FLEXKIT_GLOBAL_CONFIG"]).read_text(encoding="utf-8")
    tomllib.loads(text)  # valid TOML
    assert "codexModel" in text and "codexEffort" in text  # documented (commented or set)
    assert "skillsDir" not in text  # project-only keys omitted from the global skeleton
    assert "#" in text  # it carries comments (the whole point of TOML)


def test_legacy_json_config_is_still_read(tmp_path: Path) -> None:
    # Pre-migration projects keep working: a .json config is read when no .toml is present.
    (tmp_path / ".flexkit").mkdir(parents=True)
    (tmp_path / ".flexkit/flexkit.config.json").write_text(
        json.dumps({"codexModel": "legacy-model"}), encoding="utf-8"
    )
    assert resolve_config(tmp_path).codex_model == "legacy-model"
    assert load_config(tmp_path).codex_model == "legacy-model"  # load_config finds legacy too


def test_toml_preferred_over_legacy_json(tmp_path: Path) -> None:
    (tmp_path / ".flexkit").mkdir(parents=True)
    (tmp_path / ".flexkit/config.json").write_text('{"codexModel": "json"}', encoding="utf-8")
    (tmp_path / ".flexkit/config.toml").write_text('codexModel = "toml"\n', encoding="utf-8")
    assert resolve_config(tmp_path).codex_model == "toml"  # .toml wins over a stray .json
