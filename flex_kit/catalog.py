"""The ids flex-kit itself can generate - bundled packs + the base template.

This is the "we already know it" half of orphan detection: gen records what it
produced in `.flexkit/.generated.json`, but that record can be lost (e.g. `init
--force` wipes `.flexkit/`). The bundled catalog is derivable from the installed
package, so gen can still recognise its OWN output (a `python-naming` skill, the
`reviewer` agent) as an orphan when it is no longer in source - while leaving truly
foreign, hand-authored ids untouched.

Caveat: it cannot recognise an id flex-kit no longer ships (a renamed base skill, a
skill dropped from a pack). The persisted record covers those; the two are
complementary, used together by gen.
"""

from __future__ import annotations

from pathlib import Path

_PACKS = Path(__file__).parent / "packs"
_TEMPLATE = Path(__file__).parent / "templates" / "flexkit"


def _dir_ids(base: Path, kind: str) -> set[str]:
    """Skill ids: each is a `<kind>/<id>/SKILL.md` directory."""
    d = base / kind
    return {p.name for p in d.iterdir() if (p / "SKILL.md").exists()} if d.is_dir() else set()


def _file_ids(base: Path, kind: str) -> set[str]:
    """Agent/command ids: each is a `<kind>/<id>.md` file (id = stem)."""
    d = base / kind
    return {p.stem for p in d.iterdir() if p.is_file()} if d.is_dir() else set()


def _packs() -> list[Path]:
    return sorted(p for p in _PACKS.iterdir() if p.is_dir()) if _PACKS.is_dir() else []


def owned_skill_ids() -> set[str]:
    ids = _dir_ids(_TEMPLATE, "skills")
    for pack in _packs():
        ids |= _dir_ids(pack, "skills")
    return ids


def owned_agent_ids() -> set[str]:
    ids = _file_ids(_TEMPLATE, "agents")
    for pack in _packs():
        ids |= _file_ids(pack, "agents")
    return ids


def owned_command_ids() -> set[str]:
    return _file_ids(_TEMPLATE, "commands")
