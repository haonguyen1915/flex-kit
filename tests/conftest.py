"""Shared test fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolate_global_config(tmp_path_factory, monkeypatch):
    """Point flex-kit's global config (~/.flex-kit/config.json) at an empty temp path so no
    test ever reads the developer's real home config. Tests that exercise the global layer
    write to this path explicitly (via FLEXKIT_GLOBAL_CONFIG)."""
    path = tmp_path_factory.mktemp("flexkit-home") / "config.json"
    monkeypatch.setenv("FLEXKIT_GLOBAL_CONFIG", str(path))
