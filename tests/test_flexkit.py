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


def test_gen_writes_skills_for_both_hosts(tmp_path: Path) -> None:
    root = _project(tmp_path)
    result = gen(root)
    assert result.skills == 1
    assert result.agents == 1
    assert result.hosts == ["claude", "codex"]

    claude = (root / ".claude/skills/sample-skill/SKILL.md").read_text()
    codex = (root / ".agents/skills/sample-skill/SKILL.md").read_text()  # Codex-native dir

    assert "`code`" in claude  # Claude keeps markdown
    assert "—" not in claude  # em-dash normalized everywhere
    assert "`code`" not in codex  # Codex strips markup
    assert "<angle>" not in codex
    assert "description: >-" not in codex  # single line, no block scalar

    # References copied verbatim to both.
    assert (root / ".claude/skills/sample-skill/references/extra.md").exists()
    assert (root / ".agents/skills/sample-skill/references/extra.md").exists()


def test_gen_writes_agents_for_both_hosts(tmp_path: Path) -> None:
    root = _project(tmp_path)
    gen(root)

    claude_agent = (root / ".claude/agents/sample-agent.md").read_text()
    codex_agent = (root / ".codex/agents/sample-agent.toml").read_text()

    # Claude agent: markdown .md, model alias passed through, skills catalog injected.
    assert "model: opus" in claude_agent
    assert "- sample-skill:" in claude_agent  # <!-- SKILLS --> replaced
    assert "<!-- SKILLS -->" not in claude_agent

    # Codex agent: TOML, model mapped, description stripped, skills catalog injected.
    assert 'model = "gpt-5.5"' in codex_agent
    assert "developer_instructions = '''" in codex_agent
    assert "- sample-skill:" in codex_agent
    assert (
        'description = "An agent that reviews things - with code and angle brackets."'
        in codex_agent
    )


def test_doctor_clean_after_gen(tmp_path: Path) -> None:
    root = _project(tmp_path)
    gen(root)
    findings = [f for r in doctor(root) for f in r.findings]
    assert findings == [], findings


def test_doctor_detects_handedit(tmp_path: Path) -> None:
    root = _project(tmp_path)
    gen(root)
    target = root / ".agents/skills/sample-skill/SKILL.md"
    target.write_text(target.read_text() + "\nhand-edited\n")
    ids = [r.id for r in doctor(root) if r.findings]
    assert "generated-in-sync" in ids


def test_doctor_detects_stray_file(tmp_path: Path) -> None:
    root = _project(tmp_path)
    gen(root)
    (root / ".agents/skills/stray-extra.md").write_text("stray\n")
    msgs = [f.msg for r in doctor(root) for f in r.findings]
    assert any("stray" in m for m in msgs)


def test_doctor_detects_missing_surface(tmp_path: Path) -> None:
    root = _project(tmp_path)
    gen(root)
    shutil.rmtree(root / ".agents/skills/sample-skill")
    msgs = [f.msg for r in doctor(root) for f in r.findings]
    assert any("missing" in m for m in msgs)
