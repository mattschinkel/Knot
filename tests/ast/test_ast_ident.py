from golem.ast import IdentExpr
def test_identexpr_id():
    node = IdentExpr(id=1)
    assert node.id == 1


def test_identexpr_path():
    node = IdentExpr(id=1, path=[1, 2])
    assert node.path == [1, 2]


def test_identexpr_children():
    node = IdentExpr(id=1)
    assert node.children == ()


def test_identexpr_label():
    node = IdentExpr(id=1)
    assert node.label is None
