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

class ExprNode:
    def __init__(self, children=None):
        self.children = children or []
        self.id = None
        self.path = None
        self.label = None

    def __repr__(self):
        return f"ExprNode(id={self.id}, path={self.path}, label={self.label}, children={self.children})"

    def __eq__(self, other):
        return (isinstance(other, ExprNode) and
                self.id == other.id and
                self.path == other.path and
                self.label == other.label and
                self.children == other.children)

    def __hash__(self):
        return hash((self.id, self.path, self.label, tuple(self.children)))

    def __lt__(self, other):
        return (self.id, self.path, self.label, self.children) < (other.id, other.path, other.label, other.children)

class TypeNode(Value):
    """A type node in the AST."""
    def __init__(self, id=None, path=None, label=None, children=None):
        self.id = id
        self.path = path
        self.label = label
        self.children = children

    def __repr__(self):
        return f"TypeNode(id={self.id!r}, path={self.path!r}, label={self.label!r}, children={self.children!r})"

    def __eq__(self, other):
        if not isinstance(other, TypeNode):
            return False
        return (self.id == other.id and
                self.path == other.path and
                self.label == other.label and
                self.children == other.children)

    def __hash__(self):
        return hash((self.id, tuple(self.path), self.label, tuple(self.children)))

    def __lt__(self, other):
        if not isinstance(other, TypeNode):
            return False
        return (self.id < other.id or
                (self.id == other.id and self.path < other.path) or
                (self.id == other.id and self.path == other.path and self.label < other.label) or
                (self.id == other.id and self.path == other.path and self.label == other.label and self.children < other.children))

    def __str__(self):
        return f"Type({self.label})"

class DefNode(ExprNode):
    def __init__(self, children):
        self.children = children
        self.id = None
        self.path = None
        self.label = None

    def __repr__(self):
        return f"DefNode(id={self.id}, path={self.path}, label={self.label}, children={self.children})"

    def __eq__(self, other):
        if not isinstance(other, DefNode):
            return False
        return (self.id == other.id and self.path == other.path and 
                self.label == other.label and self.children == other.children)

    def __hash__(self):
        return hash((self.id, self.path, self.label, tuple(self.children)))

    def __lt__(self, other):
        return (self.id, self.path, self.label, self.children) < (other.id, other.path, other.label, other.children)
