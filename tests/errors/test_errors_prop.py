"""Property tests for structured errors (Phase 5 T7)."""

from __future__ import annotations

from golem.ast import LitExpr, OpExpr
from golem.canonical import normalize, print_canonical
from golem.diagnose import diagnose
from golem.parser import parse_expr
from golem.partial import CompileStatus, compile_check
from golem.types import NEVER


SAMPLES = (
    "ADD[1,2]",
    "ADD[1,true]",
    "ERR[TYPE_MISMATCH,[],i32,bool]",
    "ERR[TYPE_MISMATCH,[0],i32,bool,REPLACE[x,?:i32]]",
    "?:i32",
    "DEF[x,1]",
)


def test_no_raise():
    for s in SAMPLES:
        node = parse_expr(s)
        _ = print_canonical(node)
        _ = normalize(s)
        _ = diagnose(node)
        _ = compile_check(node)
        _ = infer_safe(node)


def infer_safe(node):
    from golem.checker import infer_type

    return infer_type(node)


def test_err_roundtrip_suite():
    for s in (
        "ERR[TYPE_MISMATCH,[],i32,bool]",
        "ERR[TYPE_MISMATCH,[body,0],f64@meters,f64@seconds,CONVERT[x,f64@meters]]",
        "ERR[HOLE_TRAP,[7],i32,any,HOLE[i32]]",
    ):
        assert normalize(s) == print_canonical(parse_expr(s))


def test_invalid_compile_still_status():
    r = compile_check(OpExpr("ADD", [LitExpr(1), LitExpr(True)]))
    assert r.status is CompileStatus.INVALID
