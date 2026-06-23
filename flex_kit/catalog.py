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
    """Skill ids: each is a `<id>/SKILL.md`, found at any depth.

    A bundled pack may nest skills in group folders (`skills/<group>/<id>/SKILL.md`) for
    tidiness; `add` flattens them to `skills/<id>`, so the owned id is the SKILL.md's
    parent dir name regardless of how deep the group nesting is."""
    d = base / kind
    return {p.parent.name for p in d.rglob("SKILL.md")} if d.is_dir() else set()


def _file_ids(base: Path, kind: str) -> set[str]:
    """Agent/command ids: each is a `<kind>/<id>.md` file (id = stem)."""
    d = base / kind
    return {p.stem for p in d.iterdir() if p.is_file()} if d.is_dir() else set()


def _packs() -> list[Path]:
    """Pack dirs, found one category level deep (`packs/<category>/<pack>`) or flat.

    Mirrors `add._pack_dirs`: packs are grouped by axis (`languages/`, `frameworks/`,
    `disciplines/`) for tidiness, so the catalog must look inside a category dir too."""
    if not _PACKS.is_dir():
        return []
    out: list[Path] = []
    for top in sorted(_PACKS.iterdir()):
        if not top.is_dir():
            continue
        if (top / "skills").is_dir() or (top / "agents").is_dir():
            out.append(top)
        else:
            out.extend(
                c
                for c in sorted(top.iterdir())
                if c.is_dir() and ((c / "skills").is_dir() or (c / "agents").is_dir())
            )
    return out


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
