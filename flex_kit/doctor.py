"""Run validation checks: tool-provided + project-provided (.flexkit/checks/)."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path

from flex_kit.checks import Check, Ctx, Finding
from flex_kit.config import load_config
from flex_kit.registry import CHECKS, HOSTS
from flex_kit.skills import discover_skills


@dataclass
class CheckResult:
    id: str
    findings: list[Finding]


def _load_project_checks(project_root: Path) -> list[Check]:
    checks_dir = project_root / ".flexkit" / "checks"
    if not checks_dir.exists():
        return []
    loaded: list[Check] = []
    for path in sorted(checks_dir.glob("*.py")):
        spec = importlib.util.spec_from_file_location(f"flexkit_project_check_{path.stem}", path)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        check = getattr(mod, "CHECK", None)
        if isinstance(check, Check):
            loaded.append(check)
    return loaded


def doctor(project_root: Path) -> list[CheckResult]:
    config = load_config(project_root)
    skills = discover_skills(project_root, config.skills_dir)
    ctx = Ctx(project_root=project_root, config=config, skills=skills, hosts=HOSTS)

    results: list[CheckResult] = []
    for check in [*CHECKS, *_load_project_checks(project_root)]:
        results.append(CheckResult(check.id, check.run(ctx) or []))
    return results
