"""doc-targets warns on unknown inject targets and markerless target agents."""

from __future__ import annotations

from pathlib import Path

from flex_kit.agents import Agent
from flex_kit.checks import Ctx
from flex_kit.checks.doc_targets import CHECK
from flex_kit.config import Config
from flex_kit.docs import Doc


def _agent(agent_id: str, lane: str, body: str = "") -> Agent:
    return Agent(id=agent_id, body=body, frontmatter={"name": agent_id, "lane": lane})


def _doc(targets: set[str]) -> Doc:
    return Doc(rel="docs/x.md", label="x", targets=frozenset(targets))


def _ctx(agents: list[Agent], docs: list[Doc]) -> Ctx:
    return Ctx(
        project_root=Path("."),
        config=Config(),
        skills=[],
        agents=agents,
        commands=[],
        docs=docs,
        hosts={},
    )


def test_unknown_target_warns() -> None:
    agents = [_agent("reviewer", "review", "<!-- DOCS -->")]
    findings = CHECK.run(_ctx(agents, [_doc({"reviewr"})]))
    assert any(f.level == "warn" and "matches no agent or lane" in f.msg for f in findings)


def test_markerless_target_warns() -> None:
    agents = [_agent("tester", "review", "no marker in this body")]
    findings = CHECK.run(_ctx(agents, [_doc({"tester"})]))
    assert any(f.level == "warn" and "won't reach it" in f.msg for f in findings)


def test_agent_lane_and_all_targets_pass() -> None:
    agents = [_agent("reviewer", "review", "<!-- DOCS -->")]
    docs = [_doc({"reviewer"}), _doc({"review"}), _doc({"all"})]
    assert CHECK.run(_ctx(agents, docs)) == []
