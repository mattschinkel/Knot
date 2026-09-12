from golem.values import Value

from golem.values import Value

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

from golem.values import Value

from golem.values import Value

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

class MatchCase:
    """One MATCH arm: CASE[tag, body] or CASE[tag, binding, body]."""

    def __init__(self, tag, body, binding=None):
        self.tag = str(tag)
        self.body = body
        self.binding = None if binding is None else str(binding)

    def __repr__(self):
        return (
            "MatchCase("
            + repr(self.tag)
            + ", "
            + repr(self.body)
            + ", "
            + repr(self.binding)
            + ")"
        )

    def __eq__(self, other):
        return (
            isinstance(other, MatchCase)
            and self.tag == other.tag
            and self.body == other.body
            and self.binding == other.binding
        )

    def __hash__(self):
        return hash((self.tag, self.body, self.binding))


class MatchExpr(ExprNode):
    """MATCH[scrutinee, CASE[tag, body]|CASE[tag, name, body], ...] (Stage 0.5)."""

    def __init__(self, scrutinee, cases=None, id=None):
        self.scrutinee = scrutinee
        self.cases = list(cases or [])
        self.id = id

    @property
    def children(self):
        kids = [self.scrutinee]
        for c in self.cases:
            kids.append(c.body)
        return tuple(kids)

    def __repr__(self):
        return "MatchExpr(" + repr(self.scrutinee) + ", " + repr(self.cases) + ")"

    def __eq__(self, other):
        return (
            isinstance(other, MatchExpr)
            and self.scrutinee == other.scrutinee
            and self.cases == other.cases
        )

    def __hash__(self):
        return hash((self.scrutinee, tuple(self.cases)))


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
    """Function value: FN[[params], body] with optional effects/caps (Phase 3).

    AIR for effects/capabilities is not locked yet; annotations are set on the
    AST node when present so the checker can attach them to FnType.
    """

    def __init__(
        self,
        params,
        body,
        id=None,
        path=None,
        label=None,
        effects=None,
        caps=None,
    ):
        self.params = list(params or [])
        self.body = body
        self.id = id
        self.path = path or []
        self.label = label
        self.effects = effects
        self.caps = caps

    @property
    def children(self):
        return (self.body,)

    def __repr__(self):
        return "FnExpr(" + repr(self.params) + ", " + repr(self.body) + ")"

    def __eq__(self, other):
        return (
            isinstance(other, FnExpr)
            and self.params == other.params
            and self.body == other.body
            and self.effects == other.effects
            and self.caps == other.caps
        )

    def __hash__(self):
        return hash((tuple(self.params), self.body, self.effects, self.caps))


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


class ErrExpr(ExprNode):
    """First-class error value in AIR (D-FB9 / Phase 5).

    Canonical: ERR[CODE,PATH,EXPECTED,ACTUAL,FIX...]
    PATH is a list of structural segments (str|int), not authored node IDs.
    EXPECTED/ACTUAL are type name strings. FIX nodes are OpExpr suggestions.
    """

    def __init__(
        self,
        code,
        path=None,
        expected=None,
        actual=None,
        fixes=None,
        id=None,
        label=None,
    ):
        self.code = str(code)
        self.path = list(path or [])
        self.expected = expected  # str type name
        self.actual = actual
        self.fixes = list(fixes or [])
        self.id = id
        self.label = label

    @property
    def children(self):
        return tuple(self.fixes)

    def __repr__(self):
        return (
            "ErrExpr("
            + repr(self.code)
            + ", "
            + repr(self.path)
            + ", "
            + repr(self.expected)
            + ", "
            + repr(self.actual)
            + ", "
            + repr(self.fixes)
            + ")"
        )

    def __eq__(self, other):
        return (
            isinstance(other, ErrExpr)
            and self.code == other.code
            and self.path == other.path
            and self.expected == other.expected
            and self.actual == other.actual
            and self.fixes == other.fixes
        )

    def __hash__(self):
        return hash(
            (
                self.code,
                tuple(self.path),
                self.expected,
                self.actual,
                tuple(self.fixes),
            )
        )

    def __str__(self):
        return repr(self)


class InlineCase:
    """One CASE[in, out] pair."""

    def __init__(self, inp, out):
        self.inp = inp
        self.out = out

    def __repr__(self):
        return "InlineCase(" + repr(self.inp) + ", " + repr(self.out) + ")"

    def __eq__(self, other):
        return (
            isinstance(other, InlineCase)
            and self.inp == other.inp
            and self.out == other.out
        )

    def __hash__(self):
        return hash((self.inp, self.out))


