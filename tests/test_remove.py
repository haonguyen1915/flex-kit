"""remove un-adds a pack from .flexkit/ and regenerates host surfaces."""

from __future__ import annotations

from pathlib import Path

import pytest

from flex_kit.add import add, remove
from flex_kit.doctor import doctor
from flex_kit.init import init


def test_remove_undoes_add(tmp_path: Path) -> None:
    init(tmp_path)
    add(tmp_path, "api-design")
    assert (tmp_path / ".flexkit/skills/api-design-pattern").exists()

    result = remove(tmp_path, "api-design")
    assert "skills/api-design-pattern" in result.removed
    assert not (tmp_path / ".flexkit/skills/api-design-pattern").exists()
    # Regenerated: the host surfaces are gone too.
    assert not (tmp_path / ".claude/skills/api-design-pattern").exists()
    assert not (tmp_path / ".agents/skills/api-design-pattern").exists()

    findings = [f for r in doctor(tmp_path) for f in r.findings]
    assert findings == [], findings


def test_remove_reports_missing_when_not_added(tmp_path: Path) -> None:
    init(tmp_path)
    result = remove(tmp_path, "api-design")
    assert "skills/api-design-pattern" in result.missing
    assert result.removed == []


def test_remove_unknown_pack_errors(tmp_path: Path) -> None:
    init(tmp_path)
    with pytest.raises(FileNotFoundError):
        remove(tmp_path, "does-not-exist")
