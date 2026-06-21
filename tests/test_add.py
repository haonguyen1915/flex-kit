"""add copies a bundled pack into .flexkit/ and regenerates host surfaces."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from flex_kit.add import add, add_all, add_packs, installed_packs, list_packs
from flex_kit.doctor import doctor
from flex_kit.init import init
from flex_kit.main import app

_runner = CliRunner()


def test_backend_pack_is_bundled() -> None:
    assert "backend" in list_packs()


def test_cli_add_copies_source_only_by_default(tmp_path: Path) -> None:
    init(tmp_path)
    res = _runner.invoke(app, ["add", "backend", "--project", str(tmp_path)])
    assert res.exit_code == 0, res.output
    assert (tmp_path / ".flexkit/skills/backend-restful-api/SKILL.md").exists()
    assert not (tmp_path / ".claude/skills/backend-restful-api").exists()  # no gen by default


def test_cli_add_gen_flag_builds_hosts(tmp_path: Path) -> None:
    init(tmp_path)
    res = _runner.invoke(app, ["add", "backend", "--gen", "--project", str(tmp_path)])
    assert res.exit_code == 0, res.output
    assert (tmp_path / ".claude/skills/backend-restful-api/SKILL.md").exists()


def test_add_packs_adds_multiple_and_gens_once(tmp_path: Path) -> None:
    init(tmp_path)
    result = add_packs(tmp_path, ["backend", "python"])

    assert "skills/backend-restful-api" in result.added
    assert any(rel.startswith("skills/python-") for rel in result.added)
    assert (tmp_path / ".flexkit/skills/backend-restful-api/SKILL.md").exists()
    assert (tmp_path / ".flexkit/skills/python-naming/SKILL.md").exists()
    assert result.gen is not None  # gen ran exactly once for the whole selection

    findings = [f for r in doctor(tmp_path) for f in r.findings]
    assert findings == [], findings


def test_installed_packs_reflects_what_was_added(tmp_path: Path) -> None:
    init(tmp_path)
    assert installed_packs(tmp_path) == set()
    add(tmp_path, "backend")
    assert "backend" in installed_packs(tmp_path)
    assert "python" not in installed_packs(tmp_path)


def test_add_pack_into_project(tmp_path: Path) -> None:
    init(tmp_path)
    result = add(tmp_path, "backend")

    assert "skills/backend-restful-api" in result.added
    assert (tmp_path / ".flexkit/skills/backend-restful-api/SKILL.md").exists()
    # Regenerated onto both hosts.
    assert (tmp_path / ".claude/skills/backend-restful-api/SKILL.md").exists()
    assert (tmp_path / ".agents/skills/backend-restful-api/SKILL.md").exists()

    findings = [f for r in doctor(tmp_path) for f in r.findings]
    assert findings == [], findings


def test_add_all_adds_every_pack_and_gens_once(tmp_path: Path) -> None:
    init(tmp_path)
    result = add_all(tmp_path)

    for pack in list_packs():
        assert any(rel for rel in result.added), result
    assert "skills/backend-restful-api" in result.added
    assert (tmp_path / ".flexkit/skills/backend-restful-api/SKILL.md").exists()
    assert result.gen is not None  # gen ran exactly once at the end

    findings = [f for r in doctor(tmp_path) for f in r.findings]
    assert findings == [], findings


def test_add_all_requires_init(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        add_all(tmp_path)


def test_add_unknown_pack_errors(tmp_path: Path) -> None:
    init(tmp_path)
    with pytest.raises(FileNotFoundError):
        add(tmp_path, "does-not-exist")


def test_add_requires_init(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        add(tmp_path, "backend")


def test_add_skips_existing_without_force(tmp_path: Path) -> None:
    init(tmp_path)
    add(tmp_path, "backend")
    again = add(tmp_path, "backend")
    assert "skills/backend-restful-api" in again.skipped
    assert again.added == []
