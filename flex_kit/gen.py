"""Generate host-native surfaces (skills + agents) from the neutral source."""

from __future__ import annotations

import shutil
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from flex_kit.agents import discover_agents
from flex_kit.build import emit_for_host
from flex_kit.catalog import owned_agent_ids, owned_command_ids, owned_skill_ids
from flex_kit.commands import discover_commands
from flex_kit.config import load_config
from flex_kit.docs import discover_docs
from flex_kit.emit import OutFile
from flex_kit.record import read_record, write_record
from flex_kit.registry import HOSTS
from flex_kit.skills import discover_skills


@dataclass
class GenResult:
    skills: int
    agents: int
    commands: int
    hosts: list[str]
    files_per_host: dict[str, int]


def _prune_empty_dirs(out_root: Path, removed: set[str]) -> None:
    """Remove now-empty directories left behind by deleted orphans, up to out_root."""
    for rel in removed:
        d = (out_root / rel).parent
        while d != out_root and d.is_dir() and not any(d.iterdir()):
            d.rmdir()
            d = d.parent


def _catalog_orphans(
    out_root: Path,
    host_mods: list,
    src_skills: set[str],
    src_agents: set[str],
    src_commands: set[str],
) -> set[str]:
    """Host output for a flex-kit-owned id that is no longer in source - found by the
    bundled catalog, so gen cleans it even when the `.generated.json` record was lost.
    Foreign (hand-authored) ids are not in the catalog and so are left untouched."""
    owned_sk, owned_ag, owned_cmd = owned_skill_ids(), owned_agent_ids(), owned_command_ids()
    orphans: set[str] = set()
    for host in host_mods:
        # Skills: <SKILLS_DIR>/<id>/... (a directory per skill).
        sdir = getattr(host, "SKILLS_DIR", None)
        if sdir and (root := out_root / sdir).is_dir():
            for entry in root.iterdir():
                if entry.is_dir() and entry.name in owned_sk and entry.name not in src_skills:
                    orphans |= {
                        f.relative_to(out_root).as_posix() for f in entry.rglob("*") if f.is_file()
                    }
        # Agents / commands: <DIR>/<id>.<ext> (a file per item, id = stem).
        for attr, owned, src in (
            ("AGENTS_DIR", owned_ag, src_agents),
            ("COMMANDS_DIR", owned_cmd, src_commands),
        ):
            d = getattr(host, attr, None)
            if d and (root := out_root / d).is_dir():
                for entry in root.iterdir():
                    if entry.is_file() and entry.stem in owned and entry.stem not in src:
                        orphans.add(entry.relative_to(out_root).as_posix())
    return orphans


def gen(project_root: Path, dry_run: bool = False, out_root: Path | None = None) -> GenResult:
    config = load_config(project_root)
    skills = discover_skills(project_root, config.skills_dir)
    agents = discover_agents(project_root, config.agents_dir)
    commands = discover_commands(project_root, config.commands_dir)
    docs = discover_docs(project_root, config.docs_dir)
    out_root = out_root or project_root
    per_host: Counter[str] = Counter()

    files: list[OutFile] = []
    for host_name in config.hosts:
        host = HOSTS.get(host_name)
        if host is None:
            raise ValueError(f'Unknown host "{host_name}" (see flex_kit/hosts/)')
        host_files = emit_for_host(host, skills, agents, commands, docs)
        per_host[host_name] += len(host_files)
        files.extend(host_files)

    if not dry_run:
        new_paths = {f.path for f in files}
        # Orphans = output we no longer produce, from two sources: (1) the persisted
        # record of last run, and (2) the bundled catalog (output whose id flex-kit owns
        # but source dropped) - the catalog net self-heals even when the record was lost.
        # Files we never generated - hand-authored, other tools - are in neither, so stay.
        active_hosts = [HOSTS[h] for h in config.hosts if h in HOSTS]
        catalog = _catalog_orphans(
            out_root,
            active_hosts,
            {s.id for s in skills},
            {a.id for a in agents},
            {c.id for c in commands},
        )
        orphans = (read_record(out_root) | catalog) - new_paths
        for rel in orphans:
            dest = out_root / rel
            if dest.is_file():
                dest.unlink()
        _prune_empty_dirs(out_root, orphans)

        for f in files:
            dest = out_root / f.path
            dest.parent.mkdir(parents=True, exist_ok=True)
            if f.content is not None:
                dest.write_text(f.content, encoding="utf-8")
            else:
                assert f.copy_from is not None  # an OutFile is content or copy_from
                shutil.copyfile(f.copy_from, dest)

        write_record(out_root, new_paths)

    return GenResult(
        skills=len(skills),
        agents=len(agents),
        commands=len(commands),
        hosts=config.hosts,
        files_per_host=dict(per_host),
    )
