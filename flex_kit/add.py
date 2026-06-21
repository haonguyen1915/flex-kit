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


def _pack_rels(pack: str) -> list[str]:
    """The .flexkit-relative paths a pack provides (skills/<id>, agents/<id>.md)."""
    src = PACKS_DIR / pack
    rels: list[str] = []
    for kind in _KINDS:
        src_kind = src / kind
        if src_kind.is_dir():
            rels += [f"{kind}/{item.name}" for item in src_kind.iterdir()]
    return rels


def installed_packs(project_root: Path) -> set[str]:
    """Packs whose every item already exists in .flexkit/ (so a re-add is a no-op)."""
    flexkit = project_root / ".flexkit"
    if not flexkit.is_dir():
        return set()
    out: set[str] = set()
    for pack in list_packs():
        rels = _pack_rels(pack)
        if rels and all((flexkit / rel).exists() for rel in rels):
            out.add(pack)
    return out


@dataclass
class AddResult:
    pack: str
    added: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    gen: GenResult | None = None


def _require_flexkit(project_root: Path) -> None:
    if not (project_root / ".flexkit").exists():
        raise FileNotFoundError(f"No .flexkit/ in {project_root} - run `flex-kit init` first")


def _copy_pack(project_root: Path, pack: str, force: bool) -> tuple[list[str], list[str]]:
    """Copy one pack's items into .flexkit/ (no gen). Returns (added, skipped) rel paths."""
    src = PACKS_DIR / pack
    if not src.is_dir():
        raise FileNotFoundError(f"Unknown pack '{pack}'. Available: {', '.join(list_packs())}")
    flexkit = project_root / ".flexkit"
    added: list[str] = []
    skipped: list[str] = []
    for kind in _KINDS:
        src_kind = src / kind
        if not src_kind.is_dir():
            continue
        for item in sorted(src_kind.iterdir()):
            dest = flexkit / kind / item.name
            rel = f"{kind}/{item.name}"
            if dest.exists() and not force:
                skipped.append(rel)
                continue
            if dest.exists():
                shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(item, dest) if item.is_dir() else shutil.copyfile(item, dest)
            added.append(rel)
    return added, skipped


def add(project_root: Path, pack: str, force: bool = False, run_gen: bool = True) -> AddResult:
    _require_flexkit(project_root)
    added, skipped = _copy_pack(project_root, pack, force)
    result = AddResult(pack=pack, added=added, skipped=skipped)
    if run_gen:
        result.gen = gen(project_root)
    return result


def add_packs(
    project_root: Path,
    packs: list[str],
    force: bool = False,
    run_gen: bool = True,
    label: str | None = None,
) -> AddResult:
    """Add several packs in one shot, then gen once (not once per pack)."""
    _require_flexkit(project_root)
    result = AddResult(pack=label or ", ".join(packs))
    for pack in packs:
        added, skipped = _copy_pack(project_root, pack, force)
        result.added.extend(added)
        result.skipped.extend(skipped)
    if run_gen:
        result.gen = gen(project_root)
    return result


def add_all(project_root: Path, force: bool = False, run_gen: bool = True) -> AddResult:
    """Add every bundled pack, then gen once (not once per pack)."""
    return add_packs(project_root, list_packs(), force, run_gen, label="--all")


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
