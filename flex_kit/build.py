"""Shared emission: the OutFiles a host produces for the whole source.

Used by both `gen` (writes them) and the generated-in-sync check (compares them),
so the two can never disagree about what a host's output should be. A host emits
only the capability kinds it supports (e.g. only the Claude host emits commands).
"""

from __future__ import annotations

from flex_kit.agents import Agent
from flex_kit.commands import Command
from flex_kit.docs import Doc
from flex_kit.emit import OutFile
from flex_kit.skills import Skill


def emit_for_host(
    host,
    skills: list[Skill],
    agents: list[Agent],
    commands: list[Command],
    docs: list[Doc],
) -> list[OutFile]:
    out: list[OutFile] = []
    for skill in skills:
        out.extend(host.emit_skill(skill))
    if agents and hasattr(host, "emit_agent"):
        for agent in agents:
            out.extend(host.emit_agent(agent, skills, docs))
    if commands and hasattr(host, "emit_command"):
        for command in commands:
            out.extend(host.emit_command(command, skills, docs))
    if hasattr(host, "emit_global"):
        out.extend(host.emit_global())
    return out
