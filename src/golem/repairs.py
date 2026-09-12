"""Deterministic repair candidates for structured errors (Phase 5).

Repairs are suggestions only — applying them is Phase 6.
"""

from __future__ import annotations

from dataclasses import dataclass

from .ast import ErrExpr, HoleExpr, IdentExpr, LitExpr, OpExpr
from .errors import StructuredError
from .types import Type


# Known fix op names (AIR).
FIX_OPS = frozenset({"REPLACE", "CONVERT", "REMOVE_OP", "HOLE"})


@dataclass(frozen=True)
class Repair:
    """One suggested fix (maps to an OP[...] node)."""

    kind: str  # replace | convert | remove_op | hole
    path: tuple = ()
    payload: str | None = None  # type name or replacement summary

    def to_op(self) -> OpExpr:
        if self.kind == "replace":
            # REPLACE[pathHole, ?:payload] — path encoded as hole or ident
            target = HoleExpr(id=0, label=self.payload) if self.payload else HoleExpr(id=0)
            return OpExpr("REPLACE", [IdentExpr(".".join(map(str, self.path)) or "_"), target])
        if self.kind == "convert":
            return OpExpr(
                "CONVERT",
                [
                    IdentExpr(".".join(map(str, self.path)) or "_"),
                    IdentExpr(self.payload or "any"),
                ],
            )
        if self.kind == "remove_op":
            return OpExpr("REMOVE_OP", [])
        if self.kind == "hole":
            return OpExpr("HOLE", [IdentExpr(self.payload or "any")])
        return OpExpr(self.kind.upper(), [])

    def to_air(self) -> str:
        from .canonical import print_canonical

        return print_canonical(self.to_op())


def validate_fix(node: object) -> bool:
    """True if node is a well-shaped fix suggestion (arity only)."""
    if not isinstance(node, OpExpr):
        return False
    op = str(node.op).upper()
    kids = list(node.children or [])
    if op == "REPLACE":
        return len(kids) == 2
    if op == "CONVERT":
        return len(kids) == 2
    if op == "REMOVE_OP":
        return len(kids) == 0
    if op == "HOLE":
        return len(kids) <= 1
    return op in FIX_OPS


def suggest_repairs(
    *,
    code: str = "TYPE_MISMATCH",
    op: str | None = None,
    expected: Type | str | None = None,
    actual: Type | str | None = None,
    path: tuple = (),
) -> tuple[Repair, ...]:
    """Deterministic repair set (Phase 5 D4). Cap 6."""
    out: list[Repair] = []
    exp_s = _type_str(expected)
    act_s = _type_str(actual)

    if code in ("TYPE_MISMATCH", "type") or expected is not None:
        if exp_s:
            out.append(Repair(kind="replace", path=path, payload=exp_s))
            out.append(Repair(kind="hole", path=path, payload=exp_s))
        if exp_s and act_s and exp_s != act_s:
            # Numeric widen/narrow as convert candidate (not applied).
            if {exp_s, act_s} <= {"i32", "i64"} or {exp_s, act_s} <= {"f32", "f64"}:
                out.append(Repair(kind="convert", path=path, payload=exp_s))
        if op and op.upper() in (
            "ADD",
            "SUB",
            "MUL",
            "DIV",
            "MOD",
            "EQ",
            "NE",
            "LT",
            "LE",
            "GT",
            "GE",
            "AND",
            "OR",
        ):
            out.append(Repair(kind="remove_op", path=path))

    if code in ("hole_trap", "HOLE_TRAP"):
        if exp_s:
            out.append(Repair(kind="replace", path=path, payload=exp_s))
        else:
            out.append(Repair(kind="hole", path=path, payload="any"))

    # Dedupe by (kind, payload)
    seen: set[tuple] = set()
    uniq: list[Repair] = []
    for r in out:
        key = (r.kind, r.payload, r.path)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)
        if len(uniq) >= 6:
            break
    return tuple(uniq)


def repairs_to_ops(repairs: tuple[Repair, ...]) -> list[OpExpr]:
    return [r.to_op() for r in repairs]


def error_to_err_expr(
    err: StructuredError,
    *,
    path: list | None = None,
    repairs: tuple[Repair, ...] | None = None,
) -> ErrExpr:
    """Build ErrExpr AIR from StructuredError (+ optional Repair set)."""
    reps = repairs
    if reps is None:
        reps = suggest_repairs(
            code=err.kind.upper() if err.kind else "ERROR",
            op=err.op,
            expected=err.expected,
            actual=err.got,
            path=tuple(path or ()),
        )
    code = err.kind.upper() if err.kind else "ERROR"
    if code == "TYPE":
        code = "TYPE_MISMATCH"
    return ErrExpr(
        code=code,
        path=list(path) if path is not None else _node_path(err.node),
        expected=_type_str(err.expected) or "any",
        actual=_type_str(err.got) or "any",
        fixes=repairs_to_ops(reps),
    )


def _type_str(t: Type | str | None) -> str | None:
    if t is None:
        return None
    if isinstance(t, str):
        return t
    # BaseType and friends
    name = getattr(t, "name", None)
    if name:
        return str(name)
    return str(t)


def _node_path(node: str | None) -> list:
    if not node:
        return []
    parts = []
    for p in str(node).split("."):
        if p.isdigit():
            parts.append(int(p))
        elif p:
            parts.append(p)
    return parts
