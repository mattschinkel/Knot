def test_node_repr():
    from knot.ast import Node
    node = Node(id=1, path=[1, 2, 3], label="test")
    # Attribute intent only - never pin exact __repr__ strings (JSON-fragile).
    assert node.id == 1
    assert node.path == [1, 2, 3]
    assert node.label == "test"
    assert "Node" in repr(node)
    assert "1" in repr(node)


def test_node_eq():
    from knot.ast import Node
    node1 = Node(id=1, path=[1, 2, 3], label="test")
    node2 = Node(id=1, path=[1, 2, 3], label="test")
    assert node1 == node2


def test_node_ne():
    from knot.ast import Node
    node1 = Node(id=1, path=[1, 2, 3], label="test")
    node2 = Node(id=2, path=[1, 2, 3], label="test")
    assert node1 != node2


def test_node_init():
    from knot.ast import Node
    node = Node(id=1, path=[1, 2, 3], label="test")
    assert node.id == 1
    assert node.path == [1, 2, 3]
    assert node.label == "test"


def test_node_attributes():
    from knot.ast import Node
    node = Node(id=1, path=[1, 2, 3], label="test")
    assert hasattr(node, 'id')
    assert hasattr(node, 'path')
    assert hasattr(node, 'label')
