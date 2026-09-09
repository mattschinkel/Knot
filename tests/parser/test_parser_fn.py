from knot.parser import parse_def, parse_fn, ParseError
from knot.ast import DefNode, FnExpr, OpExpr
import pytest


def test_parse_fn_simple():
    n = parse_fn("FN[x:i32] MUL[x, x]")
    assert isinstance(n, FnExpr)
    assert n.params == [("x", "i32")]
    assert isinstance(n.body, OpExpr)
    assert n.body.op == "MUL"


def test_parse_fn_multi_params():
    n = parse_fn("FN[a:i32, b:i32] ADD[a, b]")
    assert n.params == [("a", "i32"), ("b", "i32")]
    assert n.body.op == "ADD"


def test_parse_def_simple():
    n = parse_def("square = FN[x:i32] MUL[x, x]")
    assert isinstance(n, DefNode)
    assert n.name == "square"
    assert isinstance(n.body, FnExpr)


def test_parse_def_with_def_kw():
    n = parse_def("def square = FN[x] x")
    assert n.name == "square"
    assert isinstance(n.body, FnExpr)


def test_parse_fn_requires_fn():
    with pytest.raises(ParseError):
        parse_fn("ADD[1, 2]")
