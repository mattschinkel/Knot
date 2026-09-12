"""suggest_candidates (Phase 4 T3)."""

from __future__ import annotations

from knot.env import Env
from knot.partial import suggest_candidates
from knot.types import BOOL, I32, STRING


def test_defaults_for_base_types():
    assert "0" in suggest_candidates(I32)
    assert "false" in suggest_candidates(BOOL)
    assert '""' in suggest_candidates(STRING)


def test_env_bindings_preferred():
    env = Env()
    env.bind("count", I32)
    env.bind("name", STRING)
    cands = suggest_candidates(I32, env)
    assert "count" in cands
    assert "name" not in cands


def test_none_expected_empty():
    assert suggest_candidates(None) == ()
