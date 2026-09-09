from knot.parser import parse_hole, parse_expr, ParseError
from knot.ast import HoleExpr
import pytest


def test_parse_hole_bare():
    n = parse_hole("?")
    assert isinstance(n, HoleExpr)


def test_parse_hole_typed():
    n = parse_hole("?:i32")
    assert isinstance(n, HoleExpr)
    assert n.label == "i32"


def test_parse_hole_via_expr():
    n = parse_expr("?")
    assert isinstance(n, HoleExpr)


def test_parse_hole_rejects_non_hole():
    with pytest.raises(ParseError):
        parse_hole("42")
