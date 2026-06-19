"""Generate host-native surfaces (skills + agents) from the neutral source."""

from __future__ import annotations

import shutil
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from flex_kit.agents import discover_agents
from flex_kit.build import emit_for_host
from flex_kit.commands import discover_commands
from flex_kit.config import load_config
from flex_kit.docs import discover_docs
from flex_kit.registry import HOSTS
from flex_kit.skills import discover_skills


@dataclass
class GenResult:
    skills: int
    agents: int
    commands: int
    hosts: list[str]
    files_per_host: dict[str, int]


def gen(project_root: Path, dry_run: bool = False, out_root: Path | None = None) -> GenResult:
    config = load_config(project_root)
    skills = discover_skills(project_root, config.skills_dir)
    agents = discover_agents(project_root, config.agents_dir)
    commands = discover_commands(project_root, config.commands_dir)
    docs = discover_docs(project_root, config.docs_dir)
    out_root = out_root or project_root
    per_host: Counter[str] = Counter()

    for host_name in config.hosts:
        host = HOSTS.get(host_name)
        if host is None:
            raise ValueError(f'Unknown host "{host_name}" (see flex_kit/hosts/)')

        # Clean the host's owned roots so renamed/removed items don't linger.
        for attr in ("SKILLS_DIR", "AGENTS_DIR", "COMMANDS_DIR"):
            base = getattr(host, attr, None)
            if base:
                shutil.rmtree(out_root / base, ignore_errors=True)

        for f in emit_for_host(host, skills, agents, commands, docs):
            per_host[host_name] += 1
            if dry_run:
                continue
            dest = out_root / f.path
            dest.parent.mkdir(parents=True, exist_ok=True)
            if f.content is not None:
                dest.write_text(f.content, encoding="utf-8")
            else:
                assert f.copy_from is not None  # an OutFile is content or copy_from
                shutil.copyfile(f.copy_from, dest)

    return GenResult(
        skills=len(skills),
        agents=len(agents),
        commands=len(commands),
        hosts=config.hosts,
        files_per_host=dict(per_host),
    )
