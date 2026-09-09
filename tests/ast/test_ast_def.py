from knot.ast import DefNode, LitExpr


def test_defnode_name_and_body():
    body = LitExpr(1)
    node = DefNode("x", body)
    assert node.name == "x"
    assert node.body is body
    assert node.children == (body,)


def test_defnode_optional_meta():
    body = LitExpr(1)
    node = DefNode("x", body, id=7, path=["a"], label="L")
    assert node.id == 7
    assert node.path == ["a"]
    assert node.label == "L"


def test_defnode_eq():
    a = DefNode("x", LitExpr(1))
    b = DefNode("x", LitExpr(1))
    c = DefNode("y", LitExpr(1))
    assert a == b
    assert a != c
