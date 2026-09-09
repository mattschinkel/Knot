"""Property tests for the value representation (Phase 0)."""

from __future__ import annotations

from knot.values import (
    IntVal, FloatVal, BoolVal, StringVal, BytesVal, UnitVal, MeasuredVal,
    ListVal, SetVal, MapVal, TupleVal, SumVal, RecordVal, HoleVal, ErrorVal,
)
from knot.types import (
    BaseType, ListType, SetType, MapType, TupleType, RecordType, SumType,
    UnitType, NEVER, UNIT, I32, I64, F64, STRING,
)
from knot.errors import StructuredError
from knot.units import m, s


def test_intval_type_and_equality_type_aware():
    assert IntVal(32, 2).type == BaseType("i32")
    assert IntVal(64, 2).type == BaseType("i64")
    # 2:i32 != 2:i64 (distinct types -> distinct values)
    assert IntVal(32, 2) != IntVal(64, 2)
    assert IntVal(32, 2) == IntVal(32, 2)


def test_stringval_is_codepoints():
    # Q2: string is a code-point sequence (Python str).
    v = StringVal("héllo")
    assert v.type == STRING
    assert v.value == "héllo"


def test_bytesval_distinct_from_string():
    assert BytesVal(b"hi").type == BaseType("bytes")
    assert BytesVal(b"hi") != StringVal("hi")


def test_unitval_single():
    u = UnitVal()
    assert u.type == UNIT
    assert UnitVal() == UnitVal()  # one value, equal


def test_measured_val_carries_dimension():
    v = MeasuredVal(FloatVal(64, 10.0), m)
    assert v.type == UnitType(F64, m)
    assert v.dim == m


def test_listval_type():
    v = ListVal((IntVal(32, 1), IntVal(32, 2)), I32)
    assert v.type == ListType(I32)
    assert v.items[1] == IntVal(32, 2)


def test_setval_order_independent():
    a = SetVal(frozenset({IntVal(32, 1), IntVal(32, 2)}), I32)
    b = SetVal(frozenset({IntVal(32, 2), IntVal(32, 1)}), I32)
    assert a == b
    assert hash(a) == hash(b)


def test_mapval_order_independent():
    a = MapVal(frozenset({(IntVal(32, 1), StringVal("a"))}), I32, STRING)
    b = MapVal(frozenset({(IntVal(32, 1), StringVal("a"))}), I32, STRING)
    assert a == b
    assert a.type == MapType(I32, STRING)


def test_tupleval():
    v = TupleVal((IntVal(32, 1), StringVal("x")), (I32, STRING))
    assert v.type == TupleType((I32, STRING))


def test_sumval():
    circle = RecordType("Circle", (("r", F64),))
    shape = SumType((("Circle", circle),))
    v = SumVal("Circle", RecordVal(frozenset({("r", FloatVal(64, 1.0))}), circle), shape)
    assert v.type == shape
    assert v.tag == "Circle"


def test_recordval_type():
    user_t = RecordType("User", (("age", I32), ("name", STRING)))
    v = RecordVal(frozenset({("age", IntVal(32, 25)), ("name", StringVal("Bob"))}), user_t)
    assert v.type == user_t


def test_holeval_type_checks_against_anything():
    # D3: a hole type-checks against any type as PARTIAL (no crash).
    h = HoleVal(I32)
    assert h.expected == I32
    bare = HoleVal(None)
    assert bare.expected is None
    # a hole is a value, hashable
    assert hash(h) == hash(HoleVal(I32))


def test_errorval_type_is_never():
    e = ErrorVal(StructuredError(kind="dim", op="ADD", message="m + s"))
    # never <: everything, so an error flows where any type is expected
    assert e.type == NEVER


def test_unit_mismatch_returns_error_not_raise():
    # D4: meters + seconds returns an ErrorVal instead of raising.
    # (Kernel arithmetic is Phase 2; here we just construct the error value.)
    err = ErrorVal(StructuredError(kind="dim", op="ADD", expected=m, got=s,
                                   message="dimension mismatch"))
    assert err.err.kind == "dim"
    assert err.err.op == "ADD"
    assert str(err)  # has a string form
