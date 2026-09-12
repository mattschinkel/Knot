"""Repair suggestions (Phase 5 T4)."""

from __future__ import annotations

from golem.ast import OpExpr
from golem.repairs import Repair, suggest_repairs, validate_fix
from golem.types import BOOL, I32


def test_suggest_type_mismatch():
    reps = suggest_repairs(
        code="TYPE_MISMATCH",
        op="ADD",
        expected=I32,
        actual=BOOL,
        path=(1,),
    )
    kinds = {r.kind for r in reps}
    assert "replace" in kinds
    assert "remove_op" in kinds
    assert any(r.payload == "i32" for r in reps if r.kind == "replace")


def test_suggest_numeric_convert():
    reps = suggest_repairs(expected="i64", actual="i32", op="ADD")
    assert any(r.kind == "convert" for r in reps)


def test_validate_fix_shapes():
    assert validate_fix(OpExpr("REPLACE", [OpExpr("HOLE", []), OpExpr("HOLE", [])]))
    assert validate_fix(OpExpr("REMOVE_OP", []))
    assert not validate_fix(OpExpr("REPLACE", []))
    assert not validate_fix(OpExpr("ADD", []))


def test_repair_to_air():
    air = Repair(kind="remove_op").to_air()
    assert air == "REMOVE_OP[]"
