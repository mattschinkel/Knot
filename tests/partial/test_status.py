"""CompileStatus VALID / PARTIAL / INVALID (Phase 4 T1)."""

from __future__ import annotations

from knot.ast import HoleExpr, LitExpr, OpExpr
from knot.partial import CompileStatus, compile_check
from knot.types import I32


def test_valid_no_holes():
    r = compile_check(OpExpr("ADD", [LitExpr(1), LitExpr(2)]))
    assert r.status is CompileStatus.VALID
    assert r.typ is I32
    assert r.holes == ()
    assert r.errors == ()


def test_partial_with_hole():
    r = compile_check(OpExpr("ADD", [LitExpr(1), HoleExpr(id=7)]))
    assert r.status is CompileStatus.PARTIAL
    assert r.typ is I32
    assert len(r.holes) == 1
    assert r.errors == ()


def test_invalid_type_error():
    r = compile_check(OpExpr("ADD", [LitExpr(1), LitExpr(True)]))
    assert r.status is CompileStatus.INVALID
    assert r.typ is None
    assert len(r.errors) >= 1


def test_typed_hole_alone_is_partial():
    r = compile_check(HoleExpr(id=1, label="i32"))
    assert r.status is CompileStatus.PARTIAL
    assert r.typ is I32
