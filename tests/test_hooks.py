"""Hook logic (session-start orientation, pre-tool guard) + settings.json wiring."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from flex_kit import hooks
from flex_kit import plan as plan_mod
from flex_kit.doctor import doctor
from flex_kit.gen import gen

FIXTURE = Path(__file__).parent / "fixtures" / "proj"


def test_session_start_no_plan(tmp_path: Path) -> None:
    assert "no active plan" in hooks.session_start(tmp_path)


def test_session_start_reports_active_plan(tmp_path: Path) -> None:
    p = plan_mod.create_plan(tmp_path, "Add Auth", now=datetime(2026, 6, 18, 9, 0))
    md = p.dir / "plan.md"
    md.write_text(md.read_text().replace("- [ ] first step", "- [x] one\n- [ ] two"))
    line = hooks.session_start(tmp_path)
    assert p.id in line
    assert "1/2 steps" in line
    assert "next: two" in line


def test_user_prompt_reminds_then_dedupes(tmp_path: Path) -> None:
    p = plan_mod.create_plan(tmp_path, "task", now=datetime(2026, 6, 18, 9, 0))
    first = hooks.user_prompt(tmp_path)
    assert first is not None and "flex-kit plan:" in first
    assert hooks.user_prompt(tmp_path) is None  # unchanged -> deduped

    md = p.dir / "plan.md"
    md.write_text(md.read_text().replace("- [ ] first step", "- [x] done\n- [ ] more"))
    assert hooks.user_prompt(tmp_path) is not None  # advanced -> fires again


def test_user_prompt_silent_without_plan(tmp_path: Path) -> None:
    assert hooks.user_prompt(tmp_path) is None


def test_pre_tool_blocks_secret_path() -> None:
    reason = hooks.pre_tool_decision({"tool_input": {"file_path": "config/.env.production"}})
    assert reason is not None and "secret" in reason


def test_pre_tool_allows_normal_path() -> None:
    assert hooks.pre_tool_decision({"tool_input": {"file_path": "src/main.py"}}) is None


def test_gen_wires_hooks_into_settings(tmp_path: Path) -> None:
    root = tmp_path / "proj"
    shutil.copytree(FIXTURE, root)
    gen(root)

    settings = json.loads((root / ".claude/settings.json").read_text())
    events = settings["hooks"]
    assert {"SessionStart", "UserPromptSubmit", "PreToolUse"} <= set(events)
    assert "compact" in events["SessionStart"][0]["matcher"]  # survives compaction
    cmd = events["SessionStart"][0]["hooks"][0]["command"]
    assert cmd == "flex-kit hook session-start"

    # Codex gets no settings.json.
    assert not (root / ".codex/settings.json").exists()

    findings = [f for r in doctor(root) for f in r.findings]
    assert findings == [], findings
