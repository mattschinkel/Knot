"""Type checker helpers (Phase 2).

Type errors are values (spec D4): returned, never raised.
"""

from __future__ import annotations

from dataclasses import dataclass

from .ast import IdentExpr, IfExpr, LitExpr, OpExpr, TypedLit, UnitExpr
from .env import Env
from .errors import StructuredError
from .types import (
    Type, BOOL, I32, I64, F32, F64, STRING, BYTES, UNIT, NEVER, unify,
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
    "bool": BOOL, "string": STRING, "bytes": BYTES, "unit": UNIT, "never": NEVER,
}

_NUMERIC = frozenset({I32, I64, F32, F64})
_ARITH_OPS = frozenset({"ADD", "SUB", "MUL", "DIV", "MOD"})
_UNARY_OPS = frozenset({"NEG", "NOT"})
_COMPARE_OPS = frozenset({"EQ", "NE", "LT", "LE", "GT", "GE", "AND", "OR"})


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


def infer_type(expr: object, env: Env | None = None) -> Type | TypeErrorVal:
    """Infer the type of a kernel AST expression."""
    if isinstance(expr, LitExpr):
        return _lit_type(expr.value)
    if isinstance(expr, TypedLit):
        return _resolve_type_name(expr.type_name)
    if isinstance(expr, UnitExpr):
        return UNIT
    if isinstance(expr, IdentExpr):
        ctx = env if env is not None else Env()
        name = expr.id if isinstance(expr.id, str) else str(expr.id)
        found = ctx.lookup(name)
        if found is None:
            return type_error("unbound identifier " + repr(name), tuple(expr.path or ()))
        return found
    if isinstance(expr, IfExpr):
        return infer_if(expr, env)
    if isinstance(expr, OpExpr):
        kids = list(expr.children or [])
        if expr.op in ("IF", "COND"):
            return infer_if(expr, env)
        if expr.op in _UNARY_OPS:
            if len(kids) != 1:
                return type_error("unary " + expr.op + " arity", ())
            t0 = infer_type(kids[0], env)
            if isinstance(t0, TypeErrorVal):
                return t0
            return check_unary_op(expr.op, t0)
        if expr.op in _ARITH_OPS or expr.op in _COMPARE_OPS:
            if len(kids) != 2:
                return type_error("binary " + expr.op + " arity", ())
            t1 = infer_type(kids[0], env)
            if isinstance(t1, TypeErrorVal):
                return t1
            t2 = infer_type(kids[1], env)
            if isinstance(t2, TypeErrorVal):
                return t2
            if expr.op in _ARITH_OPS:
                return check_binary_op(expr.op, t1, t2)
            return check_compare_op(expr.op, t1, t2)
        return type_error("unknown op " + repr(expr.op), ())
    return type_error("cannot infer type of " + type(expr).__name__, ())


def infer_if(expr: object, env: Env | None = None) -> Type | TypeErrorVal:
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

    ct = infer_type(cond, env)
    if isinstance(ct, TypeErrorVal):
        return ct
    if ct != BOOL:
        return type_error("IF condition must be BOOL", ())

    tt = infer_type(then_b, env)
    if isinstance(tt, TypeErrorVal):
        return tt
    et = infer_type(else_b, env)
    if isinstance(et, TypeErrorVal):
        return et

    unified = unify(tt, et)
    if unified is None:
        return type_error("IF branch type mismatch", ())
    return unified