class InlineTest(ExprNode):
    """Inline test: TEST[name,CASE[in,out],...] (Phase 7)."""

    def __init__(self, name, cases=None, id=None, path=None, label=None):
        self.name = str(name)
        self.cases = list(cases or [])
        self.id = id
        self.path = path or []
        self.label = label

    @property
    def children(self):
        return tuple(c.inp for c in self.cases) + tuple(c.out for c in self.cases)

    def __repr__(self):
        return "InlineTest(" + repr(self.name) + ", " + repr(self.cases) + ")"

    def __eq__(self, other):
        return (
            isinstance(other, InlineTest)
            and self.name == other.name
            and self.cases == other.cases
        )

    def __hash__(self):
        return hash((self.name, tuple(self.cases)))


class PropertyDecl(ExprNode):
    """Property: PROPERTY[name,[[x:T,...],body]] (Phase 7)."""

    def __init__(self, name, params=None, body=None, id=None, path=None, label=None):
        self.name = str(name)
        self.params = list(params or [])  # (name, type_str)
        self.body = body
        self.id = id
        self.path = path or []
        self.label = label

    @property
    def children(self):
        return (self.body,) if self.body is not None else ()

    def __repr__(self):
        return (
            "PropertyDecl("
            + repr(self.name)
            + ", "
            + repr(self.params)
            + ", "
            + repr(self.body)
            + ")"
        )

    def __eq__(self, other):
        return (
            isinstance(other, PropertyDecl)
            and self.name == other.name
            and self.params == other.params
            and self.body == other.body
        )

    def __hash__(self):
        return hash((self.name, tuple(self.params), self.body))


class ExportList(ExprNode):
    """EXPORT[n1, n2, ...] inside MODULE."""

    def __init__(self, names=None, id=None):
        self.names = [str(n) for n in (names or [])]
        self.id = id

    @property
    def children(self):
        return ()

    def __repr__(self):
        return "ExportList(" + repr(self.names) + ")"

    def __eq__(self, other):
        return isinstance(other, ExportList) and self.names == other.names

    def __hash__(self):
        return hash(tuple(self.names))


class ModuleDecl(ExprNode):
    """MODULE[name, items..., EXPORT[...]] (Phase 8)."""

    def __init__(self, name, body=None, exports=None, version="0", id=None):
        self.name = str(name)
        self.body = list(body or [])
        self.exports = list(exports or [])
        self.version = str(version)
        self.id = id

    @property
    def children(self):
        return tuple(self.body)

    def __repr__(self):
        return (
            "ModuleDecl("
            + repr(self.name)
            + ", "
            + repr(self.body)
            + ", "
            + repr(self.exports)
            + ")"
        )

    def __eq__(self, other):
        return (
            isinstance(other, ModuleDecl)
            and self.name == other.name
            and self.body == other.body
            and self.exports == other.exports
            and self.version == other.version
        )

    def __hash__(self):
        return hash((self.name, tuple(self.body), tuple(self.exports), self.version))


class ImportDecl(ExprNode):
    """IMPORT[mod, name...] — empty names means all exports."""

    def __init__(self, module, names=None, id=None):
        self.module = str(module)
        self.names = [str(n) for n in (names or [])]
        self.id = id

    @property
    def children(self):
        return ()

    def __repr__(self):
        return "ImportDecl(" + repr(self.module) + ", " + repr(self.names) + ")"

    def __eq__(self, other):
        return (
            isinstance(other, ImportDecl)
            and self.module == other.module
            and self.names == other.names
        )

    def __hash__(self):
        return hash((self.module, tuple(self.names)))


class DependsDecl(ExprNode):
    """DEPENDS[mod, version] or DEPENDS[mod, version, CAPS[...]]."""

    def __init__(self, module, version="0", caps=None, id=None):
        self.module = str(module)
        self.version = str(version)
        self.caps = list(caps or [])  # capability name strings
        self.id = id

    @property
    def children(self):
        return ()

    def __repr__(self):
        return (
            "DependsDecl("
            + repr(self.module)
            + ", "
            + repr(self.version)
            + ", "
            + repr(self.caps)
            + ")"
        )

    def __eq__(self, other):
        return (
            isinstance(other, DependsDecl)
            and self.module == other.module
            and self.version == other.version
            and self.caps == other.caps
        )

    def __hash__(self):
        return hash((self.module, self.version, tuple(self.caps)))


class ModelDecl(ExprNode):
    """MODEL[name,IN[T],OUT[U],CONF[bool],EFFECTS[...]] (Phase 10)."""

    def __init__(self, name, in_type, out_type, confidence=True, effects=None, id=None):
        self.name = str(name)
        self.in_type = str(in_type)
        self.out_type = str(out_type)
        self.confidence = bool(confidence)
        self.effects = list(effects or [])
        self.id = id

    @property
    def children(self):
        return ()

    def __repr__(self):
        return (
            "ModelDecl("
            + repr(self.name)
            + ", "
            + repr(self.in_type)
            + ", "
            + repr(self.out_type)
            + ", "
            + repr(self.confidence)
            + ", "
            + repr(self.effects)
            + ")"
        )

    def __eq__(self, other):
        return (
            isinstance(other, ModelDecl)
            and self.name == other.name
            and self.in_type == other.in_type
            and self.out_type == other.out_type
            and self.confidence == other.confidence
            and self.effects == other.effects
        )

    def __hash__(self):
        return hash(
            (self.name, self.in_type, self.out_type, self.confidence, tuple(self.effects))
        )


