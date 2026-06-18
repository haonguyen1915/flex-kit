"""Add a bundled pack's skills/agents into a project's neutral source, then gen.

A pack is just a folder of `skills/` + `agents/` under flex_kit/packs/. `add`
copies it into `.flexkit/` - the content becomes the project's own source. There
is no runtime pack machinery (no manifest merge, scoping, or hooks); a pack is
content, not a system. At real scale, packs move to their own repos and this stays
the same copy-into-source step.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from flex_kit.gen import GenResult, gen

PACKS_DIR = Path(__file__).parent / "packs"
_KINDS = ("skills", "agents")


def list_packs() -> list[str]:
    if not PACKS_DIR.exists():
        return []
    return sorted(p.name for p in PACKS_DIR.iterdir() if p.is_dir())


@dataclass
class AddResult:
    pack: str
    added: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    gen: GenResult | None = None


def add(project_root: Path, pack: str, force: bool = False, run_gen: bool = True) -> AddResult:
    src = PACKS_DIR / pack
    if not src.is_dir():
        raise FileNotFoundError(f"Unknown pack '{pack}'. Available: {', '.join(list_packs())}")
    flexkit = project_root / ".flexkit"
    if not flexkit.exists():
        raise FileNotFoundError(f"No .flexkit/ in {project_root} - run `flex-kit init` first")

    result = AddResult(pack=pack)
    for kind in _KINDS:
        src_kind = src / kind
        if not src_kind.is_dir():
            continue
        for item in sorted(src_kind.iterdir()):
            dest = flexkit / kind / item.name
            rel = f"{kind}/{item.name}"
            if dest.exists() and not force:
                result.skipped.append(rel)
                continue
            if dest.exists():
                shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(item, dest) if item.is_dir() else shutil.copyfile(item, dest)
            result.added.append(rel)

    if run_gen:
        result.gen = gen(project_root)
    return result


@dataclass
class RemoveResult:
    pack: str
    removed: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    gen: GenResult | None = None


def remove(project_root: Path, pack: str, run_gen: bool = True) -> RemoveResult:
    """Delete the items a pack provides from .flexkit/ (the symmetric un-add)."""
    src = PACKS_DIR / pack
    if not src.is_dir():
        raise FileNotFoundError(f"Unknown pack '{pack}'. Available: {', '.join(list_packs())}")
    flexkit = project_root / ".flexkit"
    if not flexkit.exists():
        raise FileNotFoundError(f"No .flexkit/ in {project_root} - run `flex-kit init` first")

    result = RemoveResult(pack=pack)
    for kind in _KINDS:
        src_kind = src / kind
        if not src_kind.is_dir():
            continue
        for item in sorted(src_kind.iterdir()):
            dest = flexkit / kind / item.name
            rel = f"{kind}/{item.name}"
            if not dest.exists():
                result.missing.append(rel)
                continue
            shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
            result.removed.append(rel)

    if run_gen:
        result.gen = gen(project_root)
    return result
