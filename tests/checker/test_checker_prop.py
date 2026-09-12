"""Property-style tests for the type checker (Phase 2 T17)."""

from __future__ import annotations

from golem.ast import HoleExpr, IdentExpr, IfExpr, LitExpr, OpExpr
from golem.checker import TypeErrorVal, check_expr, infer_type
from golem.env import Env
from golem.types import ANY, I32, Type


def test_no_raise():
    samples = [
        LitExpr(1),
        LitExpr(True),
        OpExpr("ADD", [LitExpr(1), LitExpr(2)]),
        OpExpr("EQ", [LitExpr(1), LitExpr(2)]),
        IfExpr(LitExpr(True), LitExpr(1), LitExpr(2)),
        HoleExpr(id=1),
        HoleExpr(id=2, label="i32"),
        IdentExpr("missing"),
        OpExpr("ADD", [LitExpr(1), LitExpr(True)]),
    ]
    for node in samples:
        result = check_expr(node)
        assert isinstance(result, (Type, TypeErrorVal))


def test_hole_ok():
    assert infer_type(HoleExpr(id=1)) is ANY
    assert infer_type(HoleExpr(id=2, label="i32")) is I32
    # holes never raise — unknown label is TypeErrorVal
    err = check_expr(HoleExpr(id=3, label="nosuch"), Env())
    assert isinstance(err, TypeErrorVal)
