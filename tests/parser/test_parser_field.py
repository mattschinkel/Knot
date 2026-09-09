from knot.parser import parse_field_access, parse_expr, ParseError
from knot.ast import FieldAccess, IdentExpr
import pytest


def test_parse_field_access_simple():
    n = parse_field_access("user.name")
    assert isinstance(n, FieldAccess)
    assert n.field_name == "name"
    assert isinstance(n.id, IdentExpr)
    assert n.id.id == "user"


def test_parse_field_access_chained():
    n = parse_field_access("a.b.c")
    assert isinstance(n, FieldAccess)
    assert n.field_name == "c"
    assert isinstance(n.id, FieldAccess)
    assert n.id.field_name == "b"


def test_parse_expr_field_sugar():
    n = parse_expr("user.name")
    assert isinstance(n, FieldAccess)
    assert n.field_name == "name"


def test_parse_field_access_requires_dot():
    with pytest.raises(ParseError):
        parse_field_access("user")
