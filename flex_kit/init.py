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


@dataclass
class InitResult:
    flexkit_dir: Path
    gen: GenResult | None


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
