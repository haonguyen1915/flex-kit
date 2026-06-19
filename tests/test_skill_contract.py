"""The skill-contract check flags short/long descriptions and non-kebab names."""

from __future__ import annotations

from pathlib import Path

from flex_kit.checks import Ctx
from flex_kit.checks.skill_contract import CHECK
from flex_kit.config import Config
from flex_kit.skills import Skill


def _skill(skill_id: str, name: str, description: str) -> Skill:
    return Skill(
        id=skill_id,
        dir=Path("/nonexistent"),
        body="",
        frontmatter={"name": name, "description": description},
        references=[],
    )


def _ctx(*skills: Skill) -> Ctx:
    return Ctx(
        project_root=Path("."),
        config=Config(),
        skills=list(skills),
        agents=[],
        commands=[],
        docs=[],
        hosts={},
    )


def test_short_description_errors() -> None:
    findings = CHECK.run(_ctx(_skill("s", "s", "too short")))
    assert any(f.level == "error" and "too short" in f.msg for f in findings)


def test_long_description_warns() -> None:
    findings = CHECK.run(_ctx(_skill("s", "s", "x" * 2000)))
    assert any(f.level == "warn" and "long" in f.msg for f in findings)


def test_non_kebab_name_errors() -> None:
    findings = CHECK.run(_ctx(_skill("Bad_Name", "Bad_Name", "a sufficiently long description")))
    assert any(f.level == "error" and "kebab" in f.msg for f in findings)


def test_good_skill_passes() -> None:
    findings = CHECK.run(_ctx(_skill("ok", "ok", "a clear, sufficiently long description")))
    assert findings == []
