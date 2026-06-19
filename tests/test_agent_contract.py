"""The agent-contract check warns on missing `model`/`lane` and an unknown lane."""

from __future__ import annotations

from pathlib import Path

from flex_kit.agents import Agent
from flex_kit.checks import Ctx
from flex_kit.checks.agent_contract import CHECK
from flex_kit.config import Config


def _agent(agent_id: str, **fm: str) -> Agent:
    return Agent(id=agent_id, body="", frontmatter=fm)


def _ctx(*agents: Agent) -> Ctx:
    return Ctx(
        project_root=Path("."),
        config=Config(),
        skills=[],
        agents=list(agents),
        commands=[],
        docs=[],
        hosts={},
    )


def test_missing_model_warns() -> None:
    findings = CHECK.run(_ctx(_agent("a", lane="build")))
    assert any(f.level == "warn" and "`model`" in f.msg for f in findings)


def test_missing_lane_warns() -> None:
    findings = CHECK.run(_ctx(_agent("a", model="opus")))
    assert any(f.level == "warn" and "`lane`" in f.msg for f in findings)


def test_unknown_lane_warns() -> None:
    findings = CHECK.run(_ctx(_agent("a", model="opus", lane="frontend")))
    assert any(f.level == "warn" and "lane 'frontend'" in f.msg for f in findings)


def test_good_agent_passes() -> None:
    findings = CHECK.run(_ctx(_agent("a", model="opus", lane="review")))
    assert findings == []
