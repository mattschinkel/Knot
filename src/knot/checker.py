"""Type checker helpers (Phase 2).

Type errors are values (spec D4): returned, never raised.
"""

from __future__ import annotations

from dataclasses import dataclass

from .ast import (
    CallExpr, DefNode, ErrExpr, FnExpr, HoleExpr, IdentExpr, IfExpr, LitExpr, OpExpr,
    TypedLit, UnitExpr,
)
from .env import Env
from .errors import StructuredError
from .types import (
    Type, ANY, BOOL, I32, I64, F32, F64, STRING, BYTES, UNIT, NEVER, FnType,
    ListType, SetType, RecordType, TupleType, MapType, subtype, unify,
)
from .values import ErrorVal, Value


@dataclass(frozen=True)
class TypeErrorVal(Value):
    """A type-check error as a value (message + structural path)."""

    message: str
    path: tuple = ()

    @property
    def type(self):
        return NEVER

    def to_error_val(self) -> ErrorVal:
        node = ".".join(str(p) for p in self.path) if self.path else None
        return ErrorVal(StructuredError(kind="type", node=node, message=self.message))

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return "TypeErrorVal(message=" + repr(self.message) + ", path=" + repr(self.path) + ")"


def type_error(message: str, path: tuple = ()) -> TypeErrorVal:
    """Build a TypeErrorVal for a type-check failure at `path`."""
    return TypeErrorVal(message=message, path=tuple(path))


_BASE_BY_NAME = {
    "i32": I32, "i64": I64, "f32": F32, "f64": F64,
    "bool": BOOL, "string": STRING, "bytes": BYTES, "unit": UNIT,
    "never": NEVER, "any": ANY,
}

_NUMERIC = frozenset({I32, I64, F32, F64})
_ARITH_OPS = frozenset({"ADD", "SUB", "MUL", "DIV", "MOD"})
_UNARY_OPS = frozenset({"NEG", "NOT"})
_COMPARE_OPS = frozenset({"EQ", "NE", "LT", "LE", "GT", "GE", "AND", "OR"})
_COLLECTION_OPS = frozenset({"LEN", "AT", "APPEND", "CONCAT", "MAP", "FILTER"})


def _lit_type(value: object) -> Type | TypeErrorVal:
    if isinstance(value, bool):
        return BOOL
    if isinstance(value, int):
        return I32
    if isinstance(value, float):
        return F64
    if isinstance(value, str):
        return STRING
    if isinstance(value, (bytes, bytearray)):
        return BYTES
    if value is None or value == ():
        return UNIT
    return type_error("unsupported literal", ())


def _resolve_type_name(name: str) -> Type | TypeErrorVal:
    """Resolve a typed-lit type string (i32 or f64@meters base part)."""
    base = name.split("@", 1)[0]
    t = _BASE_BY_NAME.get(base)
    if t is None:
        return type_error("unknown type " + repr(name), ())
    return t


def check_binary_op(op: str, t1: Type, t2: Type) -> Type | TypeErrorVal:
    """Type rule for binary kernel ops (Phase 2 T6)."""
    if op not in _ARITH_OPS:
        return type_error("unknown binary op " + repr(op), ())
    if t1 not in _NUMERIC or t2 not in _NUMERIC:
        return type_error("binary " + op + " requires numeric types", ())
    if t1 != t2:
        return type_error("binary " + op + " operand type mismatch", ())
    return t1


def check_unary_op(op: str, t: Type) -> Type | TypeErrorVal:
    """Type rule for unary ops: NEG, NOT."""
    if op == "NEG":
        if t not in _NUMERIC:
            return type_error("NEG requires numeric type", ())
        return t
    if op == "NOT":
        if t != BOOL:
            return type_error("NOT requires BOOL type", ())
        return t
    return type_error("unknown unary op " + repr(op), ())


def check_compare_op(op: str, t1: Type, t2: Type) -> Type | TypeErrorVal:
    """Comparison and logic ops: EQ NE LT LE GT GE AND OR -> Bool."""
    if op in ("EQ", "NE"):
        if t1 != t2:
            return type_error(op + " operand type mismatch", ())
        return BOOL
    if op in ("LT", "LE", "GT", "GE"):
        if t1 not in _NUMERIC or t2 not in _NUMERIC:
            return type_error(op + " requires numeric types", ())
        if t1 != t2:
            return type_error(op + " operand type mismatch", ())
        return BOOL
    if op in ("AND", "OR"):
        if t1 != BOOL or t2 != BOOL:
            return type_error(op + " requires BOOL types", ())
        return BOOL
    return type_error("unknown compare op " + repr(op), ())


