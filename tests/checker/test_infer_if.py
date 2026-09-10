"""infer_if for IfExpr / IF OpExpr (Phase 2 T10)."""

from __future__ import annotations

from knot.ast import IfExpr, LitExpr, OpExpr
from knot.checker import TypeErrorVal, infer_if, infer_type
from knot.types import BOOL, I32


def test_infer_if_same_branches():
    node = IfExpr(LitExpr(True), LitExpr(1), LitExpr(2))
    assert infer_if(node) is I32


def test_infer_if_op_expr():
    node = OpExpr("IF", [LitExpr(True), LitExpr(1), LitExpr(2)])
    assert infer_if(node) is I32
    assert infer_type(node) is I32


def test_infer_if_bool_result():
    node = IfExpr(LitExpr(True), LitExpr(True), LitExpr(False))
    assert infer_if(node) is BOOL


def test_infer_if_branch_mismatch():
    err = infer_if(IfExpr(LitExpr(True), LitExpr(1), LitExpr(True)))
    assert isinstance(err, TypeErrorVal)


def test_infer_if_non_bool_cond():
    err = infer_if(IfExpr(LitExpr(1), LitExpr(2), LitExpr(3)))
    assert isinstance(err, TypeErrorVal)


def test_infer_cond_op_alias():
    node = OpExpr("COND", [LitExpr(False), LitExpr(10), LitExpr(20)])
    assert infer_if(node) is I32
