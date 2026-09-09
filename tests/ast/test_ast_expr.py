from knot.ast import ExprNode


def test_exprnode_id():
    node = ExprNode(id=1)
    assert node.id == 1


def test_exprnode_path():
    node = ExprNode(id=1, path=[1, 2, 3])
    assert node.path == [1, 2, 3]


def test_exprnode_label():
    node = ExprNode(id=1, label="hello")
    assert node.label == "hello"


def test_exprnode_children_default_empty():
    node = ExprNode(id=1)
    assert node.children == ()


def test_exprnode_eq_by_id():
    assert ExprNode(id=1) == ExprNode(id=1)
    assert ExprNode(id=1) != ExprNode(id=2)


def test_exprnode_lt_by_id():
    assert ExprNode(id=1) < ExprNode(id=2)
