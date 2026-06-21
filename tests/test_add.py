"""add copies a bundled pack into .flexkit/ and regenerates host surfaces."""

from __future__ import annotations

from pathlib import Path

import pytest

from flex_kit.add import add, add_all, list_packs
from flex_kit.doctor import doctor
from flex_kit.init import init


def test_backend_pack_is_bundled() -> None:
    assert "backend" in list_packs()


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
