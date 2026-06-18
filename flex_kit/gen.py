"""Generate host-native skill surfaces from the neutral source."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from flex_kit.config import load_config
from flex_kit.registry import HOSTS
from flex_kit.render import render_skill_content
from flex_kit.skills import discover_skills


@dataclass
class Written:
    host: str
    id: str
    dir: Path
    count: int


@dataclass
class GenResult:
    skills: int
    hosts: list[str]
    written: list[Written]


def gen(project_root: Path, dry_run: bool = False, out_root: Path | None = None) -> GenResult:
    config = load_config(project_root)
    skills = discover_skills(project_root, config.skills_dir)
    out_root = out_root or project_root
    written: list[Written] = []

    for host_name in config.hosts:
        host = HOSTS.get(host_name)
        if host is None:
            raise ValueError(f'Unknown host "{host_name}" (see flex_kit/hosts/)')

        for skill in skills:
            dest_dir = out_root / host.BASE_DIR / skill.id
            count = 1 + len(skill.references)
            if not dry_run:
                shutil.rmtree(dest_dir, ignore_errors=True)
                dest_dir.mkdir(parents=True, exist_ok=True)
                (dest_dir / "SKILL.md").write_text(
                    render_skill_content(host, skill), encoding="utf-8"
                )
                for rel in skill.references:
                    dest = dest_dir / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(skill.dir / rel, dest)
            written.append(Written(host_name, skill.id, dest_dir, count))

    return GenResult(skills=len(skills), hosts=config.hosts, written=written)
