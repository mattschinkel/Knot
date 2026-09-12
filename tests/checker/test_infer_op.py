"""infer_type for OpExpr via check_binary_op / check_unary_op (Phase 2 T9)."""

from __future__ import annotations

from golem.ast import LitExpr, OpExpr
from golem.checker import TypeErrorVal, infer_type
from golem.types import I32, BOOL, F64


def test_infer_add():
    assert infer_type(OpExpr("ADD", [LitExpr(1), LitExpr(2)])) is I32


def test_infer_mul_nested():
    inner = OpExpr("ADD", [LitExpr(1), LitExpr(2)])
    assert infer_type(OpExpr("MUL", [inner, LitExpr(3)])) is I32


def test_infer_neg():
    assert infer_type(OpExpr("NEG", [LitExpr(1)])) is I32


def test_infer_not():
    assert infer_type(OpExpr("NOT", [LitExpr(True)])) is BOOL


def test_infer_eq():
    assert infer_type(OpExpr("EQ", [LitExpr(1), LitExpr(2)])) is BOOL


def test_infer_add_mismatch():
    # 1 is i32, 1.5 is f64 — no implicit cast
    err = infer_type(OpExpr("ADD", [LitExpr(1), LitExpr(1.5)]))
    assert isinstance(err, TypeErrorVal)


def test_infer_float_add():
    assert infer_type(OpExpr("ADD", [LitExpr(1.0), LitExpr(2.0)])) is F64