class ToolDecl(ExprNode):
    """TOOL[name,IN[T],OUT[U],EFFECTS[...]] (Phase 10)."""

    def __init__(self, name, in_type, out_type, effects=None, id=None):
        self.name = str(name)
        self.in_type = str(in_type)
        self.out_type = str(out_type)
        self.effects = list(effects or [])
        self.id = id

    @property
    def children(self):
        return ()

    def __repr__(self):
        return (
            "ToolDecl("
            + repr(self.name)
            + ", "
            + repr(self.in_type)
            + ", "
            + repr(self.out_type)
            + ", "
            + repr(self.effects)
            + ")"
        )

    def __eq__(self, other):
        return (
            isinstance(other, ToolDecl)
            and self.name == other.name
            and self.in_type == other.in_type
            and self.out_type == other.out_type
            and self.effects == other.effects
        )

    def __hash__(self):
        return hash((self.name, self.in_type, self.out_type, tuple(self.effects)))


class InvokeExpr(ExprNode):
    """INVOKE[name,arg...] — call registered MODEL or TOOL (Phase 10)."""

    def __init__(self, name, args=None, id=None):
        self.name = str(name)
        self.args = list(args or [])
        self.id = id

    @property
    def children(self):
        return tuple(self.args)

    def __repr__(self):
        return "InvokeExpr(" + repr(self.name) + ", " + repr(self.args) + ")"

    def __eq__(self, other):
        return (
            isinstance(other, InvokeExpr)
            and self.name == other.name
            and self.args == other.args
        )

    def __hash__(self):
        return hash((self.name, tuple(self.args)))


class ParExpr(ExprNode):
    """PAR[e1,e2,...] — dataflow-independent branches (Phase 11)."""

    def __init__(self, branches=None, id=None):
        self.branches = list(branches or [])
        self.id = id

    @property
    def children(self):
        return tuple(self.branches)

    def __repr__(self):
        return "ParExpr(" + repr(self.branches) + ")"

    def __eq__(self, other):
        return isinstance(other, ParExpr) and self.branches == other.branches

    def __hash__(self):
        return hash(tuple(self.branches))


class SeqExpr(ExprNode):
    """SEQ[e1,e2,...] — explicit sequencing (Phase 11)."""

    def __init__(self, steps=None, id=None):
        self.steps = list(steps or [])
        self.id = id

    @property
    def children(self):
        return tuple(self.steps)

    def __repr__(self):
        return "SeqExpr(" + repr(self.steps) + ")"

    def __eq__(self, other):
        return isinstance(other, SeqExpr) and self.steps == other.steps

    def __hash__(self):
        return hash(tuple(self.steps))


class RefExpr(ExprNode):
    """REF[region,expr] — place value in a named region (Phase 11)."""

    def __init__(self, region, expr, id=None):
        self.region = str(region)
        self.expr = expr
        self.id = id

    @property
    def children(self):
        return (self.expr,)

    def __repr__(self):
        return "RefExpr(" + repr(self.region) + ", " + repr(self.expr) + ")"

    def __eq__(self, other):
        return (
            isinstance(other, RefExpr)
            and self.region == other.region
            and self.expr == other.expr
        )

    def __hash__(self):
        return hash((self.region, self.expr))


class DerefExpr(ExprNode):
    """DEREF[expr] — unwrap RegionVal (Phase 11)."""

    def __init__(self, expr, id=None):
        self.expr = expr
        self.id = id

    @property
    def children(self):
        return (self.expr,)

    def __repr__(self):
        return "DerefExpr(" + repr(self.expr) + ")"

    def __eq__(self, other):
        return isinstance(other, DerefExpr) and self.expr == other.expr

    def __hash__(self):
        return hash(self.expr)


class UnsafeExpr(ExprNode):
    """UNSAFE[CAPS[cap...],body] — capability-gated escape (Phase 11)."""

    def __init__(self, caps=None, body=None, id=None):
        self.caps = list(caps or [])
        self.body = body
        self.id = id

    @property
    def children(self):
        return (self.body,) if self.body is not None else ()

    def __repr__(self):
        return "UnsafeExpr(" + repr(self.caps) + ", " + repr(self.body) + ")"

    def __eq__(self, other):
        return (
            isinstance(other, UnsafeExpr)
            and self.caps == other.caps
            and self.body == other.body
        )

    def __hash__(self):
        return hash((tuple(self.caps), self.body))


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
