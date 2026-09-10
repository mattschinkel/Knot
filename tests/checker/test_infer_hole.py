"""infer_hole for HoleExpr (Phase 2 T11)."""

from __future__ import annotations

from knot.ast import HoleExpr
from knot.checker import TypeErrorVal, infer_hole, infer_type
from knot.types import ANY, I32, F64


def test_infer_hole_bare():
    assert infer_hole(HoleExpr(id=1)) is ANY
    assert infer_type(HoleExpr(id=2)) is ANY


def test_infer_hole_typed_i32():
    assert infer_hole(HoleExpr(id=1, label="i32")) is I32


def test_infer_hole_typed_dim():
    assert infer_hole(HoleExpr(id=1, label="f64@meters")) is F64


def test_infer_hole_unknown_label():
    err = infer_hole(HoleExpr(id=1, label="nosuch"))
    assert isinstance(err, TypeErrorVal)
