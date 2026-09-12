"""Hole constraint propagation (Phase 4 T4 / D-FB10)."""

from __future__ import annotations

from knot.ast import HoleExpr, IfExpr, LitExpr, OpExpr
from knot.checker import TypeErrorVal, infer_type
from knot.partial import CompileStatus, compile_check
from knot.types import BOOL, I32


def test_add_bare_hole_adopts_i32():
    t = infer_type(OpExpr("ADD", [LitExpr(1), HoleExpr(id=1)]))
    assert t is I32
    t2 = infer_type(OpExpr("ADD", [HoleExpr(id=2), LitExpr(5)]))
    assert t2 is I32


def test_eq_bare_hole_adopts_sibling():
    t = infer_type(OpExpr("EQ", [LitExpr(1), HoleExpr(id=1)]))
    assert t is BOOL


def test_if_branch_hole():
    t = infer_type(IfExpr(LitExpr(True), LitExpr(1), HoleExpr(id=3)))
    assert t is I32


def test_not_hole_is_bool():
    t = infer_type(OpExpr("NOT", [HoleExpr(id=1)]))
    assert t is BOOL


def test_both_holes_with_outer_expected():
    t = infer_type(
        OpExpr("ADD", [HoleExpr(id=1), HoleExpr(id=2)]),
        expected=I32,
    )
    assert t is I32


def test_mismatched_typed_hole_still_errors():
    err = infer_type(OpExpr("ADD", [LitExpr(1), HoleExpr(id=1, label="bool")]))
    assert isinstance(err, TypeErrorVal)


def test_partial_not_invalid_for_propagated_hole():
    r = compile_check(OpExpr("MUL", [LitExpr(2), HoleExpr(id=8)]))
    assert r.status is CompileStatus.PARTIAL
    assert r.typ is I32
