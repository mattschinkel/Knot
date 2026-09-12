from golem.parser import parse_def, parse_fn, parse_expr, ParseError
from golem.ast import DefNode, FnExpr, OpExpr
import pytest


def test_parse_fn_canonical():
    n = parse_fn("FN[[x:i32], MUL[x, x]]")
    assert isinstance(n, FnExpr)
    assert n.params == [("x", "i32")]
    assert isinstance(n.body, OpExpr)
    assert n.body.op == "MUL"


def test_parse_fn_multi_params():
    n = parse_fn("FN[[a:i32, b:i32], ADD[a, b]]")
    assert n.params == [("a", "i32"), ("b", "i32")]
    assert n.body.op == "ADD"


def test_parse_def_canonical():
    n = parse_def("DEF[square, FN[[x:i32], MUL[x, x]]]")
    assert isinstance(n, DefNode)
    assert n.name == "square"
    assert isinstance(n.body, FnExpr)


def test_parse_def_via_expr():
    n = parse_expr("DEF[x, 1]")
    assert isinstance(n, DefNode)
    assert n.name == "x"


def test_legacy_fn_juxtaposition_rejected():
    with pytest.raises(ParseError):
        parse_fn("FN[x:i32] MUL[x, x]")


def test_legacy_eq_def_rejected():
    with pytest.raises(ParseError):
        parse_def("square = FN[[x:i32], MUL[x, x]]")
