"""infer ErrExpr + validate fixes (Phase 5 T6)."""

from __future__ import annotations

from golem.ast import ErrExpr, OpExpr
from golem.checker import TypeErrorVal, infer_type
from golem.parser import parse_err
from golem.types import NEVER


def test_infer_err_is_never():
    n = parse_err("ERR[TYPE_MISMATCH,[],i32,bool]")
    assert infer_type(n) is NEVER


def test_infer_err_with_valid_fixes():
    n = parse_err("ERR[TYPE_MISMATCH,[],i32,bool,REPLACE[x,?:i32],REMOVE_OP[]]")
    assert infer_type(n) is NEVER


def test_infer_err_bad_fix_shape():
    n = ErrExpr(
        "TYPE_MISMATCH",
        [],
        "i32",
        "bool",
        fixes=[OpExpr("REPLACE", [])],  # arity 0 — invalid
    )
    err = infer_type(n)
    assert isinstance(err, TypeErrorVal)
