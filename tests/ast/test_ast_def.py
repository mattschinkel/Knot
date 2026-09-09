from knot.ast import DefNode
def test_defnode_id():
    node = DefNode(id=1)
    assert node.id == 1


def test_defnode_path():
    node = DefNode(path=[1, 2, 3])
    assert node.path == [1, 2, 3]


def test_defnode_label():
    node = DefNode(label="test_label")
    assert node.label == "test_label"


def test_defnode_children():
    node = DefNode(children=[1, 2, 3])
    assert node.children == [1, 2, 3]


def test_defnode_children_only():
    node = DefNode(children=[1, 2, 3])
    assert node.children == [1, 2, 3]


def test_defnode_id():
    node = DefNode(children=[1])
    node.id = 1
    assert node.id == 1


def test_defnode_path():
    node = DefNode(children=[1])
    node.path = [1, 2, 3]
    assert node.path == [1, 2, 3]


def test_defnode_label():
    node = DefNode(children=[1])
    node.label = "test_label"
    assert node.label == "test_label"


def test_defnode_children():
    node = DefNode(children=[1, 2, 3])
    assert node.children == [1, 2, 3]
