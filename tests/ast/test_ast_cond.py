from knot.ast import IfExpr
def test_ifexpr_children():
    node = IfExpr(id=1, then_branch=..., else_branch=...)
    assert node.children == (..., ...)


def test_ifexpr_children():
    node = IfExpr()
    assert node.children == ()


def test_ifexpr_init():
    node = IfExpr(1, 2, 3)
    assert node.id == 1
    assert node.then_branch == 2
    assert node.else_branch == 3


def test_ifexpr_init():
    node = IfExpr(1, 2, 3)
    assert node.id == 1
    assert node.then_branch == 2
    assert node.else_branch == 3
    assert node.children == (2, 3)


def test_ifexpr_children():
    node = IfExpr(1, 2, 3)
    assert node.children == (2, 3)
