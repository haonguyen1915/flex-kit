"""Check protocol shared by tool-provided and project-provided checks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from flex_kit.config import Config
from flex_kit.skills import Skill


@dataclass
class Ctx:
    project_root: Path
    config: Config
    skills: list[Skill]
    hosts: dict


@dataclass
class Finding:
    level: str  # "error" | "warn"
    msg: str


@dataclass
class Check:
    id: str
    run: Callable[[Ctx], list[Finding]]
