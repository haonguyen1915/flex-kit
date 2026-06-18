"""Integration tests: gen produces in-sync surfaces; doctor catches drift."""

from __future__ import annotations

import shutil
from pathlib import Path

from flex_kit.doctor import doctor
from flex_kit.gen import gen

FIXTURE = Path(__file__).parent / "fixtures" / "proj"


def _project(tmp_path: Path) -> Path:
    root = tmp_path / "proj"
    shutil.copytree(FIXTURE, root)
    return root


def test_gen_writes_both_hosts(tmp_path: Path) -> None:
    root = _project(tmp_path)
    result = gen(root)
    assert result.skills == 1
    assert result.hosts == ["claude", "codex"]

    claude = (root / ".claude/skills/sample-skill/SKILL.md").read_text()
    codex = (root / ".agents/skills/sample-skill/SKILL.md").read_text()

    # Claude keeps markdown + single-line description.
    assert "`code`" in claude
    assert "—" not in claude  # em-dash normalized everywhere
    # Codex strips markup and uses a block scalar.
    assert "description: >-" in codex
    assert "`code`" not in codex
    assert "<angle>" not in codex

    # References copied verbatim to both.
    assert (root / ".claude/skills/sample-skill/references/extra.md").exists()
    assert (root / ".agents/skills/sample-skill/references/extra.md").exists()


def test_doctor_clean_after_gen(tmp_path: Path) -> None:
    root = _project(tmp_path)
    gen(root)
    results = doctor(root)
    findings = [f for r in results for f in r.findings]
    assert findings == [], findings


def test_doctor_detects_handedit(tmp_path: Path) -> None:
    root = _project(tmp_path)
    gen(root)
    target = root / ".agents/skills/sample-skill/SKILL.md"
    target.write_text(target.read_text() + "\nhand-edited line\n")

    results = doctor(root)
    ids = [r.id for r in results if r.findings]
    assert "generated-in-sync" in ids


def test_doctor_detects_missing_surface(tmp_path: Path) -> None:
    root = _project(tmp_path)
    gen(root)
    shutil.rmtree(root / ".agents/skills/sample-skill")

    results = doctor(root)
    msgs = [f.msg for r in results for f in r.findings]
    assert any("missing" in m for m in msgs)
