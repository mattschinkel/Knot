def test_exprnode_init():
    node = ExprNode()
    assert node.id is None
    assert node.path is None
    assert node.label is None
    assert node.children == ()


def test_exprnode_repr():
    node = ExprNode()
    assert repr(node) == "ExprNode()"


def test_exprnode_eq():
    node1 = ExprNode()
    node2 = ExprNode()
    assert node1 == node2


def test_exprnode_hash():
    node = ExprNode()
    assert hash(node) != 0


def test_exprnode_iter():
    node = ExprNode()
    assert list(iter(node)) == []


def test_exprnode_len():
    node = ExprNode()
    assert len(node) == 0


def test_exprnode_with_children():
    node = ExprNode(children=[1, 2, 3])
    assert node.children == (1, 2, 3)


def test_exprnode_init():
    node = ExprNode()
    assert node.id is None
    assert node.path is None
    assert node.label is None
    assert node.children == ()


def test_exprnode_repr():
    node = ExprNode()
    assert repr(node) == "ExprNode()"


def test_exprnode_eq():
    node1 = ExprNode()
    node2 = ExprNode()
    assert node1 == node2


def test_exprnode_hash():
    node = ExprNode()
    assert hash(node) != 0


def test_exprnode_iter():
    node = ExprNode()
    assert list(iter(node)) == []


def test_exprnode_len():
    node = ExprNode()
    assert len(node) == 0


def test_exprnode_with_children():
    node = ExprNode(children=[1, 2, 3])
    assert node.children == (1, 2, 3)


def test_exprnode_init():
    node = ExprNode()
    assert node.id is None
    assert node.path is None
    assert node.label is None
    assert node.children == ()


def test_exprnode_repr():
    node = ExprNode()
    assert repr(node) == "ExprNode()"


def test_exprnode_eq():
    node1 = ExprNode()
    node2 = ExprNode()
    assert node1 == node2


def test_exprnode_hash():
    node = ExprNode()
    assert hash(node) != 0


def test_exprnode_iter():
    node = ExprNode()
    assert list(iter(node)) == []


def test_exprnode_len():
    node = ExprNode()
    assert len(node) == 0


def test_exprnode_with_children():
    node = ExprNode(children=[1, 2, 3])
    assert node.children == (1, 2, 3)


def test_exprnode_init():
    node = ExprNode()
    assert node.id is None
    assert node.path is None
    assert node.label is None
    assert node.children == ()


def test_exprnode_repr():
    node = ExprNode()
    assert repr(node) == "ExprNode()"


def test_exprnode_eq():
    node1 = ExprNode()
    node2 = ExprNode()
    assert node1 == node2


def test_exprnode_hash():
    node = ExprNode()
    assert hash(node) != 0


def test_exprnode_iter():
    node = ExprNode()
    assert list(iter(node)) == []


def test_exprnode_len():
    node = ExprNode()
    assert len(node) == 0


def test_exprnode_with_children():
    node = ExprNode(children=[1, 2, 3])
    assert node.children == (1, 2, 3)


def test_exprnode_init():
    node = ExprNode()
    assert node.id is None
    assert node.path is None
    assert node.label is None
    assert node.children == ()


def test_exprnode_repr():
    node = ExprNode()
    assert repr(node) == "ExprNode()"


def test_exprnode_eq():
    node1 = ExprNode()
    node2 = ExprNode()
    assert node1 == node2


def test_exprnode_hash():
    node = ExprNode()
    assert hash(node) != 0


def test_exprnode_iter():
    node = ExprNode()
    assert list(iter(node)) == []


def test_exprnode_len():
    node = ExprNode()
    assert len(node) == 0


def test_exprnode_with_children():
    node = ExprNode(children=[1, 2, 3])
    assert node.children == (1, 2, 3)