def _is_bare_hole(expr: object) -> bool:
    return isinstance(expr, HoleExpr) and (expr.label is None or expr.label == "")


def _infer_binary_operands(
    left: object,
    right: object,
    env: Env | None,
    expected: Type | None,
) -> tuple[Type | TypeErrorVal, Type | TypeErrorVal]:
    """Infer binary operands with hole constraint propagation (Phase 4 D3).

    Concrete operands are inferred without a sibling expected type so existing
    op error messages stay accurate; bare holes adopt the other side (or
    ``expected`` when both are holes / AND-OR BOOL).
    """
    if expected is BOOL and not _is_bare_hole(left) and not _is_bare_hole(right):
        return (
            infer_type(left, env, expected=BOOL),
            infer_type(right, env, expected=BOOL),
        )
    if _is_bare_hole(left) and not _is_bare_hole(right):
        t2 = infer_type(right, env)
        if isinstance(t2, TypeErrorVal):
            return t2, t2
        t1 = infer_type(left, env, expected=t2)
        return t1, t2
    if _is_bare_hole(right) and not _is_bare_hole(left):
        t1 = infer_type(left, env)
        if isinstance(t1, TypeErrorVal):
            return t1, t1
        t2 = infer_type(right, env, expected=t1)
        return t1, t2
    if _is_bare_hole(left) and _is_bare_hole(right):
        t1 = infer_type(left, env, expected=expected)
        t2 = infer_type(right, env, expected=expected)
        return t1, t2
    return infer_type(left, env), infer_type(right, env)


