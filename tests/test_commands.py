"""Commands generate to the Claude host only; Codex does not emit them."""

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


def test_command_generates_for_claude_only(tmp_path: Path) -> None:
    root = _project(tmp_path)
    result = gen(root)
    assert result.commands == 1

    cmd = root / ".claude/commands/sample-command.md"
    assert cmd.exists()
    text = cmd.read_text()
    assert "argument-hint: [task]" in text
    assert "name:" not in text.split("---")[1]  # name dropped (filename is the command)
    assert "`sample-skill`" in text  # <!-- SKILLS --> injected (compact name list)
    assert "<!-- SKILLS -->" not in text

    # Codex has no command surface.
    assert not (root / ".codex/commands").exists()
    assert not (root / ".agents/commands").exists()


def test_doctor_clean_with_command(tmp_path: Path) -> None:
    root = _project(tmp_path)
    gen(root)
    findings = [f for r in doctor(root) for f in r.findings]
    assert findings == [], findings
