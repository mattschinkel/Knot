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
    def __init__(self, id, path=None, label=None):
        self.id = id
        self.path = path or []
        self.label = label

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id})'

    def __eq__(self, other):
        if isinstance(other, ExprNode):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    @property
    def children(self):
        return ()

    def __lt__(self, other):
        return self.id < other.id

    def __str__(self):
        return str(self.id)

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
    """A binding: name = expr (phase1_spec Def)."""

    def __init__(self, name, body, id=None, path=None, label=None):
        self.name = name
        self.body = body
        self.id = id
        self.path = path or []
        self.label = label

    @property
    def children(self):
        return (self.body,)

    def __repr__(self):
        return "DefNode(" + repr(self.name) + ", " + repr(self.body) + ")"

    def __eq__(self, other):
        return (isinstance(other, DefNode)
                and self.name == other.name
                and self.body == other.body)

    def __hash__(self):
        return hash((self.name, self.body))


class OpExpr(ExprNode):
    def __init__(self, op, children=None, id=None, path=None, label=None):
        self.op = op
        self._kids = list(children or [])
        super().__init__(id if id is not None else 0, path, label)

    @property
    def children(self):
        return self._kids

    def __repr__(self):
        return "OpExpr(op=" + repr(self.op) + ", children=" + repr(self.children) + ")"

    def __eq__(self, other):
        if not isinstance(other, OpExpr):
            return False
        return self.op == other.op and list(self.children) == list(other.children)

    def __hash__(self):
        return hash((self.op, tuple(self.children)))

class IfExpr(ExprNode):
    def __init__(self, cond, then_branch, else_branch):
        super().__init__(id=1)
        self.cond = cond
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return f"IfExpr(cond={self.cond}, then_branch={self.then_branch}, else_branch={self.else_branch})"

    def __eq__(self, other):
        if not isinstance(other, IfExpr):
            return False
        return (self.cond == other.cond and
                self.then_branch == other.then_branch and
                self.else_branch == other.else_branch)

    def __hash__(self):
        return hash((self.cond, self.then_branch, self.else_branch))

    def __lt__(self, other):
        return self.cond < other.cond

    @property
    def children(self):
        return (self.then_branch, self.else_branch)

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

class MatchExpr(ExprNode):
    __slots__ = ('pattern', 'body')

    def __init__(self, pattern=None, body=None):
        self.pattern = pattern
        self.body = body

    def __repr__(self):
        return f'MatchExpr(pattern={self.pattern!r}, body={self.body!r})'

    def __eq__(self, other):
        if not isinstance(other, MatchExpr):
            return False
        return (self.pattern == other.pattern and
                self.body == other.body)

    def __hash__(self):
        return hash((self.pattern, self.body))

    def __lt__(self, other):
        if not isinstance(other, MatchExpr):
            return False
        if self.pattern is None and other.pattern is None:
            return self.body is not None and other.body is not None
        if self.pattern is None:
            return True
        if other.pattern is None:
            return False
        return self.pattern < other.pattern

    @property
    def children(self):
        return (self.pattern, self.body)

class LetExpr(ExprNode):
    __slots__ = ('id', 'path', 'label')

    def __init__(self, id, path, label=None):
        super().__init__(id=id, path=path, label=label)
        self.id = id
        self.path = path
        self.label = label

    def __repr__(self):
        return f"LetExpr(id={self.id!r}, path={self.path!r}, label={self.label!r})"

    def __eq__(self, other):
        if not isinstance(other, LetExpr):
            return False
        return (self.id == other.id and self.path == other.path and self.label == other.label)

    def __hash__(self):
        return hash((self.id, self.path, self.label))

    def __lt__(self, other):
        return (self.id, self.path, self.label) < (other.id, other.path, other.label)

    @property
    def children(self):
        return []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

class WithExpr(ExprNode):
    def __init__(self, id, path=None, label=None):
        super().__init__(id, path=path, label=label)

    def __repr__(self):
        return f"WithExpr(id={self.id})"

    def __eq__(self, other):
        if not isinstance(other, WithExpr):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __lt__(self, other):
        return self.id < other.id

    @property
    def children(self):
        return ()

