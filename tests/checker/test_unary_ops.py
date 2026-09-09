"""check_unary_op for NEG / NOT (Phase 2 T7)."""

from __future__ import annotations

from knot.checker import TypeErrorVal, check_unary_op
from knot.types import I32, I64, F32, F64, BOOL, STRING


def test_neg_numeric():
    for t in (I32, I64, F32, F64):
        assert check_unary_op("NEG", t) is t


def test_neg_non_numeric():
    err = check_unary_op("NEG", BOOL)
    assert isinstance(err, TypeErrorVal)
    err2 = check_unary_op("NEG", STRING)
    assert isinstance(err2, TypeErrorVal)


def test_not_bool():
    assert check_unary_op("NOT", BOOL) is BOOL


def test_not_non_bool():
    err = check_unary_op("NOT", I32)
    assert isinstance(err, TypeErrorVal)


def test_unknown_unary():
    err = check_unary_op("ABS", I32)
    assert isinstance(err, TypeErrorVal)
