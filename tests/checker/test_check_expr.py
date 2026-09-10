"""check_expr public dispatcher (Phase 2 T16)."""

from __future__ import annotations

from knot.ast import DefNode, FnExpr, HoleExpr, IdentExpr, IfExpr, LitExpr, OpExpr
from knot.checker import TypeErrorVal, check_expr
from knot.env import Env
from knot.types import ANY, FnType, I32, BOOL


def test_check_expr_lit():
    assert check_expr(LitExpr(1)) is I32


def test_check_expr_op():
    assert check_expr(OpExpr("ADD", [LitExpr(1), LitExpr(2)])) is I32


def test_check_expr_if():
    assert check_expr(IfExpr(LitExpr(True), LitExpr(1), LitExpr(2))) is I32


def test_check_expr_hole():
    assert check_expr(HoleExpr(id=1)) is ANY


def test_check_expr_def():
    env = Env()
    assert check_expr(DefNode("x", LitExpr(9)), env) is I32
    assert env.lookup("x") is I32


def test_check_expr_fn():
    t = check_expr(FnExpr([("x", "i32")], IdentExpr("x")))
    assert isinstance(t, FnType) and t.ret is I32


def test_check_expr_unbound():
    err = check_expr(IdentExpr("missing"))
    assert isinstance(err, TypeErrorVal)


def test_check_expr_mismatch():
    err = check_expr(OpExpr("ADD", [LitExpr(1), LitExpr(True)]))
    assert isinstance(err, TypeErrorVal)
