"""Extension registries. Adding a host or a check is additive: drop a module in
flex_kit/hosts/ or flex_kit/checks/ and register it here - no change to
gen/doctor.
"""

from __future__ import annotations

from flex_kit.checks import generated_in_sync, skill_refs, source_valid
from flex_kit.hosts import claude, codex

HOSTS = {claude.ID: claude, codex.ID: codex}

# Tool-provided checks. Project-specific checks load from .flexkit/checks/.
CHECKS = [source_valid.CHECK, skill_refs.CHECK, generated_in_sync.CHECK]
