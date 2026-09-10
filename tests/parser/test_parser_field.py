from knot.parser import parse_field_access, parse_expr, ParseError
from knot.ast import OpExpr, IdentExpr
import pytest


def test_canonical_get_not_dot():
    n = parse_expr("GET[user, name]")
    assert isinstance(n, OpExpr)
    assert n.op == "GET"
    assert isinstance(n.children[0], IdentExpr)
    assert n.children[0].id == "user"
    assert isinstance(n.children[1], IdentExpr)
    assert n.children[1].id == "name"


def test_dot_sugar_rejected_in_expr():
    with pytest.raises(ParseError):
        parse_expr("user.name")


def test_parse_field_access_helper_rejected():
    with pytest.raises(ParseError):
        parse_field_access("user.name")
