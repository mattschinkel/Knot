"""infer_type for LitExpr / TypedLit / IdentExpr / UnitExpr (Phase 2 T5)."""

from __future__ import annotations

from knot.ast import IdentExpr, LitExpr, TypedLit, UnitExpr
from knot.checker import TypeErrorVal, infer_type
from knot.env import Env
from knot.types import BOOL, I32, F64, STRING, UNIT


def test_infer_lit_int():
    assert infer_type(LitExpr(42)) is I32


def test_infer_lit_bool():
    assert infer_type(LitExpr(True)) is BOOL


def test_infer_lit_string():
    assert infer_type(LitExpr("hi")) is STRING


def test_infer_lit_float():
    assert infer_type(LitExpr(1.5)) is F64


def test_infer_typed_lit():
    assert infer_type(TypedLit(2, "i32")) is I32
    assert infer_type(TypedLit(True, "bool")) is BOOL


def test_infer_typed_lit_unknown():
    err = infer_type(TypedLit(1, "nope"))
    assert isinstance(err, TypeErrorVal)


def test_infer_unit_expr():
    assert infer_type(UnitExpr(id=0)) is UNIT


def test_infer_ident_bound():
    env = Env()
    env.bind("x", I32)
    assert infer_type(IdentExpr("x"), env) is I32


def test_infer_ident_unbound():
    err = infer_type(IdentExpr("y"), Env())
    assert isinstance(err, TypeErrorVal)
