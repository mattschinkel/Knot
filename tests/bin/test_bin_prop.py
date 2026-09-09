"""Property-style tests for bin serialize/deserialize."""
from knot.addressing import reset_ids
from knot.ast import OpExpr
from knot.bin import deserialize, serialize
from knot.parser import parse_def, parse_expr, parse_program


def setup_function():
    reset_ids()


def test_roundtrip():
    samples = ["42", "ADD[1, 2]", "MUL[x, y]", "GET[user, name]", "?:i32"]
    for src in samples:
        node = parse_expr(src)
        out = deserialize(serialize(node))
        assert type(out) is type(node)


def test_id_stability():
    reset_ids()
    a = parse_expr("ADD[1, 2]")
    b = deserialize(serialize(a))
    assert isinstance(a, OpExpr) and isinstance(b, OpExpr)
    assert a.op == b.op
    assert a.children[0].value == b.children[0].value


def test_def_and_program_roundtrip():
    d = parse_def("f = FN[x:i32] ADD[x, 1]")
    assert deserialize(serialize(d)).name == "f"
    prog = parse_program("ADD[1, 2]\nSUB[9, 3]")
    out = deserialize(serialize(prog))
    assert len(out) == 2
    assert out[0].op == "ADD"
    assert out[1].op == "SUB"
