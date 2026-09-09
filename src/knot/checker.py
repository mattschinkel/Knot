"""Type checker helpers (Phase 2).

Type errors are values (spec D4): returned, never raised.
"""

from __future__ import annotations

from dataclasses import dataclass

from .ast import IdentExpr, LitExpr, TypedLit, UnitExpr
from .env import Env
from .errors import StructuredError
from .types import (
    Type, BaseType, BOOL, I32, I64, F32, F64, STRING, BYTES, UNIT, NEVER,
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


def infer_type(expr: object, env: Env | None = None) -> Type | TypeErrorVal:
    """Infer the type of a kernel AST expression (Phase 2 T5: literals/idents)."""
    if isinstance(expr, LitExpr):
        return _lit_type(expr.value)
    if isinstance(expr, TypedLit):
        t = _BASE_BY_NAME.get(expr.type_name)
        if t is None:
            return type_error("unknown type " + repr(expr.type_name), tuple(expr.path or ()))
        return t
    if isinstance(expr, UnitExpr):
        return UNIT
    if isinstance(expr, IdentExpr):
        ctx = env if env is not None else Env()
        name = expr.id if isinstance(expr.id, str) else str(expr.id)
        found = ctx.lookup(name)
        if found is None:
            return type_error("unbound identifier " + repr(name), tuple(expr.path or ()))
        return found
    return type_error("cannot infer type of " + type(expr).__name__, ())


_NUMERIC = frozenset({I32, I64, F32, F64})
_ARITH_OPS = frozenset({"ADD", "SUB", "MUL", "DIV", "MOD"})


def check_binary_op(op: str, t1: Type, t2: Type) -> Type | TypeErrorVal:
    """Type rule for binary kernel ops (Phase 2 T6).

    Spec: ADD/SUB/MUL/DIV/MOD are (T, T) -> T for numeric T; no implicit casts.
    """
    if op not in _ARITH_OPS:
        return type_error("unknown binary op " + repr(op), ())
    if t1 not in _NUMERIC or t2 not in _NUMERIC:
        return type_error("binary " + op + " requires numeric types", ())
    if t1 != t2:
        return type_error("binary " + op + " operand type mismatch", ())
    return t1

def check_unary_op(op: str, t: Type) -> Type | TypeErrorVal:
    """Type rule for unary ops: NEG, NOT.

    NEG: numeric T -> T; NOT: Bool -> Bool.
    """
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
    if op == "EQ" or op == "NE":
        return BOOL
    if op == "LT" or op == "LE" or op == "GT" or op == "GE":
        if t1 not in _NUMERIC or t2 not in _NUMERIC:
            return type_error("LT/LE/GT/GE requires numeric type", ())
        return BOOL
    if op == "AND" or op == "OR":
        if t1 != BOOL or t2 != BOOL:
            return type_error("AND/OR requires BOOL type", ())
        return BOOL
    return type_error("unknown compare op " + repr(op), ())
