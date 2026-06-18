"""Shared emission: the OutFiles a host produces for the whole source.

Used by both `gen` (writes them) and the generated-in-sync check (compares them),
so the two can never disagree about what a host's output should be.
"""

from __future__ import annotations

from flex_kit.agents import Agent
from flex_kit.emit import OutFile
from flex_kit.skills import Skill


def emit_for_host(host, skills: list[Skill], agents: list[Agent]) -> list[OutFile]:
    out: list[OutFile] = []
    for skill in skills:
        out.extend(host.emit_skill(skill))
    if agents and hasattr(host, "emit_agent"):
        for agent in agents:
            out.extend(host.emit_agent(agent, skills))
    return out
