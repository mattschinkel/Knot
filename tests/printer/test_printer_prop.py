"""Property-style tests for the pretty printer view."""
from knot.addressing import reset_ids
from knot.parser import parse_def, parse_expr
from knot.printer import print_ast


def setup_function():
    reset_ids()


def test_roundtrip():
    # Printer is a view (not invertible to brackets); check semantic content survives.
    out = print_ast(parse_expr("ADD[1, 2]"))
    assert "1" in out and "2" in out
    assert "+" in out or "ADD" in out


def test_no_bracket():
    samples = [
        parse_expr("ADD[1, 2]"),
        parse_expr("MUL[x, y]"),
        parse_expr("MAP[xs, f]"),
        parse_def("square = FN[x:i32] MUL[x, x]"),
        parse_expr("GET[user, name]"),
    ]
    for node in samples:
        text = print_ast(node)
        assert "[" not in text
        assert "]" not in text
