"""Property-style tests for the canonical bracket parser."""
import pytest

from knot.addressing import reset_ids
from knot.ast import FieldAccess, HoleExpr, OpExpr
from knot.parser import ParseError, parse_expr, parse_field_access, parse_hole


def setup_function():
    reset_ids()


def test_bracket_only():
    node = parse_expr("ADD[1, 2]")
    assert isinstance(node, OpExpr)
    assert node.op == "ADD"
    with pytest.raises(ParseError):
        parse_expr("ADD(1, 2)")


def test_field_sugar():
    node = parse_field_access("user.name")
    assert isinstance(node, FieldAccess)
    assert node.field_name == "name"
    getn = parse_expr("GET[user, name]")
    assert isinstance(getn, OpExpr)
    assert getn.op == "GET"


def test_hole_support():
    h = parse_hole("?")
    assert isinstance(h, HoleExpr)
    assert h.label is None
    ht = parse_hole("?:i32")
    assert isinstance(ht, HoleExpr)
    assert ht.label == "i32"
