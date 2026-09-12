"""Dataflow concurrency, regions, and UNSAFE (Phase 11).

User code has no threads/locks/malloc. PAR means independence; evaluation
collects results in argument order (may run sequentially).
"""

from __future__ import annotations

from typing import Callable

from .ast import DerefExpr, ParExpr, RefExpr, SeqExpr, UnsafeExpr
from .effects import Capability, CapabilitySet, check_capabilities
from .errors import StructuredError
from .types import RegionType, TupleType, Type, UNIT, subtype
from .values import ErrorVal, RegionVal, TupleVal, UnitVal, Value


EvalFn = Callable[[object], Value]


def schedule_par(branches: list) -> list[list]:
    """Return concurrent groups. v1: one group containing all branches (D1)."""
    return [list(branches)]


def needed_unsafe_caps(cap_names: list[str]) -> CapabilitySet:
    """Always require Capability.UNSAFE plus any listed CAPS names."""
    caps: list[Capability] = [Capability.UNSAFE]
    for n in cap_names:
        try:
            c = Capability(n)
        except ValueError:
            continue
        if c not in caps:
            caps.append(c)
    return CapabilitySet(caps)


def check_unsafe(cap_names: list[str], granted: CapabilitySet | None) -> ErrorVal | None:
    """None if granted covers needed; else ErrorVal(kind=capability)."""
    granted = granted or CapabilitySet()
    needed = needed_unsafe_caps(cap_names)
    if check_capabilities(needed, granted):
        return None
    return ErrorVal(
        StructuredError(
            kind="capability",
            message="UNSAFE missing required capabilities",
            op="UNSAFE",
        )
    )


def eval_par(branches: list, ev: EvalFn) -> Value:
    """Evaluate PAR children; return TupleVal in source order."""
    results: list[Value] = []
    types: list[Type] = []
    for b in branches:
        v = ev(b)
        if isinstance(v, ErrorVal):
            return v
        results.append(v)
        types.append(v.type)
    return TupleVal(tuple(results), tuple(types))


def eval_seq(steps: list, ev: EvalFn) -> Value:
    """Evaluate SEQ left-to-right; return last value (or unit if empty)."""
    if not steps:
        return UnitVal()
    last: Value = UnitVal()
    for s in steps:
        last = ev(s)
        if isinstance(last, ErrorVal):
            return last
    return last


def eval_ref(region: str, expr: object, ev: EvalFn) -> Value:
    inner = ev(expr)
    if isinstance(inner, ErrorVal):
        return inner
    return RegionVal(inner, region)


def eval_deref(expr: object, ev: EvalFn) -> Value:
    v = ev(expr)
    if isinstance(v, ErrorVal):
        return v
    if isinstance(v, RegionVal):
        return v.value
    return ErrorVal(
        StructuredError(
            kind="region",
            message="DEREF expects RegionVal",
            op="DEREF",
        )
    )


def eval_unsafe(
    caps: list[str],
    body: object,
    ev: EvalFn,
    granted: CapabilitySet | None,
) -> Value:
    err = check_unsafe(caps, granted)
    if err is not None:
        return err
    return ev(body)


def evaluate_concurrency(
    expr: object,
    ev: EvalFn,
    *,
    granted: CapabilitySet | None = None,
) -> Value | None:
    """Dispatch Phase 11 nodes. Returns None if expr is not a concurrency node."""
    if isinstance(expr, ParExpr):
        return eval_par(expr.branches, ev)
    if isinstance(expr, SeqExpr):
        return eval_seq(expr.steps, ev)
    if isinstance(expr, RefExpr):
        return eval_ref(expr.region, expr.expr, ev)
    if isinstance(expr, DerefExpr):
        return eval_deref(expr.expr, ev)
    if isinstance(expr, UnsafeExpr):
        return eval_unsafe(expr.caps, expr.body, ev, granted)
    return None


def infer_par_type(branch_types: list[Type]) -> Type:
    return TupleType(tuple(branch_types))


def infer_seq_type(step_types: list[Type]) -> Type:
    if not step_types:
        return UNIT
    return step_types[-1]


def infer_ref_type(inner: Type, region: str) -> Type:
    return RegionType(inner, region)


def region_subtype(s: Type, t: Type) -> bool:
    """RegionType[A,r] <: RegionType[B,r] iff A <: B (same region)."""
    if isinstance(s, RegionType) and isinstance(t, RegionType):
        if s.region != t.region:
            return False
        return subtype(s.inner, t.inner)
    return False
