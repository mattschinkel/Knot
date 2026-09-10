"""infer_fn for FnExpr / CallExpr (Phase 2 T12)."""

from __future__ import annotations

from knot.ast import CallExpr, FnExpr, IdentExpr, LitExpr, OpExpr
from knot.checker import TypeErrorVal, infer_fn, infer_type
from knot.types import FnType, I32


def test_infer_fn_simple():
    fn = FnExpr([("x", "i32")], OpExpr("MUL", [IdentExpr("x"), IdentExpr("x")]))
    t = infer_fn(fn)
    assert isinstance(t, FnType)
    assert t.params == (I32,)
    assert t.ret is I32


def test_infer_fn_via_infer_type():
    fn = FnExpr([("x", "i32")], IdentExpr("x"))
    assert isinstance(infer_type(fn), FnType)


def test_infer_call():
    fn = FnExpr([("x", "i32")], IdentExpr("x"))
    call = CallExpr(fn, [LitExpr(7)])
    assert infer_fn(call) is I32


def test_infer_call_arity_mismatch():
    fn = FnExpr([("x", "i32")], IdentExpr("x"))
    err = infer_fn(CallExpr(fn, []))
    assert isinstance(err, TypeErrorVal)


def test_infer_call_arg_mismatch():
    fn = FnExpr([("x", "i32")], IdentExpr("x"))
    err = infer_fn(CallExpr(fn, [LitExpr(True)]))
    assert isinstance(err, TypeErrorVal)


def test_infer_fn_requires_annotation():
    err = infer_fn(FnExpr([("x", None)], LitExpr(1)))
    assert isinstance(err, TypeErrorVal)
