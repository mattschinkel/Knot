"""Bridge type-check failures to ErrorVal / ErrExpr (Phase 5)."""

from __future__ import annotations

from dataclasses import dataclass

from .ast import ErrExpr, OpExpr
from .canonical import print_canonical
from .checker import TypeErrorVal, infer_type
from .env import Env
from .errors import StructuredError
from .repairs import error_to_err_expr, suggest_repairs
from .types import Type
from .values import ErrorVal


@dataclass(frozen=True)
class DiagnoseOk:
    """Successful type diagnosis."""

    typ: Type

    @property
    def ok(self) -> bool:
        return True


@dataclass(frozen=True)
class DiagnoseErr:
    """Failed type diagnosis with structured error value + AIR."""

    error: ErrorVal
    err_expr: ErrExpr
    air: str

    @property
    def ok(self) -> bool:
        return False


def diagnose(expr: object, env: Env | None = None) -> DiagnoseOk | DiagnoseErr:
    """Type-check expr; on failure return ErrorVal with repair suggestions."""
    ctx = env if env is not None else Env()
    result = infer_type(expr, ctx)
    if not isinstance(result, TypeErrorVal):
        return DiagnoseOk(typ=result)

    op = str(getattr(expr, "op", None) or "") or None
    expected = None
    actual = None
    if isinstance(expr, OpExpr):
        kids = list(expr.children or [])
        if len(kids) == 2:
            t1 = infer_type(kids[0], ctx)
            t2 = infer_type(kids[1], ctx)
            if not isinstance(t1, TypeErrorVal):
                expected = t1
            if not isinstance(t2, TypeErrorVal):
                actual = t2
            # Prefer left type as expected when both typed (binary mismatch).
            if expected is not None and actual is not None:
                pass
            elif actual is not None and expected is None:
                expected = actual
                actual = None

    repairs = suggest_repairs(
        code="TYPE_MISMATCH",
        op=op,
        expected=expected,
        actual=actual,
        path=tuple(result.path) if result.path else (),
    )
    structured = StructuredError(
        kind="TYPE_MISMATCH",
        node=".".join(str(p) for p in result.path) if result.path else None,
        op=op,
        expected=expected,
        got=actual,
        repair=tuple(r.to_air() for r in repairs),
        message=result.message,
    )
    err_val = ErrorVal(structured)
    err_expr = error_to_err_expr(structured, path=list(result.path), repairs=repairs)
    return DiagnoseErr(error=err_val, err_expr=err_expr, air=print_canonical(err_expr))


def err_expr_to_value(node: ErrExpr) -> ErrorVal:
    """ErrExpr → ErrorVal (execute/result path)."""
    return ErrorVal(
        StructuredError(
            kind=node.code,
            node=".".join(str(p) for p in node.path) if node.path else None,
            expected=None,
            got=None,
            repair=tuple(
                print_canonical(f) if not isinstance(f, str) else f for f in node.fixes
            ),
            message="ERR value",
        )
    )
