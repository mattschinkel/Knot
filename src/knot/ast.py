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

class OpExpr(ExprNode):
    def __init__(self, op, children=None):
        self.op = op
        super().__init__(children or [])

    def __repr__(self):
        return f"OpExpr(op={self.op!r}, children={self.children!r})"

    def __eq__(self, other):
        if not isinstance(other, OpExpr):
            return False
        return (self.op == other.op and
                self.children == other.children)

    def __hash__(self):
        return hash((self.op, tuple(self.children)))

    def __lt__(self, other):
        return (self.op, self.children) < (other.op, other.children)

class IfExpr(ExprNode):
    def __init__(self, cond, then_branch, else_branch):
        super().__init__()
        self.cond = cond
        self.then_branch = then_branch
        self.else_branch = else_branch
        self.children = (then_branch, else_branch)

    def __repr__(self):
        return f"IfExpr(id={self.id}, cond={self.cond}, then_branch={self.then_branch}, else_branch={self.else_branch})"

    def __eq__(self, other):
        return (isinstance(other, IfExpr) and
                self.id == other.id and
                self.cond == other.cond and
                self.then_branch == other.then_branch and
                self.else_branch == other.else_branch)

    def __hash__(self):
        return hash((self.id, self.cond, self.then_branch, self.else_branch))

    def __lt__(self, other):
        return (self.id, self.cond, self.then_branch, self.else_branch) < (other.id, other.cond, other.then_branch, other.else_branch)

class CondExpr(ExprNode):
    def __init__(self, cond):
        self.cond = cond

    def __repr__(self):
        return f"CondExpr(cond={self.cond!r})"

    def __eq__(self, other):
        if not isinstance(other, CondExpr):
            return False
        return self.cond == other.cond

    def __hash__(self):
        return hash((self.cond,))

    def __lt__(self, other):
        return self.cond < other.cond
