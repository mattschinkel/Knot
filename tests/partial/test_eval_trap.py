"""evaluate hole trap as ErrorVal (Phase 4 T5)."""

from __future__ import annotations

from golem.ast import HoleExpr, LitExpr, OpExpr
from golem.partial import evaluate
from golem.values import ErrorVal, IntVal


def test_hole_traps():
    v = evaluate(HoleExpr(id=7))
    assert isinstance(v, ErrorVal)
    assert v.err.kind == "hole_trap"


def test_add_propagates_hole_trap():
    v = evaluate(OpExpr("ADD", [LitExpr(1), HoleExpr(id=3)]))
    assert isinstance(v, ErrorVal)
    assert v.err.kind == "hole_trap"


def test_add_literals_ok():
    v = evaluate(OpExpr("ADD", [LitExpr(2), LitExpr(3)]))
    assert isinstance(v, IntVal)
    assert v.value == 5


def test_never_raises_on_hole():
    for node in (HoleExpr(id=1), OpExpr("ADD", [HoleExpr(id=1), HoleExpr(id=2)])):
        assert isinstance(evaluate(node), ErrorVal)
