"""infer_def for DefNode bindings via Env (Phase 2 T13)."""

from __future__ import annotations

from knot.ast import DefNode, FnExpr, IdentExpr, LitExpr, OpExpr
from knot.checker import TypeErrorVal, infer_def, infer_type
from knot.env import Env
from knot.types import FnType, I32


def test_infer_def_lit():
    env = Env()
    t = infer_def(DefNode("x", LitExpr(1)), env)
    assert t is I32
    assert env.lookup("x") is I32


def test_infer_def_fn():
    env = Env()
    fn = FnExpr([("n", "i32")], IdentExpr("n"))
    t = infer_def(DefNode("id", fn), env)
    assert isinstance(t, FnType)
    assert env.lookup("id") is t


def test_infer_def_then_ident():
    env = Env()
    infer_def(DefNode("x", LitExpr(42)), env)
    assert infer_type(IdentExpr("x"), env) is I32


def test_infer_def_body_error():
    env = Env()
    err = infer_def(DefNode("bad", OpExpr("ADD", [LitExpr(1), LitExpr(True)])), env)
    assert isinstance(err, TypeErrorVal)
    assert env.lookup("bad") is None
