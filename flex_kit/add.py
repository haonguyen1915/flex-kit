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


def _is_pack(d: Path) -> bool:
    """A pack is a dir that provides content (a skills/ or agents/ subdir)."""
    return (d / "skills").is_dir() or (d / "agents").is_dir()


def _pack_dirs() -> list[Path]:
    """Every pack dir, found one **category** level deep (`packs/<category>/<pack>`).

    Packs are grouped by axis for repo tidiness (`languages/`, `frameworks/`,
    `disciplines/`); the category is organization only - the add unit stays the leaf pack
    and its name is flat (`add fastapi`). A pack placed directly under packs/ (no category)
    still works, so the grouping is optional."""
    if not PACKS_DIR.is_dir():
        return []
    out: list[Path] = []
    for top in sorted(PACKS_DIR.iterdir()):
        if not top.is_dir():
            continue
        if _is_pack(top):
            out.append(top)  # flat pack, no category
        else:
            out.extend(c for c in sorted(top.iterdir()) if c.is_dir() and _is_pack(c))
    return out


def _pack_dir(pack: str) -> Path | None:
    """Resolve a flat pack name to its dir, wherever its category sits."""
    for d in _pack_dirs():
        if d.name == pack:
            return d
    return None


def list_packs() -> list[str]:
    return sorted(d.name for d in _pack_dirs())


def _pack_items(pack: str) -> list[tuple[str, Path]]:
    """(.flexkit-relative dest, source path) for each item a pack provides.

    Skills may be organized into group subfolders in the bundled pack for tidiness
    (`skills/<group>/<id>/SKILL.md`); they are **flattened** here to `skills/<id>` so the
    project source and host output stay one level deep (Claude Code only discovers
    one-level skills). Agents are flat files.
    """
    src = _pack_dir(pack)
    if src is None:
        return []
    items: list[tuple[str, Path]] = []
    skills_dir = src / "skills"
    if skills_dir.is_dir():
        for skill_md in sorted(skills_dir.rglob("SKILL.md")):
            skill_dir = skill_md.parent
            items.append((f"skills/{skill_dir.name}", skill_dir))
    agents_dir = src / "agents"
    if agents_dir.is_dir():
        for item in sorted(agents_dir.iterdir()):
            items.append((f"agents/{item.name}", item))
    return items


def _pack_rels(pack: str) -> list[str]:
    """The .flexkit-relative paths a pack provides (skills/<id>, agents/<id>.md)."""
    return [rel for rel, _ in _pack_items(pack)]


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
    if _pack_dir(pack) is None:
        raise FileNotFoundError(f"Unknown pack '{pack}'. Available: {', '.join(list_packs())}")
    flexkit = project_root / ".flexkit"
    added: list[str] = []
    skipped: list[str] = []
    for rel, item in _pack_items(pack):
        dest = flexkit / rel
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
    if _pack_dir(pack) is None:
        raise FileNotFoundError(f"Unknown pack '{pack}'. Available: {', '.join(list_packs())}")
    flexkit = project_root / ".flexkit"
    if not flexkit.exists():
        raise FileNotFoundError(f"No .flexkit/ in {project_root} - run `flex-kit init` first")

    result = RemoveResult(pack=pack)
    for rel, _item in _pack_items(pack):
        dest = flexkit / rel
        if not dest.exists():
            result.missing.append(rel)
            continue
        shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
        result.removed.append(rel)

    if run_gen:
        result.gen = gen(project_root)
    return result
