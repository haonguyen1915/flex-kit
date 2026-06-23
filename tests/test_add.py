"""add copies a bundled pack into .flexkit/ and regenerates host surfaces."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from flex_kit.add import _pack_items, add, add_all, add_packs, installed_packs, list_packs
from flex_kit.doctor import doctor
from flex_kit.init import init
from flex_kit.main import app

_runner = CliRunner()


def test_grouped_pack_skills_flatten_on_add(tmp_path: Path, monkeypatch) -> None:
    # A bundled pack whose skills sit in a group folder (skills/<group>/<id>/SKILL.md).
    sk = tmp_path / "packs" / "demo" / "skills" / "style" / "demo-naming"
    sk.mkdir(parents=True)
    sk.joinpath("SKILL.md").write_text(
        "---\nname: demo-naming\n"
        "description: a demo skill for the flatten test\n---\n\n# Demo\n"
    )
    monkeypatch.setattr("flex_kit.add.PACKS_DIR", tmp_path / "packs")

    # _pack_items flattens the group out of the dest path.
    assert [rel for rel, _ in _pack_items("demo")] == ["skills/demo-naming"]

    proj = tmp_path / "proj"
    init(proj, run_gen=False)
    add(proj, "demo", run_gen=False)
    assert (proj / ".flexkit/skills/demo-naming/SKILL.md").exists()  # flattened
    assert not (proj / ".flexkit/skills/style").exists()  # group folder dropped


def test_backend_pack_is_bundled() -> None:
    assert "backend" in list_packs()


def test_category_nested_pack_is_discovered_by_flat_name(tmp_path: Path, monkeypatch) -> None:
    # A pack grouped under a category folder (packs/<category>/<pack>) is found and added
    # by its flat leaf name - the category is repo organization only.
    sk = tmp_path / "packs" / "frameworks" / "demo-fw" / "skills" / "demo-fw-routing"
    sk.mkdir(parents=True)
    sk.joinpath("SKILL.md").write_text(
        "---\nname: demo-fw-routing\n"
        "description: a demo framework skill under a category folder\n---\n\n# Demo\n"
    )
    monkeypatch.setattr("flex_kit.add.PACKS_DIR", tmp_path / "packs")

    assert "demo-fw" in list_packs()  # flat name, not "frameworks/demo-fw"
    assert [rel for rel, _ in _pack_items("demo-fw")] == ["skills/demo-fw-routing"]

    proj = tmp_path / "proj"
    init(proj, run_gen=False)
    add(proj, "demo-fw", run_gen=False)
    assert (proj / ".flexkit/skills/demo-fw-routing/SKILL.md").exists()


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
