"""init scaffolds the starter source and gens host surfaces."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from flex_kit.doctor import doctor
from flex_kit.init import init
from flex_kit.main import app

_runner = CliRunner()


def test_init_scaffolds_and_gens(tmp_path: Path) -> None:
    result = init(tmp_path)

    # Source scaffolded.
    assert (tmp_path / ".flexkit/flexkit.config.json").exists()
    assert (tmp_path / ".flexkit/skills/process-navigator/SKILL.md").exists()
    assert (tmp_path / ".flexkit/skills/process-verify-fix-loop/SKILL.md").exists()
    assert (tmp_path / ".flexkit/skills/process-decision-interview/SKILL.md").exists()
    assert (tmp_path / ".flexkit/skills/process-navigator/SKILL.md").exists()
    assert (tmp_path / ".flexkit/skills/process-planning-methodology/SKILL.md").exists()
    assert (tmp_path / ".flexkit/skills/process-planning-methodology/references/red-team-personas.md").exists()
    assert (tmp_path / ".flexkit/agents/reviewer.md").exists()
    assert (tmp_path / ".flexkit/agents/implementer.md").exists()
    assert (tmp_path / ".flexkit/agents/tester.md").exists()
    assert (tmp_path / ".flexkit/agents/planner.md").exists()
    assert (tmp_path / ".flexkit/agents/debugger.md").exists()
    assert (tmp_path / ".flexkit/agents/simplifier.md").exists()
    assert (tmp_path / ".flexkit/commands/flex-implement.md").exists()
    assert (tmp_path / ".flexkit/commands/flex-change.md").exists()
    assert (tmp_path / ".flexkit/commands/flex-fix.md").exists()
    assert (tmp_path / ".flexkit/commands/flex-simplify.md").exists()
    assert (tmp_path / ".flexkit/commands/flex-docs.md").exists()

    # gen ran -> host surfaces exist (commands are flex- prefixed to avoid host built-ins).
    assert (tmp_path / ".claude/skills/process-navigator/SKILL.md").exists()
    assert (tmp_path / ".agents/skills/process-verify-fix-loop/SKILL.md").exists()
    assert (tmp_path / ".claude/commands/flex-skill-creator.md").exists()
    assert (tmp_path / ".codex/agents/reviewer.toml").exists()
    assert (tmp_path / ".claude/commands/flex-implement.md").exists()
    assert (tmp_path / ".claude/commands/flex-review.md").exists()
    assert (tmp_path / ".claude/commands/flex-codex-review.md").exists()
    g = result.gen
    assert g is not None and g.skills == 4 and g.agents == 6 and g.commands == 15

    # Freshly scaffolded project is in sync.
    findings = [f for r in doctor(tmp_path) for f in r.findings]
    assert findings == [], findings


def test_init_refuses_existing_without_force(tmp_path: Path) -> None:
    init(tmp_path)
    with pytest.raises(FileExistsError):
        init(tmp_path)
    init(tmp_path, force=True)  # force overwrites cleanly


def test_init_force_preserves_generated_record(tmp_path: Path) -> None:
    init(tmp_path)  # writes .flexkit/.generated.json
    record = tmp_path / ".flexkit/.generated.json"
    before = record.read_text()
    assert before.strip()
    init(tmp_path, force=True, run_gen=False)  # wipes .flexkit but carries the record across
    assert record.read_text() == before  # so the next gen can still prune orphaned output


def test_init_no_gen(tmp_path: Path) -> None:
    result = init(tmp_path, run_gen=False)
    assert result.gen is None
    assert (tmp_path / ".flexkit/skills/process-navigator/SKILL.md").exists()
    assert not (tmp_path / ".claude").exists()


def test_cli_init_scaffolds_source_only_by_default(tmp_path: Path) -> None:
    res = _runner.invoke(app, ["init", "--project", str(tmp_path)])
    assert res.exit_code == 0, res.output
    assert (tmp_path / ".flexkit/skills/process-navigator/SKILL.md").exists()
    assert not (tmp_path / ".claude").exists()  # gen does not run by default


def test_cli_init_gen_flag_builds_hosts(tmp_path: Path) -> None:
    res = _runner.invoke(app, ["init", "--gen", "--project", str(tmp_path)])
    assert res.exit_code == 0, res.output
    assert (tmp_path / ".claude/skills/process-navigator/SKILL.md").exists()


def test_cli_init_force_warns_before_wiping_nonempty(tmp_path: Path) -> None:
    _runner.invoke(app, ["init", "--project", str(tmp_path)])
    (tmp_path / ".flexkit/skills/mine").mkdir()  # local source the user added
    res = _runner.invoke(app, ["init", "--force", "--project", str(tmp_path)])
    assert res.exit_code == 0, res.output
    assert "deletes" in res.output  # warned about the wipe
    assert not (tmp_path / ".flexkit/skills/mine").exists()  # re-scaffolded fresh
