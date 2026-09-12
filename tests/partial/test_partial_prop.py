"""Property tests for partial compile (Phase 4 T6)."""

from __future__ import annotations

from golem.ast import HoleExpr, IfExpr, LitExpr, OpExpr
from golem.partial import CompileStatus, compile_check, evaluate
from golem.values import ErrorVal, Value


# Fixed suite for M4: hole-bearing programs that should be PARTIAL.
PARTIAL_SUITE = (
    OpExpr("ADD", [LitExpr(1), HoleExpr(id=1)]),
    OpExpr("ADD", [HoleExpr(id=2), LitExpr(2)]),
    OpExpr("EQ", [LitExpr(1), HoleExpr(id=3)]),
    IfExpr(LitExpr(True), LitExpr(1), HoleExpr(id=4)),
    HoleExpr(id=5, label="i32"),
    OpExpr("NOT", [HoleExpr(id=6)]),
    OpExpr("MUL", [LitExpr(3), HoleExpr(id=7, label="i32")]),
)


def test_no_raise():
    samples = list(PARTIAL_SUITE) + [
        OpExpr("ADD", [LitExpr(1), LitExpr(2)]),
        OpExpr("ADD", [LitExpr(1), LitExpr(True)]),
        HoleExpr(id=99, label="nosuch"),
    ]
    for node in samples:
        r = compile_check(node)
        assert r.status in CompileStatus
        v = evaluate(node)
        assert isinstance(v, (Value, ErrorVal)) or isinstance(v, Value)


def test_pure_ok_partial_suite():
    """Every suite member is PARTIAL (type-correct with holes)."""
    for node in PARTIAL_SUITE:
        r = compile_check(node)
        assert r.status is CompileStatus.PARTIAL, (node, r)


def test_m4_coherence():
    """M4 = fraction of PARTIAL_SUITE that compile as PARTIAL."""
    ok = sum(
        1 for n in PARTIAL_SUITE if compile_check(n).status is CompileStatus.PARTIAL
    )
    assert ok / len(PARTIAL_SUITE) == 1.0
