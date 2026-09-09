"""Property-style tests for AST identity, paths, and structural round-trips."""
from knot.addressing import generate_id, generate_path, reset_ids
from knot.ast import DefNode, FnExpr, IdentExpr, LitExpr, OpExpr
from knot.bin import deserialize, serialize
from knot.parser import parse_def, parse_expr


def setup_function():
    reset_ids()


def test_roundtrip():
    node = parse_expr("ADD[1, MUL[2, 3]]")
    out = deserialize(serialize(node))
    assert isinstance(out, OpExpr)
    assert out.op == "ADD"
    assert out.children[0].value == 1
    assert out.children[1].op == "MUL"


def test_id_uniqueness():
    a = generate_id()
    b = generate_id()
    c = generate_id()
    assert len({a, b, c}) == 3


def test_path_stability():
    p1 = generate_path("1.2.body")
    p2 = generate_path("1.2.body")
    assert p1 == p2
    assert p1 == (1, 2, "body")


def test_def_roundtrip_structure():
    node = parse_def("square = FN[x:i32] MUL[x, x]")
    assert isinstance(node, DefNode)
    assert node.name == "square"
    assert isinstance(node.body, FnExpr)
    assert node.body.params[0][0] == "x"


def test_lit_and_ident_stable():
    lit = LitExpr(7)
    ident = IdentExpr("x")
    assert lit.value == 7
    assert ident.id == "x"