def infer_type(
    expr: object,
    env: Env | None = None,
    expected: Type | None = None,
) -> Type | TypeErrorVal:
    """Infer the type of a kernel AST expression.

    ``expected`` (Phase 4) is an optional bidirectional check type. Bare holes
    adopt it; other nodes unify with it when both sides are concrete.
    """
    if isinstance(expr, LitExpr):
        got = _lit_type(expr.value)
        return _meet_expected(got, expected)
    if isinstance(expr, TypedLit):
        got = _resolve_type_name(expr.type_name)
        if isinstance(got, TypeErrorVal):
            return got
        return _meet_expected(got, expected)
    if isinstance(expr, UnitExpr):
        return _meet_expected(UNIT, expected)
    if isinstance(expr, IdentExpr):
        ctx = env if env is not None else Env()
        name = expr.id if isinstance(expr.id, str) else str(expr.id)
        found = ctx.lookup(name)
        if found is None:
            return type_error("unbound identifier " + repr(name), tuple(expr.path or ()))
        return _meet_expected(found, expected)
    if isinstance(expr, DefNode):
        return infer_def(expr, env)
    if isinstance(expr, HoleExpr):
        return infer_hole(expr, env, expected=expected)
    if isinstance(expr, ErrExpr):
        # First-class error value; type is never (flows anywhere).
        for fix in expr.fixes:
            from .repairs import validate_fix

            if not validate_fix(fix):
                return type_error("ERR fix has invalid shape", ())
        return NEVER
    if isinstance(expr, FnExpr) or isinstance(expr, CallExpr):
        return infer_fn(expr, env)
    if isinstance(expr, IfExpr):
        return infer_if(expr, env, expected=expected)
    from .ast import DerefExpr, ParExpr, RefExpr, SeqExpr, UnsafeExpr
    from .concurrency import infer_par_type, infer_ref_type, infer_seq_type

    if isinstance(expr, ParExpr):
        branch_ts = []
        for b in expr.branches:
            t = infer_type(b, env)
            if isinstance(t, TypeErrorVal):
                return t
            branch_ts.append(t)
        return _meet_expected(infer_par_type(branch_ts), expected)
    if isinstance(expr, SeqExpr):
        step_ts = []
        for s in expr.steps:
            t = infer_type(s, env)
            if isinstance(t, TypeErrorVal):
                return t
            step_ts.append(t)
        return _meet_expected(infer_seq_type(step_ts), expected)
    if isinstance(expr, RefExpr):
        inner = infer_type(expr.expr, env)
        if isinstance(inner, TypeErrorVal):
            return inner
        return _meet_expected(infer_ref_type(inner, expr.region), expected)
    if isinstance(expr, DerefExpr):
        from .types import RegionType

        t = infer_type(expr.expr, env)
        if isinstance(t, TypeErrorVal):
            return t
        if isinstance(t, RegionType):
            return _meet_expected(t.inner, expected)
        return type_error("DEREF expects RegionType", ())
    if isinstance(expr, UnsafeExpr):
        return infer_type(expr.body, env, expected=expected)
    from .ast import MatchExpr

    if isinstance(expr, MatchExpr):
        st = infer_type(expr.scrutinee, env)
        if isinstance(st, TypeErrorVal):
            return st
        if not expr.cases:
            return type_error("MATCH needs cases", ())
        result = None
        for case in expr.cases:
            bt = infer_type(case.body, env)
            if isinstance(bt, TypeErrorVal):
                return bt
            if result is None:
                result = bt
            else:
                u = unify(result, bt)
                if u is None:
                    return type_error("MATCH branch mismatch", ())
                result = u
        return _meet_expected(result, expected)
    if isinstance(expr, OpExpr):
        kids = list(expr.children or [])
        if expr.op in ("IF", "COND"):
            return infer_if(expr, env, expected=expected)
        if expr.op in ("GET", "SET", "FIELD"):
            return _infer_access_op(expr, env)
        if expr.op in _COLLECTION_OPS or expr.op in (
            "LIST",
            "SLICE",
            "CODEPOINT",
            "FROM_CODEPOINT",
            "MAP_NEW",
            "MAP_GET",
            "MAP_SET",
            "RECORD",
            "SUM",
            "TAG",
            "PAYLOAD",
            "FS_READ",
            "FS_WRITE",
            "PRINT",
            "BYTES_FROM_STRING",
            "STRING_FROM_BYTES",
        ):
            if expr.op == "LIST":
                from .types import ListType

                if not kids:
                    return _meet_expected(ListType(I32), expected)
                et = infer_type(kids[0], env)
                if isinstance(et, TypeErrorVal):
                    return et
                for k in kids[1:]:
                    t = infer_type(k, env)
                    if isinstance(t, TypeErrorVal):
                        return t
                    if unify(et, t) is None:
                        return type_error("LIST elem mismatch", ())
                return _meet_expected(ListType(et), expected)
            if expr.op == "MAP_NEW":
                from .types import MapType

                return _meet_expected(MapType(STRING, I32), expected)
            if expr.op in _COLLECTION_OPS:
                return _infer_collection_op(expr, env)
            # other runtime ops: soft ANY / concrete where easy
            types = []
            for k in kids:
                t = infer_type(k, env)
                if isinstance(t, TypeErrorVal):
                    return t
                types.append(t)
            if expr.op == "SLICE" and types:
                return _meet_expected(types[0], expected)
            if expr.op == "CODEPOINT":
                return _meet_expected(I32, expected)
            if expr.op == "FROM_CODEPOINT":
                return _meet_expected(STRING, expected)
            if expr.op == "TAG":
                return _meet_expected(STRING, expected)
            if expr.op == "FS_READ":
                return _meet_expected(BYTES, expected)
            if expr.op in ("FS_WRITE", "PRINT"):
                return _meet_expected(UNIT, expected)
            if expr.op == "BYTES_FROM_STRING":
                return _meet_expected(BYTES, expected)
            if expr.op == "STRING_FROM_BYTES":
                return _meet_expected(STRING, expected)
            if types:
                return _meet_expected(types[-1], expected)
            from .types import ANY

            return _meet_expected(ANY, expected)
        kids = list(expr.children or [])
        if expr.op in ("IF", "COND"):
            return infer_if(expr, env, expected=expected)
        if expr.op in ("GET", "SET", "FIELD"):
            return _infer_access_op(expr, env)
        if expr.op in _COLLECTION_OPS:
            return _infer_collection_op(expr, env)
        if expr.op in _UNARY_OPS:
            if len(kids) != 1:
                return type_error("unary " + expr.op + " arity", ())
            child_expected = None
            if expr.op == "NEG" and expected is not None and expected in _NUMERIC:
                child_expected = expected
            elif expr.op == "NOT":
                child_expected = BOOL
            t0 = infer_type(kids[0], env, expected=child_expected)
            if isinstance(t0, TypeErrorVal):
                return t0
            got = check_unary_op(expr.op, t0)
            if isinstance(got, TypeErrorVal):
                return got
            return _meet_expected(got, expected)
        if expr.op in _ARITH_OPS or expr.op in _COMPARE_OPS:
            if len(kids) != 2:
                return type_error("binary " + expr.op + " arity", ())
            op_expected = expected if expr.op in _ARITH_OPS else None
            if expr.op in ("AND", "OR"):
                op_expected = BOOL
            t1, t2 = _infer_binary_operands(kids[0], kids[1], env, op_expected)
            if isinstance(t1, TypeErrorVal):
                return t1
            if isinstance(t2, TypeErrorVal):
                return t2
            if expr.op in _ARITH_OPS:
                got = check_binary_op(expr.op, t1, t2)
            else:
                got = check_compare_op(expr.op, t1, t2)
            if isinstance(got, TypeErrorVal):
                return got
            return _meet_expected(got, expected)
        return type_error("unknown op " + repr(expr.op), ())
    return type_error("cannot infer type of " + type(expr).__name__, ())


