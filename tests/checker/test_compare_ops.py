"""check_compare_op for EQ/NE/LT/LE/GT/GE/AND/OR (Phase 2 T8)."""

from __future__ import annotations

from golem.checker import TypeErrorVal, check_compare_op
from golem.types import I32, I64, F64, BOOL, STRING


def test_eq_ne_same_type():
    assert check_compare_op("EQ", I32, I32) is BOOL
    assert check_compare_op("NE", STRING, STRING) is BOOL


def test_eq_mismatch():
    err = check_compare_op("EQ", I32, I64)
    assert isinstance(err, TypeErrorVal)


def test_ordered_numeric():
    for op in ("LT", "LE", "GT", "GE"):
        assert check_compare_op(op, I32, I32) is BOOL
        assert check_compare_op(op, F64, F64) is BOOL


def test_ordered_mismatch_or_non_numeric():
    assert isinstance(check_compare_op("LT", I32, I64), TypeErrorVal)
    assert isinstance(check_compare_op("LT", BOOL, BOOL), TypeErrorVal)


def test_and_or():
    assert check_compare_op("AND", BOOL, BOOL) is BOOL
    assert check_compare_op("OR", BOOL, BOOL) is BOOL
    assert isinstance(check_compare_op("AND", I32, I32), TypeErrorVal)


def test_unknown_op():
    assert isinstance(check_compare_op("XOR", BOOL, BOOL), TypeErrorVal)
