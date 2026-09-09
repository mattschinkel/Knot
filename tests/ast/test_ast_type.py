from knot.ast import TypeNode
def test_typenode_id():
    node = TypeNode(id=1)
    assert node.id == 1


def test_typenode_path():
    node = TypeNode(path=[1, 2, 3])
    assert node.path == [1, 2, 3]


def test_typenode_label():
    node = TypeNode(label="type_label")
    assert node.label == "type_label"


def test_typenode_children():
    node = TypeNode(children=[1, 2])
    assert node.children == [1, 2]


def test_typenode_eq():
    node1 = TypeNode(id=1, path=[1, 2], label="T", children=[10])
    node2 = TypeNode(id=1, path=[1, 2], label="T", children=[10])
    assert node1 == node2


def test_typenode_hash():
    node1 = TypeNode(id=1, path=[1, 2], label="T", children=[10])
    node2 = TypeNode(id=1, path=[1, 2], label="T", children=[10])
    assert hash(node1) == hash(node2)


def test_typenode_lt():
    node1 = TypeNode(id=1, path=[1, 2], label="T", children=[10])
    node2 = TypeNode(id=2, path=[3, 4], label="U", children=[20])
    assert node1 < node2


def test_typenode_id():
    node = TypeNode(id=1)
    assert node.id == 1


def test_typenode_path():
    node = TypeNode(path=[1, 2, 3])
    assert node.path == [1, 2, 3]


def test_typenode_label():
    node = TypeNode(label="type_label")
    assert node.label == "type_label"


def test_typenode_children():
    node = TypeNode(children=[1, 2])
    assert node.children == [1, 2]


def test_typenode_eq():
    node1 = TypeNode(id=1, path=[1, 2], label="T", children=[10])
    node2 = TypeNode(id=1, path=[1, 2], label="T", children=[10])
    assert node1 == node2


def test_typenode_hash():
    node1 = TypeNode(id=1, path=[1, 2], label="T", children=[10])
    node2 = TypeNode(id=1, path=[1, 2], label="T", children=[10])
    assert hash(node1) == hash(node2)


def test_typenode_lt():
    node1 = TypeNode(id=1, path=[1, 2], label="T", children=[10])
    node2 = TypeNode(id=2, path=[3, 4], label="U", children=[20])
    assert node1 < node2
