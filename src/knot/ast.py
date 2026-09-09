from knot.values import Value

class Node(Value):
    """Base AST node class."""

    def __init__(self, id=None, path=None, label=None):
        self.id = id
        self.path = path or []
        self.label = label

    def __repr__(self):
        return f"Node(id={self.id!r}, path={self.path!r}, label={self.label!r})"

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return (self.id == other.id and
                self.path == other.path and
                self.label == other.label)

    def __ne__(self, other):
        return not self.__eq__(other)
