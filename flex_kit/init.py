"""Scaffold a project's neutral source from the bundled starter template, then gen.

Unlike prep-kit (which ships pre-generated host dirs in its bundle), flex-kit's
template carries ONLY the source `.flexkit/`. `init` copies that source; `gen`
produces the host surfaces - so there is no copy-then-overwrite redundancy.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from flex_kit.gen import GenResult, gen
from flex_kit.record import read_record, write_record

TEMPLATE_DIR = Path(__file__).parent / "templates" / "flexkit"


_BASE_KINDS = ("skills", "agents", "commands")


@dataclass
class InitResult:
    flexkit_dir: Path
    gen: GenResult | None


@dataclass
class UpdateResult:
    updated: list[str]
    gen: GenResult | None


def update(project_root: Path, run_gen: bool = False) -> UpdateResult:
    """Refresh the flex-kit BASE items (the template's agents/skills/commands) in an
    existing .flexkit/ to the installed version's prompts, overwriting them. Anything not
    shipped in the base template - added packs, your own skills/agents - is left entirely
    untouched. Items the new version dropped are not removed (only add/overwrite), and
    flexkit.config.json is never touched.
    """
    dest = project_root / ".flexkit"
    if not dest.exists():
        raise FileNotFoundError(f"No .flexkit/ in {project_root} - run `flex-kit init` first")
    updated: list[str] = []
    for kind in _BASE_KINDS:
        src_kind = TEMPLATE_DIR / kind
        if not src_kind.is_dir():
            continue
        for item in sorted(src_kind.iterdir()):
            target = dest / kind / item.name
            if target.exists():
                shutil.rmtree(target) if target.is_dir() else target.unlink()
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(item, target) if item.is_dir() else shutil.copyfile(item, target)
            updated.append(f"{kind}/{item.name}")
    result = gen(project_root) if run_gen else None
    return UpdateResult(updated=updated, gen=result)


def init(project_root: Path, force: bool = False, run_gen: bool = True) -> InitResult:
    dest = project_root / ".flexkit"
    preserved: set[str] = set()
    if dest.exists():
        if not force:
            raise FileExistsError(
                f".flexkit already exists in {project_root} (use --force to overwrite)"
            )
        # Carry the gen record across the wipe: .generated.json lives in .flexkit/, so a
        # naive rmtree would lose it and orphan every host file this project produced. The
        # next gen needs it to prune that now-sourceless output.
        preserved = read_record(project_root)
        shutil.rmtree(dest)
    shutil.copytree(TEMPLATE_DIR, dest)
    if preserved:
        write_record(project_root, preserved)
    result = gen(project_root) if run_gen else None
    return InitResult(flexkit_dir=dest, gen=result)
