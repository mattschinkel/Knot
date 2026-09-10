"""check_access for GET / FIELD / SET (Phase 2 T14)."""

from __future__ import annotations

from knot.ast import IdentExpr, LitExpr, OpExpr
from knot.checker import TypeErrorVal, check_access, infer_type
from knot.env import Env
from knot.types import I32, RecordType, STRING, TupleType


def _user_rec():
    return RecordType("User", (("age", I32), ("name", STRING)))


def test_get_record_field():
    rec = _user_rec()
    assert check_access("GET", rec, "name") is STRING
    assert check_access("FIELD", rec, IdentExpr("age")) is I32


def test_get_unknown_field():
    err = check_access("GET", _user_rec(), "email")
    assert isinstance(err, TypeErrorVal)


def test_get_tuple_index():
    tup = TupleType((I32, STRING))
    assert check_access("GET", tup, 0) is I32
    assert check_access("GET", tup, LitExpr(1)) is STRING


def test_set_record_ok():
    rec = _user_rec()
    assert check_access("SET", rec, "age", I32) is rec


def test_set_record_mismatch():
    err = check_access("SET", _user_rec(), "age", STRING)
    assert isinstance(err, TypeErrorVal)


def test_infer_get_op():
    env = Env()
    env.bind("u", _user_rec())
    node = OpExpr("GET", [IdentExpr("u"), IdentExpr("name")])
    assert infer_type(node, env) is STRING