def _meet_expected(got: Type, expected: Type | None) -> Type | TypeErrorVal:
    if expected is None:
        return got
    u = unify(got, expected)
    if u is not None:
        return u
    if subtype(got, expected):
        return expected
    return type_error("type does not match expected", ())


def infer_if(
    expr: object,
    env: Env | None = None,
    expected: Type | None = None,
) -> Type | TypeErrorVal:
    """IF/COND: (Bool, T, T) -> T via unify of then/else branches."""
    if isinstance(expr, IfExpr):
        cond, then_b, else_b = expr.cond, expr.then_branch, expr.else_branch
    elif isinstance(expr, OpExpr) and expr.op in ("IF", "COND"):
        kids = list(expr.children or [])
        if len(kids) != 3:
            return type_error(expr.op + " arity", ())
        cond, then_b, else_b = kids[0], kids[1], kids[2]
    else:
        return type_error("infer_if expects IfExpr or IF/COND OpExpr", ())

    ct = infer_type(cond, env, expected=BOOL)
    if isinstance(ct, TypeErrorVal):
        return ct
    if ct != BOOL:
        return type_error("IF condition must be BOOL", ())

    tt = infer_type(then_b, env, expected=expected)
    if isinstance(tt, TypeErrorVal):
        return tt
    et = infer_type(else_b, env, expected=expected if expected is not None else tt)
    if isinstance(et, TypeErrorVal):
        return et

    unified = unify(tt, et)
    if unified is None:
        return type_error("IF branch type mismatch", ())
    return _meet_expected(unified, expected)


def infer_hole(
    expr: object,
    env: Env | None = None,
    expected: Type | None = None,
) -> Type | TypeErrorVal:
    """HoleExpr: bare `?` adopts expected (or ANY); `?:T` resolves / meets expected."""
    if not isinstance(expr, HoleExpr):
        return type_error("infer_hole expects HoleExpr", ())
    labeled: Type | None = None
    if expr.label is not None and expr.label != "":
        resolved = _resolve_type_name(str(expr.label))
        if isinstance(resolved, TypeErrorVal):
            return resolved
        labeled = resolved
    if labeled is not None and expected is not None:
        return _meet_expected(labeled, expected)
    if labeled is not None:
        return labeled
    if expected is not None:
        return expected
    return ANY

