"""check_binary_op for ADD/SUB/MUL/DIV/MOD (Phase 2 T6)."""

from __future__ import annotations

from knot.checker import TypeErrorVal, check_binary_op
from knot.types import I32, I64, F64, BOOL, STRING


def test_add_same_int():
    assert check_binary_op("ADD", I32, I32) is I32
    assert check_binary_op("ADD", I64, I64) is I64


def test_arith_ops_float():
    for op in ("ADD", "SUB", "MUL", "DIV", "MOD"):
        assert check_binary_op(op, F64, F64) is F64


def test_mismatch_no_cast():
    err = check_binary_op("ADD", I32, I64)
    assert isinstance(err, TypeErrorVal)


def test_non_numeric():
    err = check_binary_op("ADD", BOOL, BOOL)
    assert isinstance(err, TypeErrorVal)
    err2 = check_binary_op("ADD", STRING, STRING)
    assert isinstance(err2, TypeErrorVal)


def test_unknown_op():
    err = check_binary_op("XOR", I32, I32)
    assert isinstance(err, TypeErrorVal)
