"""Checker base: type_error / TypeErrorVal (Phase 2 T4)."""

from __future__ import annotations

from knot.checker import TypeErrorVal, type_error


def test_type_error_creation():
    err = type_error("Type mismatch", (1, 2, 3))
    assert isinstance(err, TypeErrorVal)
    assert err.message == "Type mismatch"
    assert err.path == (1, 2, 3)


def test_type_error_empty_path():
    err = type_error("Type mismatch", ())
    assert err.message == "Type mismatch"
    assert err.path == ()


def test_type_error_str():
    err = type_error("Type mismatch", (1, 2, 3))
    assert str(err) == "Type mismatch"


def test_type_error_repr():
    err = type_error("Type mismatch", (1, 2, 3))
    assert "Type mismatch" in repr(err)
    assert "path=" in repr(err)


def test_to_error_val():
    err = type_error("bad", ("a", "b"))
    ev = err.to_error_val()
    assert ev.err.kind == "type"
    assert ev.err.message == "bad"
    assert ev.err.node == "a.b"
