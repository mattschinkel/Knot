from knot.parser import parse_typed_lit, parse_expr, ParseError
from knot.ast import TypedLit
import pytest


def test_parse_typed_lit_int():
    n = parse_typed_lit("2:i32")
    assert isinstance(n, TypedLit)
    assert n.value == 2
    assert n.type_name == "i32"


def test_parse_typed_lit_float_unit():
    n = parse_typed_lit("10:meters")
    assert isinstance(n, TypedLit)
    assert n.value == 10
    assert n.type_name == "meters"


def test_parse_typed_lit_via_expr():
    n = parse_expr("42:i64")
    assert isinstance(n, TypedLit)
    assert n.value == 42
    assert n.type_name == "i64"


def test_parse_typed_lit_requires_type():
    with pytest.raises(ParseError):
        parse_typed_lit("42")
