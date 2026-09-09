from knot.ast import ExprNode
def test_exprnode_id():
    node = ExprNode(id=1)
    assert node.id == 1

def test_exprnode_path():
    node = ExprNode(path=[1, 2, 3])
    assert node.path == [1, 2, 3]

def test_exprnode_label():
    node = ExprNode(label="hello")
    assert node.label == "hello"

def test_exprnode_children():
    node = ExprNode(children=[1, 2])
    assert node.children == [1, 2]


def test_exprnode_id():
    node = ExprNode(children=[1])
    assert node.id is None

def test_exprnode_path():
    node = ExprNode(children=[1])
    assert node.path is None

def test_exprnode_label():
    node = ExprNode(children=[1])
    assert node.label is None

def test_exprnode_children():
    node = ExprNode(children=[1, 2])
    assert node.children == [1, 2]
