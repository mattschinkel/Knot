"""HoleReport collection (Phase 4 T2)."""

from __future__ import annotations

from knot.ast import HoleExpr, LitExpr, OpExpr
from knot.partial import collect_holes, compile_check
from knot.types import I32


def test_collect_bare_hole_in_add():
    holes = collect_holes(OpExpr("ADD", [LitExpr(3), HoleExpr(id=9)]))
    assert len(holes) == 1
    h = holes[0]
    assert h.hole_id == 9
    assert h.expected is I32
    assert "ADD" in h.context
    assert "0" in h.candidates


def test_compile_check_includes_candidates():
    r = compile_check(OpExpr("ADD", [HoleExpr(id=1), LitExpr(2)]))
    assert r.holes[0].expected is I32
    assert r.holes[0].candidates


def test_collect_nested_holes():
    node = OpExpr(
        "ADD",
        [HoleExpr(id=1, label="i32"), OpExpr("MUL", [LitExpr(2), HoleExpr(id=2)])],
    )
    holes = collect_holes(node)
    assert {h.hole_id for h in holes} == {1, 2}
