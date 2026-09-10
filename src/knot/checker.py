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


def infer_type(expr, env):
    match expr:
        case IdentExpr(id):
            return env.lookup(id)
        case LitExpr(value):
            return infer_literal_type(value)
        case UnitExpr():
            return UNIT
        case _:
            return type_error("unknown expression type", ())


def infer_literal_type(value):
    if isinstance(value, bool):
        return BOOL
    if isinstance(value, int):
        return I32
    if isinstance(value, float):
        return F64
    if isinstance(value, str):
        return STRING
    return type_error("unknown literal type", ())


def infer_literal_type(value):
    if isinstance(value, bool):
        return BOOL
    if isinstance(value, int):
        return I32
    if isinstance(value, float):
        return F64
    if isinstance(value, str):
        return STRING
    return type_error("unknown literal type", ())


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
