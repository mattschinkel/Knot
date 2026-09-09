from knot.bin import serialize, deserialize
from knot.parser import parse_expr, parse_def, parse_program
from knot.ast import LitExpr, OpExpr, DefNode
from knot.addressing import reset_ids


def setup_function():
    reset_ids()


def test_serialize_lit_roundtrip():
    n = parse_expr("42")
    data = serialize(n)
    assert isinstance(data, (bytes, bytearray))
    out = deserialize(data)
    assert isinstance(out, LitExpr)
    assert out.value == 42


def test_serialize_op_roundtrip():
    n = parse_expr("ADD[1, 2]")
    out = deserialize(serialize(n))
    assert isinstance(out, OpExpr)
    assert out.op == "ADD"
    assert out.children[0].value == 1
    assert out.children[1].value == 2


def test_serialize_def_roundtrip():
    n = parse_def("square = FN[x:i32] MUL[x, x]")
    out = deserialize(serialize(n))
    assert isinstance(out, DefNode)
    assert out.name == "square"
    assert out.body.params == [("x", "i32")]


def test_serialize_program_roundtrip():
    nodes = parse_program("ADD[1, 2]\nMUL[3, 4]")
    out = deserialize(serialize(nodes))
    assert len(out) == 2
    assert out[0].op == "ADD"
    assert out[1].op == "MUL"
