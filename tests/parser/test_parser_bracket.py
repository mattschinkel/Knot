from golem.parser import parse_expr, parse_program, ParseError
from golem.ast import LitExpr, IdentExpr, OpExpr, HoleExpr, UnitExpr
from golem.addressing import reset_ids
import pytest


def setup_function():
    reset_ids()


def test_parse_program_empty():
    assert parse_program("") == []
    assert parse_program("   ") == []


def test_parse_lit_int():
    n = parse_expr("42")
    assert isinstance(n, LitExpr)
    assert n.value == 42


def test_parse_ident():
    n = parse_expr("foo")
    assert isinstance(n, IdentExpr)
    assert n.id == "foo"


def test_parse_op():
    n = parse_expr("ADD[1, 2]")
    assert isinstance(n, OpExpr)
    assert n.op == "ADD"
    assert len(n.children) == 2
    assert n.children[0].value == 1
    assert n.children[1].value == 2


def test_parse_nested_op():
    n = parse_expr("MUL[ADD[1, 2], 3]")
    assert isinstance(n, OpExpr)
    assert n.op == "MUL"
    assert n.children[0].op == "ADD"
    assert n.children[1].value == 3


def test_parse_hole():
    n = parse_expr("?")
    assert isinstance(n, HoleExpr)


def test_parse_unit():
    n = parse_expr("UNIT")
    assert isinstance(n, UnitExpr)


def test_parse_program_two_exprs():
    nodes = parse_program("ADD[1, 2]\nMUL[3, 4]")
    assert len(nodes) == 2
    assert nodes[0].op == "ADD"
    assert nodes[1].op == "MUL"


def test_parse_trailing_junk_raises():
    with pytest.raises(ParseError):
        parse_expr("ADD[1, 2] junk")
