"""gen preserves unmanaged host files and cleans only its own orphans."""

from __future__ import annotations

import shutil
from pathlib import Path

from flex_kit.doctor import doctor
from flex_kit.gen import gen
from flex_kit.init import init


def test_gen_preserves_unmanaged_files(tmp_path: Path) -> None:
    init(tmp_path)
    handmade = tmp_path / ".claude/skills/handmade/SKILL.md"
    handmade.parent.mkdir(parents=True, exist_ok=True)
    handmade.write_text("# mine\n")

    gen(tmp_path)  # re-gen must not wipe what it did not generate

    assert handmade.read_text() == "# mine\n"
    assert (tmp_path / ".claude/agents/planner.md").exists()  # flex-kit output still there


def test_gen_cleans_orphan_on_source_removal(tmp_path: Path) -> None:
    init(tmp_path)
    orphan = tmp_path / ".claude/skills/process-navigator/SKILL.md"
    assert orphan.exists()

    shutil.rmtree(tmp_path / ".flexkit/skills/process-navigator")  # remove the source
    gen(tmp_path)

    assert not orphan.exists()  # generated output cleaned
    assert not (tmp_path / ".claude/skills/process-navigator").exists()  # empty dir pruned
    assert [f for r in doctor(tmp_path) for f in r.findings] == []


def test_gen_catalog_net_cleans_unrecorded_pack_orphan(tmp_path: Path) -> None:
    init(tmp_path)  # base gen + a record that knows only the process-* base skills
    # A pack-skill output with NO record entry - as if the record had been lost/wiped.
    orphan = tmp_path / ".claude/skills/python-naming/SKILL.md"
    orphan.parent.mkdir(parents=True)
    orphan.write_text("stale\n")
    # A genuinely hand-authored skill (a foreign id) must survive.
    keep = tmp_path / ".claude/skills/my-custom/SKILL.md"
    keep.parent.mkdir(parents=True)
    keep.write_text("mine\n")

    gen(tmp_path)

    assert not orphan.exists()  # python-naming is a known pack id, not in source -> cleaned
    assert not (tmp_path / ".claude/skills/python-naming").exists()  # empty dir pruned
    assert keep.read_text() == "mine\n"  # foreign id -> untouched
