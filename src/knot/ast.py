from knot.values import Value

from knot.values import Value

class Node(Value):
    def __init__(self, id=None, path=None, label=None, children=()):
        self.id = id
        self.path = path
        self.label = label
        self.children = children

    def __repr__(self):
        return f"Node(id={self.id!r}, path={self.path!r}, label={self.label!r}, children={self.children!r})"

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return (self.id == other.id and
                self.path == other.path and
                self.label == other.label and
                self.children == other.children)

    def __hash__(self):
        return hash((self.id, self.path, self.label, self.children))

    def __iter__(self):
        return iter(self.children)

    def __len__(self):
        return len(self.children)

from knot.values import Value

from knot.values import Value

class ExprNode(Value):
    def __init__(self, children=()):
        self.id = None
        self.path = None
        self.label = None
        self.children = children

    def __repr__(self):
        return f"ExprNode({self.children!r})"

    def __eq__(self, other):
        if not isinstance(other, ExprNode):
            return False
        return self.children == other.children

    def __hash__(self):
        return hash(self.children)

    def __iter__(self):
        return iter(self.children)

    def __len__(self):
        return len(self.children)
