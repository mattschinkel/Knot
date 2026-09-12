"""ERR parse / AST (Phase 5 T1–T2)."""

from __future__ import annotations

from knot.ast import ErrExpr, HoleExpr, OpExpr
from knot.parser import parse_err, parse_expr


def test_parse_err_minimal():
    n = parse_err("ERR[TYPE_MISMATCH,[],i32,bool]")
    assert isinstance(n, ErrExpr)
    assert n.code == "TYPE_MISMATCH"
    assert n.path == []
    assert n.expected == "i32"
    assert n.actual == "bool"
    assert n.fixes == []


def test_parse_err_with_path_and_fix():
    n = parse_expr(
        "ERR[TYPE_MISMATCH,[body,0],i32,bool,REPLACE[x,?:i32],REMOVE_OP[]]"
    )
    assert isinstance(n, ErrExpr)
    assert n.path == ["body", 0]
    assert len(n.fixes) == 2
    assert isinstance(n.fixes[0], OpExpr)
    assert n.fixes[0].op == "REPLACE"
    assert isinstance(n.fixes[0].children[1], HoleExpr)
    assert n.fixes[1].op == "REMOVE_OP"


def test_parse_err_dim_types():
    n = parse_err("ERR[DIM_MISMATCH,[1],f64@meters,f64@seconds]")
    assert n.expected == "f64@meters"
    assert n.actual == "f64@seconds"


def test_parse_err_allows_spaces():
    n = parse_expr("ERR[ TYPE_MISMATCH , [a] , i32 , bool ]")
    assert n.code == "TYPE_MISMATCH"
    assert n.path == ["a"]
