"""Tests for the structured error shape (Phase 0)."""

from __future__ import annotations

from golem.errors import StructuredError


def test_error_fields():
    e = StructuredError(kind="type", op="ADD", expected=None, got=None,
                        message="bad")
    assert e.kind == "type"
    assert e.op == "ADD"
    assert e.message == "bad"
    assert e.repair == ()


def test_error_frozen_and_hashable():
    e = StructuredError(kind="dim", op="MUL", message="m·s")
    assert hash(e) == hash(StructuredError(kind="dim", op="MUL", message="m·s"))
    # frozen: cannot reassign
    import dataclasses
    try:
        e.kind = "x"  # type: ignore[misc]
        raise AssertionError("expected frozen dataclass to reject assignment")
    except dataclasses.FrozenInstanceError:
        pass


def test_error_str_form():
    e = StructuredError(kind="dim", op="ADD", node="expr.3", message="m + s")
    s = str(e)
    assert "dim" in s
    assert "ADD" in s
    assert "expr.3" in s
