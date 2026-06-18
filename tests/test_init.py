"""init scaffolds the starter source and gens host surfaces."""

from __future__ import annotations

from pathlib import Path

import pytest

from flex_kit.doctor import doctor
from flex_kit.init import init


def test_init_scaffolds_and_gens(tmp_path: Path) -> None:
    result = init(tmp_path)

    # Source scaffolded.
    assert (tmp_path / ".flexkit/flexkit.config.json").exists()
    assert (tmp_path / ".flexkit/skills/skill-creator/SKILL.md").exists()
    assert (tmp_path / ".flexkit/skills/verify-fix-loop/SKILL.md").exists()
    assert (tmp_path / ".flexkit/skills/decision-interview/SKILL.md").exists()
    assert (tmp_path / ".flexkit/skills/navigator/SKILL.md").exists()
    assert (tmp_path / ".flexkit/skills/planning-methodology/SKILL.md").exists()
    assert (tmp_path / ".flexkit/skills/planning-methodology/references/red-team-personas.md").exists()
    assert (tmp_path / ".flexkit/agents/reviewer.md").exists()
    assert (tmp_path / ".flexkit/agents/implementer.md").exists()
    assert (tmp_path / ".flexkit/agents/tester.md").exists()
    assert (tmp_path / ".flexkit/agents/planner.md").exists()
    assert (tmp_path / ".flexkit/commands/flex-implement.md").exists()
    assert (tmp_path / ".flexkit/commands/flex-change.md").exists()
    assert (tmp_path / ".flexkit/commands/flex-fix.md").exists()

    # gen ran -> host surfaces exist (commands are flex- prefixed to avoid host built-ins).
    assert (tmp_path / ".claude/skills/skill-creator/SKILL.md").exists()
    assert (tmp_path / ".agents/skills/verify-fix-loop/SKILL.md").exists()
    assert (tmp_path / ".codex/agents/reviewer.toml").exists()
    assert (tmp_path / ".claude/commands/flex-implement.md").exists()
    assert (tmp_path / ".claude/commands/flex-review.md").exists()
    assert (tmp_path / ".claude/commands/flex-codex-review.md").exists()
    g = result.gen
    assert g is not None and g.skills == 5 and g.agents == 4 and g.commands == 9

    # Freshly scaffolded project is in sync.
    findings = [f for r in doctor(tmp_path) for f in r.findings]
    assert findings == [], findings


def test_init_refuses_existing_without_force(tmp_path: Path) -> None:
    init(tmp_path)
    with pytest.raises(FileExistsError):
        init(tmp_path)
    init(tmp_path, force=True)  # force overwrites cleanly


def test_init_no_gen(tmp_path: Path) -> None:
    result = init(tmp_path, run_gen=False)
    assert result.gen is None
    assert (tmp_path / ".flexkit/skills/skill-creator/SKILL.md").exists()
    assert not (tmp_path / ".claude").exists()
