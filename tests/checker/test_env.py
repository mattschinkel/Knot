"""Tests for the scoped type environment (Phase 2 T3)."""

from __future__ import annotations

import pytest

from knot.env import Env
from knot.types import I32, STRING, ListType


def test_bind_and_lookup():
    env = Env()
    env.bind("x", I32)
    assert env.lookup("x") is I32
    assert env.lookup("y") is None
    assert "x" in env
    assert "y" not in env


def test_enter_leave_scope_shadowing():
    env = Env()
    env.bind("x", I32)
    env.enter_scope("inner")
    env.bind("x", STRING)
    assert env.lookup("x") is STRING
    env.leave_scope()
    assert env.lookup("x") is I32


def test_outer_visible_in_inner():
    env = Env()
    env.bind("xs", ListType(I32))
    env.enter_scope("inner")
    assert env.lookup("xs") == ListType(I32)
    env.leave_scope()


def test_leave_root_raises():
    env = Env()
    with pytest.raises(RuntimeError):
        env.leave_scope()