def infer_fn(expr: object, env: Env | None = None) -> Type | TypeErrorVal:
    """Infer FnExpr (params+body) or CallExpr application.

    When FnExpr carries Phase 3 effects/caps annotations, they are attached
    to the resulting FnType (AIR form for those annotations is not locked yet).
    """
    if isinstance(expr, FnExpr):
        from .effects import CapabilitySet, EffectSet

        ctx = env if env is not None else Env()
        ctx.enter_scope("fn")
        param_types: list[Type] = []
        for item in expr.params:
            if not (isinstance(item, tuple) and len(item) >= 1):
                ctx.leave_scope()
                return type_error("FN param must be (name, type)", ())
            name = item[0]
            ann = item[1] if len(item) > 1 else None
            if ann is None:
                ctx.leave_scope()
                return type_error("FN param requires type annotation", ())
            pt = _resolve_type_name(str(ann))
            if isinstance(pt, TypeErrorVal):
                ctx.leave_scope()
                return pt
            ctx.bind(str(name), pt)
            param_types.append(pt)
        ret = infer_type(expr.body, ctx)
        ctx.leave_scope()
        if isinstance(ret, TypeErrorVal):
            return ret
        effects = expr.effects if isinstance(expr.effects, EffectSet) else EffectSet()
        caps = expr.caps if isinstance(expr.caps, CapabilitySet) else CapabilitySet()
        return FnType(tuple(param_types), ret, effects=effects, caps=caps)

    if isinstance(expr, CallExpr):
        ft = infer_type(expr.fn, env)
        if isinstance(ft, TypeErrorVal):
            return ft
        if not isinstance(ft, FnType):
            return type_error("CALL on non-function", ())
        args = list(expr.args or [])
        if len(args) != len(ft.params):
            return type_error("CALL arity mismatch", ())
        for arg, expected in zip(args, ft.params):
            at = infer_type(arg, env)
            if isinstance(at, TypeErrorVal):
                return at
            if unify(at, expected) is None:
                return type_error("CALL arg type mismatch", ())
        return ft.ret

    return type_error("infer_fn expects FnExpr or CallExpr", ())


def infer_def(expr: object, env: Env | None = None) -> Type | TypeErrorVal:
    """Bind DefNode name to inferred body type in Env; return that type."""
    if not isinstance(expr, DefNode):
        return type_error("infer_def expects DefNode", ())
    ctx = env if env is not None else Env()
    body_t = infer_type(expr.body, ctx)
    if isinstance(body_t, TypeErrorVal):
        return body_t
    ctx.bind(str(expr.name), body_t)
    return body_t


def _field_key(key: object) -> str | int | TypeErrorVal:
    """Resolve GET/SET/FIELD key from AST atom or bare str/int."""
    if isinstance(key, IdentExpr):
        return str(key.id)
    if isinstance(key, LitExpr) and isinstance(key.value, int) and not isinstance(key.value, bool):
        return int(key.value)
    if isinstance(key, str):
        return key
    if isinstance(key, int) and not isinstance(key, bool):
        return key
    return type_error("access key must be field name or tuple index", ())


def _lookup_record_field(rec: RecordType, name: str) -> Type | TypeErrorVal:
    for fname, fty in rec.fields:
        if fname == name:
            return fty
    return type_error("unknown field " + repr(name), ())


def check_access(
    op: str,
    base: Type,
    key: object,
    val: Type | None = None,
) -> Type | TypeErrorVal:
    """Type-check GET / FIELD / SET on records, tuples, and maps."""
    op = str(op).upper()
    if op not in ("GET", "FIELD", "SET"):
        return type_error("unknown access op " + repr(op), ())

    k = _field_key(key)
    if isinstance(k, TypeErrorVal):
        return k

    if op in ("GET", "FIELD"):
        if isinstance(base, RecordType):
            if not isinstance(k, str):
                return type_error("record access needs field name", ())
            return _lookup_record_field(base, k)
        if isinstance(base, TupleType):
            if not isinstance(k, int):
                return type_error("tuple access needs index", ())
            if k < 0 or k >= len(base.elems):
                return type_error("tuple index out of range", ())
            return base.elems[k]
        if isinstance(base, MapType):
            return base.val
        return type_error(op + " requires record, tuple, or map", ())

    # SET
    if val is None:
        return type_error("SET requires value type", ())
    if isinstance(base, RecordType):
        if not isinstance(k, str):
            return type_error("record SET needs field name", ())
        cur = _lookup_record_field(base, k)
        if isinstance(cur, TypeErrorVal):
            return cur
        if unify(val, cur) is None:
            return type_error("SET field type mismatch", ())
        return base
    if isinstance(base, TupleType):
        if not isinstance(k, int):
            return type_error("tuple SET needs index", ())
        if k < 0 or k >= len(base.elems):
            return type_error("tuple index out of range", ())
        if unify(val, base.elems[k]) is None:
            return type_error("SET tuple elem type mismatch", ())
        return base
    if isinstance(base, MapType):
        if unify(val, base.val) is None:
            return type_error("SET map value type mismatch", ())
        return base
    return type_error("SET requires record, tuple, or map", ())