class FieldAccess(ExprNode):
    def __init__(self, id, path=None, label=None, field_name=None):
        self.id = id
        self.path = path or []
        self.label = label
        self.field_name = field_name

    def __repr__(self):
        return f"FieldAccess(id={self.id}, path={self.path}, label={self.label}, field_name={self.field_name})"

    def __eq__(self, other):
        return (isinstance(other, FieldAccess) and
                self.id == other.id and
                self.path == other.path and
                self.label == other.label and
                self.field_name == other.field_name)

    def __hash__(self):
        return hash((self.id, self.path, self.label, self.field_name))

    def __lt__(self, other):
        return (isinstance(other, FieldAccess) and
                self.id < other.id)

    @property
    def children(self):
        return ()

class FnExpr(ExprNode):
    """Function value: FN[params...] body."""

    def __init__(self, params, body, id=None, path=None, label=None):
        self.params = list(params or [])
        self.body = body
        self.id = id
        self.path = path or []
        self.label = label

    @property
    def children(self):
        return (self.body,)

    def __repr__(self):
        return "FnExpr(" + repr(self.params) + ", " + repr(self.body) + ")"

    def __eq__(self, other):
        return (isinstance(other, FnExpr)
                and self.params == other.params
                and self.body == other.body)

    def __hash__(self):
        return hash((tuple(self.params), self.body))


class CallExpr(ExprNode):
    def __init__(self, fn, args=None):
        self.fn = fn
        self.args = args or []
        super().__init__(id=1)

    def __repr__(self):
        return f"CallExpr(fn={self.fn!r}, args={self.args!r})"

    def __eq__(self, other):
        if not isinstance(other, CallExpr):
            return False
        return (self.fn == other.fn and
                self.args == other.args)

    def __hash__(self):
        return hash((self.fn, tuple(self.args)))

    def __lt__(self, other):
        return self.fn < other.fn

    @property
    def children(self):
        return (self.fn, tuple(self.args))

class HoleExpr(ExprNode):
    def __init__(self, id, path=None, label=None):
        self.id = id
        self.path = path or []
        self.label = label
        self._children = tuple()

    def __repr__(self):
        return f"HoleExpr(id={self.id!r}, path={self.path!r}, label={self.label!r}, children={self._children!r})"

    def __eq__(self, other):
        if not isinstance(other, HoleExpr):
            return False
        return (self.id == other.id and self.path == other.path and self.label == other.label)

    def __hash__(self):
        return hash((self.id, tuple(self.path), self.label))

    def __lt__(self, other):
        if not isinstance(other, HoleExpr):
            return False
        return (self.id < other.id or (self.id == other.id and self.path < other.path))

    def __str__(self):
        return f"HoleExpr(id={self.id}, path={self.path}, label={self.label}, children={self._children})"

    @property
    def children(self):
        return self._children

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

class LitExpr(ExprNode):
    def __init__(self, value):
        self.value = value

    @property
    def id(self):
        return self.value

    @property
    def path(self):
        return []

    @property
    def label(self):
        return None

    @property
    def children(self):
        return (self.value,)

    def __repr__(self):
        return f'LitExpr({self.value})'

    def __eq__(self, other):
        if not isinstance(other, LitExpr):
            return False
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def __lt__(self, other):
        if not isinstance(other, LitExpr):
            return False
        return self.value < other.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'LitExpr({self.value})'

class TypedLit(ExprNode):
    """Literal with an explicit type annotation: 2:i32, 10:meters (phase1_spec)."""

    def __init__(self, value, type_name, id=None, path=None, label=None):
        self.value = value
        self.type_name = type_name
        self.id = id
        self.path = path or []
        self.label = label

    @property
    def children(self):
        return ()

    def __repr__(self):
        return "TypedLit(" + repr(self.value) + ", " + repr(self.type_name) + ")"

    def __eq__(self, other):
        return (isinstance(other, TypedLit)
                and self.value == other.value
                and self.type_name == other.type_name)

    def __hash__(self):
        return hash((self.value, self.type_name))


class IdentExpr(ExprNode):
    def __init__(self, id, path=None):
        self.id = id
        self.path = path or []
        self.label = None

    @property
    def children(self):
        return ()

class UnitExpr(ExprNode):
    def __init__(self, id, path=None, label=None):
        super().__init__(id, path, label)

    @property
    def children(self):
        return ()

    def __repr__(self):
        return f'UnitExpr({self.id})'

    def __eq__(self, other):
        if not isinstance(other, UnitExpr):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __lt__(self, other):
        if not isinstance(other, UnitExpr):
            return False
        return self.id < other.id

    def __str__(self):
        return str(self.id)
