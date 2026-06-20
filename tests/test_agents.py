"""The agent roster catalog (id, lane, `[docs]` flag) injects at <!-- AGENTS -->."""

from __future__ import annotations

from flex_kit.agents import Agent, agent_catalog, inject_agents


def _agent(agent_id: str, lane: str, body: str = "") -> Agent:
    desc = f"{agent_id} does things - and more"
    return Agent(id=agent_id, body=body, frontmatter={"name": agent_id, "lane": lane, "description": desc})


def test_catalog_shows_lane_and_docs_flag() -> None:
    agents = [
        _agent("reviewer", "review", "## Project Docs\n<!-- DOCS -->\n"),
        _agent("debugger", "review", "no docs marker here"),
    ]
    cat = agent_catalog(agents)
    assert "- reviewer (review) [docs]: reviewer does things" in cat
    assert "- debugger (review): debugger does things" in cat  # no [docs] -> not a target


def test_inject_agents_marker_is_line_level() -> None:
    agents = [_agent("reviewer", "review", "<!-- DOCS -->")]
    assert inject_agents("no marker", agents) == "no marker"
    assert "- reviewer (review) [docs]" in inject_agents("a\n<!-- AGENTS -->\nb", agents)
    # an inline mention in prose is left untouched
    prose = "document the `<!-- AGENTS -->` marker"
    assert inject_agents(prose, agents) == prose