def _infer_access_op(expr: OpExpr, env: Env | None) -> Type | TypeErrorVal:
    kids = list(expr.children or [])
    if expr.op in ("GET", "FIELD"):
        if len(kids) != 2:
            return type_error(expr.op + " arity", ())
        base_t = infer_type(kids[0], env)
        if isinstance(base_t, TypeErrorVal):
            return base_t
        return check_access(expr.op, base_t, kids[1])
    if expr.op == "SET":
        if len(kids) != 3:
            return type_error("SET arity", ())
        base_t = infer_type(kids[0], env)
        if isinstance(base_t, TypeErrorVal):
            return base_t
        val_t = infer_type(kids[2], env)
        if isinstance(val_t, TypeErrorVal):
            return val_t
        return check_access("SET", base_t, kids[1], val_t)
    return type_error("unknown access op", ())


def check_collection(op: str, *arg_types: Type) -> Type | TypeErrorVal:
    """Type-check LEN AT APPEND CONCAT MAP FILTER."""
    op = str(op).upper()
    args = list(arg_types)

    if op == "LEN":
        if len(args) != 1:
            return type_error("LEN arity", ())
        if isinstance(args[0], (ListType, SetType, MapType, TupleType)) or args[0] is STRING:
            return I32
        return type_error("LEN requires collection or string", ())

    if op == "AT":
        if len(args) != 2:
            return type_error("AT arity", ())
        if args[1] != I32:
            return type_error("AT index must be i32", ())
        if isinstance(args[0], ListType):
            return args[0].elem
        if args[0] is STRING or args[0] == STRING:
            return STRING
        if isinstance(args[0], TupleType):
            # index unknown statically → error unless single elem; use elem unify
            if not args[0].elems:
                return type_error("AT on empty tuple", ())
            return args[0].elems[0]
        return type_error("AT requires list, tuple, or string", ())

    if op == "APPEND":
        if len(args) != 2:
            return type_error("APPEND arity", ())
        if not isinstance(args[0], ListType):
            return type_error("APPEND requires list", ())
        if unify(args[1], args[0].elem) is None:
            return type_error("APPEND elem type mismatch", ())
        return args[0]

    if op == "CONCAT":
        if len(args) != 2:
            return type_error("CONCAT arity", ())
        if (args[0] is STRING or args[0] == STRING) and (
            args[1] is STRING or args[1] == STRING
        ):
            return STRING
        if not isinstance(args[0], ListType) or not isinstance(args[1], ListType):
            return type_error("CONCAT requires lists or strings", ())
        if unify(args[0].elem, args[1].elem) is None:
            return type_error("CONCAT elem type mismatch", ())
        return args[0]

    if op == "MAP":
        if len(args) != 2:
            return type_error("MAP arity", ())
        if not isinstance(args[0], ListType):
            return type_error("MAP requires list", ())
        if not isinstance(args[1], FnType) or len(args[1].params) != 1:
            return type_error("MAP requires FnType(elem)->ret", ())
        if unify(args[0].elem, args[1].params[0]) is None:
            return type_error("MAP fn param mismatch", ())
        return ListType(args[1].ret)

    if op == "FILTER":
        if len(args) != 2:
            return type_error("FILTER arity", ())
        if not isinstance(args[0], ListType):
            return type_error("FILTER requires list", ())
        if not isinstance(args[1], FnType) or len(args[1].params) != 1:
            return type_error("FILTER requires FnType(elem)->bool", ())
        if unify(args[0].elem, args[1].params[0]) is None:
            return type_error("FILTER fn param mismatch", ())
        if args[1].ret != BOOL:
            return type_error("FILTER fn must return bool", ())
        return args[0]

    return type_error("unknown collection op " + repr(op), ())


def _infer_collection_op(expr: OpExpr, env: Env | None) -> Type | TypeErrorVal:
    kids = list(expr.children or [])
    types: list[Type] = []
    for kid in kids:
        t = infer_type(kid, env)
        if isinstance(t, TypeErrorVal):
            return t
        types.append(t)
    return check_collection(expr.op, *types)


def check_expr(expr: object, env: Env | None = None) -> Type | TypeErrorVal:
    """Public type-check entry: dispatch over AST via infer_type."""
    return infer_type(expr, env)
