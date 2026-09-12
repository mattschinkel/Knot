"""Partial compile: VALID / PARTIAL / INVALID + hole reports (Phase 4).

Deterministic kernel only — no LLM. Holes type-check; evaluation traps as
ErrorVal (errors-as-values), never raises.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ast import (
    CallExpr,
    DefNode,
    FnExpr,
    HoleExpr,
    IdentExpr,
    IfExpr,
    LitExpr,
    OpExpr,
    TypedLit,
    UnitExpr,
)
from .checker import TypeErrorVal, infer_type
from .env import Env
from .errors import StructuredError
from .types import (
    BOOL,
    BYTES,
    F32,
    F64,
    I32,
    I64,
    STRING,
    Type,
    UNIT,
    subtype,
    unify,
)
from .values import (
    BoolVal,
    ErrorVal,
    FloatVal,
    HoleVal,
    IntVal,
    StringVal,
    UnitVal,
    Value,
)


class CompileStatus(str, Enum):
    VALID = "valid"
    PARTIAL = "partial"
    INVALID = "invalid"


@dataclass(frozen=True)
class HoleReport:
    """One hole occurrence in a program (design §6)."""

    hole_id: int | str
    expected: Type | None
    context: str
    path: tuple
    candidates: tuple[str, ...]


@dataclass(frozen=True)
class CompileReport:
    status: CompileStatus
    typ: Type | None
    holes: tuple[HoleReport, ...]
    errors: tuple[TypeErrorVal, ...]


_CANDIDATE_CAP = 8

_DEFAULT_LITERALS: dict[Type, str] = {
    I32: "0",
    I64: "0",
    F32: "0.0",
    F64: "0.0",
    BOOL: "false",
    STRING: '""',
    BYTES: "[]",
    UNIT: "()",
}


def suggest_candidates(expected: Type | None, env: Env | None = None) -> tuple[str, ...]:
    """Deterministic hole fill suggestions (Phase 4 D4). Cap {_CANDIDATE_CAP}."""
    out: list[str] = []
    ctx = env if env is not None else Env()
    if expected is not None:
        for name, typ in sorted(ctx.bindings().items()):
            if unify(typ, expected) is not None or subtype(typ, expected):
                out.append(name)
                if len(out) >= _CANDIDATE_CAP:
                    return tuple(out)
        lit = _DEFAULT_LITERALS.get(expected)
        if lit is not None and lit not in out:
            out.append(lit)
    return tuple(out[:_CANDIDATE_CAP])


def collect_holes(
    expr: object,
    env: Env | None = None,
    *,
    expected: Type | None = None,
    context: str = "root",
    path: tuple = (),
) -> tuple[HoleReport, ...]:
    """Walk AST and build HoleReports with context-propagated expected types."""
    ctx = env if env is not None else Env()
    found: list[HoleReport] = []

    def walk(
        node: object,
        exp: Type | None,
        ctx_name: str,
        p: tuple,
    ) -> None:
        if isinstance(node, HoleExpr):
            hole_exp: Type | None = exp
            if node.label:
                t = infer_type(node, ctx, expected=exp)
                hole_exp = None if isinstance(t, TypeErrorVal) else t
            elif exp is not None:
                hole_exp = exp
            else:
                t = infer_type(node, ctx)
                hole_exp = None if isinstance(t, TypeErrorVal) else t
            hid: int | str = node.id if node.id is not None else ".".join(map(str, p)) or 0
            found.append(
                HoleReport(
                    hole_id=hid,
                    expected=hole_exp if hole_exp is not None and not isinstance(hole_exp, TypeErrorVal) else exp,
                    context=ctx_name,
                    path=p,
                    candidates=suggest_candidates(
                        hole_exp if not isinstance(hole_exp, TypeErrorVal) else exp,
                        ctx,
                    ),
                )
            )
            return
        if isinstance(node, LitExpr) or isinstance(node, TypedLit) or isinstance(node, UnitExpr):
            return
        if isinstance(node, IdentExpr):
            return
        if isinstance(node, DefNode):
            walk(node.body, exp, f"DEF[{node.name}]", p + ("body",))
            return
        if isinstance(node, FnExpr):
            # Bind params into a child env for body candidates
            child = Env()
            # Copy outer bindings
            for n, t in ctx.bindings().items():
                child.bind(n, t)
            child.enter_scope("fn")
            for item in node.params:
                if isinstance(item, tuple) and len(item) >= 2 and item[1] is not None:
                    from .checker import _resolve_type_name

                    pt = _resolve_type_name(str(item[1]))
                    if not isinstance(pt, TypeErrorVal):
                        child.bind(str(item[0]), pt)
            _walk_in(node.body, exp, "FN.body", p + ("body",), child)
            return
        if isinstance(node, CallExpr):
            walk(node.fn, None, "CALL.fn", p + ("fn",))
            for i, arg in enumerate(node.args or []):
                walk(arg, None, f"CALL.arg{i}", p + ("arg", i))
            return
        if isinstance(node, IfExpr):
            walk(node.cond, BOOL, "IF.cond", p + ("cond",))
            walk(node.then_branch, exp, "IF.then", p + ("then",))
            walk(node.else_branch, exp, "IF.else", p + ("else",))
            return
        if isinstance(node, OpExpr):
            kids = list(node.children or [])
            op = node.op
            if op in ("IF", "COND") and len(kids) == 3:
                walk(kids[0], BOOL, f"{op}.cond", p + (0,))
                walk(kids[1], exp, f"{op}.then", p + (1,))
                walk(kids[2], exp, f"{op}.else", p + (2,))
                return
            if op in ("ADD", "SUB", "MUL", "DIV", "MOD") and len(kids) == 2:
                left_hole = isinstance(kids[0], HoleExpr) and (
                    kids[0].label is None or kids[0].label == ""
                )
                right_hole = isinstance(kids[1], HoleExpr) and (
                    kids[1].label is None or kids[1].label == ""
                )
                if left_hole and not right_hole:
                    rt = infer_type(kids[1], ctx, expected=exp)
                    sibling = None if isinstance(rt, TypeErrorVal) else rt
                    walk(kids[0], sibling if sibling is not None else exp, f"{op}.left", p + (0,))
                    walk(kids[1], exp, f"{op}.right", p + (1,))
                    return
                if right_hole and not left_hole:
                    lt = infer_type(kids[0], ctx, expected=exp)
                    sibling = None if isinstance(lt, TypeErrorVal) else lt
                    walk(kids[0], exp, f"{op}.left", p + (0,))
                    walk(kids[1], sibling if sibling is not None else exp, f"{op}.right", p + (1,))
                    return
                walk(kids[0], exp, f"{op}.left", p + (0,))
                walk(kids[1], exp, f"{op}.right", p + (1,))
                return
            if op in ("EQ", "NE", "LT", "LE", "GT", "GE") and len(kids) == 2:
                left_hole = isinstance(kids[0], HoleExpr) and (
                    kids[0].label is None or kids[0].label == ""
                )
                right_hole = isinstance(kids[1], HoleExpr) and (
                    kids[1].label is None or kids[1].label == ""
                )
                if left_hole and not right_hole:
                    rt = infer_type(kids[1], ctx)
                    sibling = None if isinstance(rt, TypeErrorVal) else rt
                    walk(kids[0], sibling, f"{op}.left", p + (0,))
                    walk(kids[1], None, f"{op}.right", p + (1,))
                    return
                if right_hole and not left_hole:
                    lt = infer_type(kids[0], ctx)
                    sibling = None if isinstance(lt, TypeErrorVal) else lt
                    walk(kids[0], None, f"{op}.left", p + (0,))
                    walk(kids[1], sibling, f"{op}.right", p + (1,))
                    return
            if op in ("AND", "OR") and len(kids) == 2:
                walk(kids[0], BOOL, f"{op}.left", p + (0,))
                walk(kids[1], BOOL, f"{op}.right", p + (1,))
                return
            if op in ("NEG",) and len(kids) == 1:
                walk(kids[0], exp, f"{op}.arg", p + (0,))
                return
            if op == "NOT" and len(kids) == 1:
                walk(kids[0], BOOL, f"{op}.arg", p + (0,))
                return
            for i, kid in enumerate(kids):
                walk(kid, None, f"{op}.{i}", p + (i,))
            return
        # Fallback: walk .children / .body if present
        kids = getattr(node, "children", None)
        if kids:
            for i, kid in enumerate(list(kids)):
                walk(kid, None, f"{type(node).__name__}.{i}", p + (i,))

    def _walk_in(node, exp, ctx_name, p, local_env: Env) -> None:
        nonlocal ctx
        saved = ctx
        ctx = local_env
        walk(node, exp, ctx_name, p)
        ctx = saved

    walk(expr, expected, context, path)
    return tuple(found)


def compile_check(expr: object, env: Env | None = None) -> CompileReport:
    """Type-check and classify as VALID / PARTIAL / INVALID (Phase 4 D1)."""
    ctx = env if env is not None else Env()
    typ = infer_type(expr, ctx)
    errors: list[TypeErrorVal] = []
    if isinstance(typ, TypeErrorVal):
        errors.append(typ)
        typ_out: Type | None = None
    else:
        typ_out = typ
    holes = collect_holes(expr, ctx, expected=typ_out)
    # Also flag typed holes with unknown labels already covered by infer_type errors.
    if errors:
        status = CompileStatus.INVALID
    elif holes:
        status = CompileStatus.PARTIAL
    else:
        status = CompileStatus.VALID
    return CompileReport(
        status=status,
        typ=typ_out,
        holes=holes,
        errors=tuple(errors),
    )


def evaluate(
    expr: object,
    env: Env | None = None,
    *,
    program: object | None = None,
    bindings: dict | None = None,
    granted_caps=None,
) -> Value:
    """Evaluate expression; holes trap as ErrorVal.

    ``program`` — list of DefNode (Phase 7) for named calls.
    ``bindings`` — name -> Value for property params / FN locals.
    ``granted_caps`` — CapabilitySet for UNSAFE (Phase 11).
    """
    binds = dict(bindings or {})

    def ev(node: object) -> Value:
        return evaluate(
            node, env, program=program, bindings=binds, granted_caps=granted_caps
        )

    from .concurrency import evaluate_concurrency

    conc = evaluate_concurrency(expr, ev, granted=granted_caps)
    if conc is not None:
        return conc

    from .ast import MatchExpr, MatchCase
    from .values import SumVal, StringVal

    if isinstance(expr, MatchExpr):
        scr = ev(expr.scrutinee)
        if isinstance(scr, ErrorVal):
            return scr
        if not isinstance(scr, SumVal):
            return ErrorVal(
                StructuredError(kind="type", op="MATCH", message="scrutinee must be sum")
            )
        for case in expr.cases:
            if case.tag == scr.tag:
                local = dict(binds)
                if case.binding:
                    local[case.binding] = scr.payload
                return evaluate(
                    case.body,
                    env,
                    program=program,
                    bindings=local,
                    granted_caps=granted_caps,
                )
        return ErrorVal(
            StructuredError(kind="match", op="MATCH", message="no matching CASE")
        )

    if isinstance(expr, HoleExpr) or isinstance(expr, HoleVal):
        hid = getattr(expr, "id", None)
        return ErrorVal(
            StructuredError(
                kind="hole_trap",
                node=str(hid) if hid is not None else None,
                message="evaluation reached a hole",
            )
        )
    from .ast import ErrExpr, CallExpr
    from .diagnose import err_expr_to_value

    if isinstance(expr, ErrExpr):
        return err_expr_to_value(expr)
    if isinstance(expr, LitExpr):
        v = expr.value
        if isinstance(v, Value):
            return v
        if isinstance(v, bool):
            return BoolVal(v)
        if isinstance(v, int):
            return IntVal(32, v)
        if isinstance(v, float):
            return FloatVal(64, v)
        if isinstance(v, str):
            return StringVal(v)
        if v is None:
            return UnitVal()
        return ErrorVal(StructuredError(kind="eval", message="unsupported literal"))
    if isinstance(expr, UnitExpr):
        return UnitVal()
    if isinstance(expr, TypedLit):
        return ev(LitExpr(expr.value))
    if isinstance(expr, IdentExpr):
        name = str(expr.id)
        if name in binds:
            return binds[name]
        return ErrorVal(
            StructuredError(
                kind="eval",
                message="unbound identifier at eval: " + name,
            )
        )
    if isinstance(expr, OpExpr):
        kids = list(expr.children or [])
        op = str(expr.op)
        # Named user function call: foo[args] → DEF[foo, FN[...]]
        if program is not None and op not in _KERNEL_OPS:
            return _call_def(op, kids, program, binds, granted_caps=granted_caps)
        if op in _ARITH_BIN and len(kids) == 2:
            a, b = ev(kids[0]), ev(kids[1])
            if isinstance(a, ErrorVal):
                return a
            if isinstance(b, ErrorVal):
                return b
            return _eval_arith(op, a, b)
        if op in _CMP_BIN and len(kids) == 2:
            a, b = ev(kids[0]), ev(kids[1])
            if isinstance(a, ErrorVal):
                return a
            if isinstance(b, ErrorVal):
                return b
            return _eval_cmp(op, a, b)
        if op == "NEG" and len(kids) == 1:
            a = ev(kids[0])
            if isinstance(a, ErrorVal):
                return a
            if isinstance(a, IntVal):
                return IntVal(a.bits, -a.value)
            if isinstance(a, FloatVal):
                return FloatVal(a.bits, -a.value)
            return ErrorVal(StructuredError(kind="eval", op=op, message="bad operands"))
        if op == "NOT" and len(kids) == 1:
            a = ev(kids[0])
            if isinstance(a, ErrorVal):
                return a
            if isinstance(a, BoolVal):
                return BoolVal(not a.value)
            return ErrorVal(StructuredError(kind="eval", op=op, message="bad operands"))
        if op in ("AND", "OR") and len(kids) == 2:
            a = ev(kids[0])
            if isinstance(a, ErrorVal):
                return a
            if not isinstance(a, BoolVal):
                return ErrorVal(StructuredError(kind="eval", op=op, message="bad operands"))
            # short-circuit
            if op == "AND" and not a.value:
                return BoolVal(False)
            if op == "OR" and a.value:
                return BoolVal(True)
            b = ev(kids[1])
            if isinstance(b, ErrorVal):
                return b
            if isinstance(b, BoolVal):
                return BoolVal(b.value)
            return ErrorVal(StructuredError(kind="eval", op=op, message="bad operands"))
        if op in ("IF", "COND") and len(kids) == 3:
            c = ev(kids[0])
            if isinstance(c, ErrorVal):
                return c
            if isinstance(c, BoolVal) and c.value:
                return ev(kids[1])
            return ev(kids[2])
        # Stage 0.5 runtime ops
        from .runtime_ops import RUNTIME_OPS, eval_op
        from .ast import IdentExpr as _Ident

        if op in RUNTIME_OPS:
            if op == "RECORD":
                # RECORD[name, FIELD[k,v], ...]
                flat: list = []
                if not kids:
                    return ErrorVal(
                        StructuredError(kind="arity", op="RECORD", message="need name")
                    )
                name_v = ev(kids[0])
                if isinstance(name_v, ErrorVal):
                    return name_v
                flat.append(name_v)
                for f in kids[1:]:
                    if isinstance(f, OpExpr) and str(f.op).upper() == "FIELD":
                        fk = list(f.children or [])
                        if len(fk) != 2:
                            return ErrorVal(
                                StructuredError(
                                    kind="arity", op="FIELD", message="FIELD[k,v]"
                                )
                            )
                        kn, vv = fk[0], fk[1]
                        if isinstance(kn, _Ident):
                            flat.append(StringVal(str(kn.id)))
                        else:
                            kv = ev(kn)
                            if isinstance(kv, ErrorVal):
                                return kv
                            flat.append(kv)
                        val = ev(vv)
                        if isinstance(val, ErrorVal):
                            return val
                        flat.append(val)
                    else:
                        return ErrorVal(
                            StructuredError(
                                kind="eval", op="RECORD", message="expected FIELD"
                            )
                        )
                return eval_op("RECORD", flat, granted=granted_caps)
            if op == "GET" and len(kids) == 2:
                base = ev(kids[0])
                if isinstance(base, ErrorVal):
                    return base
                fld = kids[1]
                if isinstance(fld, _Ident):
                    from .values import StringVal as SV

                    return eval_op("GET", [base, SV(str(fld.id))], granted=granted_caps)
                fv = ev(fld)
                if isinstance(fv, ErrorVal):
                    return fv
                return eval_op("GET", [base, fv], granted=granted_caps)
            if op == "MAP_NEW":
                return eval_op("MAP_NEW", [], granted=granted_caps)
            vals = []
            for kid in kids:
                v = ev(kid)
                if isinstance(v, ErrorVal):
                    return v
                vals.append(v)
            return eval_op(op, vals, granted=granted_caps)
        for kid in kids:
            v = ev(kid)
            if isinstance(v, ErrorVal) and v.err.kind == "hole_trap":
                return v
        return ErrorVal(
            StructuredError(kind="eval", op=op, message="op not implemented")
        )
    if isinstance(expr, IfExpr):
        c = ev(expr.cond)
        if isinstance(c, ErrorVal):
            return c
        if isinstance(c, BoolVal) and c.value:
            return ev(expr.then_branch)
        return ev(expr.else_branch)
    if isinstance(expr, DefNode):
        return ev(expr.body)
    if isinstance(expr, FnExpr):
        return ErrorVal(StructuredError(kind="eval", message="cannot eval raw FN"))
    if isinstance(expr, CallExpr):
        fn = expr.fn
        if isinstance(fn, IdentExpr) and program is not None:
            return _call_def(
                str(fn.id),
                list(expr.args or []),
                program,
                binds,
                granted_caps=granted_caps,
            )
        return ErrorVal(StructuredError(kind="eval", message="CALL not implemented"))
    return ErrorVal(
        StructuredError(kind="eval", message="cannot evaluate " + type(expr).__name__)
    )


_ARITH_BIN = frozenset({"ADD", "SUB", "MUL", "DIV", "MOD"})
_CMP_BIN = frozenset({"EQ", "NE", "LT", "LE", "GT", "GE"})
from .runtime_ops import RUNTIME_OPS

_KERNEL_OPS = (
    _ARITH_BIN
    | _CMP_BIN
    | frozenset({"NEG", "NOT", "AND", "OR", "IF", "COND", "GET", "SET", "FIELD"})
    | RUNTIME_OPS
)


def _eval_arith(op: str, a: Value, b: Value) -> Value:
    if isinstance(a, IntVal) and isinstance(b, IntVal):
        if op == "ADD":
            return IntVal(a.bits, a.value + b.value)
        if op == "SUB":
            return IntVal(a.bits, a.value - b.value)
        if op == "MUL":
            return IntVal(a.bits, a.value * b.value)
        if op == "DIV":
            if b.value == 0:
                return ErrorVal(StructuredError(kind="eval", op=op, message="div0"))
            return IntVal(a.bits, a.value // b.value)
        if op == "MOD":
            if b.value == 0:
                return ErrorVal(StructuredError(kind="eval", op=op, message="mod0"))
            return IntVal(a.bits, a.value % b.value)
    if isinstance(a, FloatVal) and isinstance(b, FloatVal):
        if op == "ADD":
            return FloatVal(a.bits, a.value + b.value)
        if op == "SUB":
            return FloatVal(a.bits, a.value - b.value)
        if op == "MUL":
            return FloatVal(a.bits, a.value * b.value)
        if op == "DIV":
            return FloatVal(a.bits, a.value / b.value)
    return ErrorVal(StructuredError(kind="eval", op=op, message="bad operands"))


def _eval_cmp(op: str, a: Value, b: Value) -> Value:
    if isinstance(a, IntVal) and isinstance(b, IntVal):
        x, y = a.value, b.value
    elif isinstance(a, FloatVal) and isinstance(b, FloatVal):
        x, y = a.value, b.value
    elif isinstance(a, BoolVal) and isinstance(b, BoolVal) and op in ("EQ", "NE"):
        x, y = a.value, b.value
    elif isinstance(a, StringVal) and isinstance(b, StringVal) and op in ("EQ", "NE"):
        x, y = a.value, b.value
    else:
        return ErrorVal(StructuredError(kind="eval", op=op, message="bad operands"))
    if op == "EQ":
        return BoolVal(x == y)
    if op == "NE":
        return BoolVal(x != y)
    if op == "LT":
        return BoolVal(x < y)
    if op == "LE":
        return BoolVal(x <= y)
    if op == "GT":
        return BoolVal(x > y)
    if op == "GE":
        return BoolVal(x >= y)
    return ErrorVal(StructuredError(kind="eval", op=op, message="bad operands"))


def _call_def(
    name: str,
    args: list,
    program: object,
    outer_binds: dict,
    *,
    granted_caps=None,
) -> Value:
    from .ast import DefNode, FnExpr

    items = program if isinstance(program, list) else [program]
    target = None
    for item in items:
        if isinstance(item, DefNode) and str(item.name) == name:
            target = item
            break
    if target is None:
        return ErrorVal(
            StructuredError(kind="eval", message="unknown function " + name)
        )
    body = target.body
    if isinstance(body, FnExpr):
        if len(args) != len(body.params):
            return ErrorVal(
                StructuredError(kind="eval", message="arity mismatch " + name)
            )
        local = dict(outer_binds)
        for (pname, _pt), arg in zip(body.params, args):
            v = evaluate(
                arg, program=program, bindings=outer_binds, granted_caps=granted_caps
            )
            if isinstance(v, ErrorVal):
                return v
            local[str(pname)] = v
        return evaluate(
            body.body, program=program, bindings=local, granted_caps=granted_caps
        )
    # Non-FN body: evaluate directly (constant def)
    return evaluate(
        body, program=program, bindings=outer_binds, granted_caps=granted_caps
    )
