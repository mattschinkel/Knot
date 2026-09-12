"""AST → bytecode (deterministic lowering, Phase 9)."""

from __future__ import annotations

from dataclasses import dataclass, field

from knot.ast import (
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
from knot.errors import StructuredError
from knot.values import BoolVal, ErrorVal, FloatVal, IntVal, StringVal, UnitVal, Value
from knot.vm.chunk import Chunk
from knot.vm.opcode import Op


@dataclass
class FuncInfo:
    name: str
    arity: int
    chunk: Chunk
    local_names: tuple[str, ...]


@dataclass
class ProgramImage:
    functions: dict[str, FuncInfo] = field(default_factory=dict)
    main: Chunk | None = None


def compile_expr(
    expr: object,
    chunk: Chunk | None = None,
    *,
    locals_map: dict[str, int] | None = None,
) -> Chunk | ErrorVal:
    """Compile expression into chunk (creates one if needed)."""
    ch = chunk if chunk is not None else Chunk()
    locs = locals_map if locals_map is not None else {}
    err = _compile(expr, ch, locs)
    if err is not None:
        return err
    return ch


def compile_program(items: list | object) -> ProgramImage | ErrorVal:
    """Compile DEF[name, FN[[params],body]] entries into ProgramImage."""
    seq = items if isinstance(items, list) else [items]
    image = ProgramImage()
    for item in seq:
        if not isinstance(item, DefNode):
            continue
        body = item.body
        if not isinstance(body, FnExpr):
            # constant def: zero-arg function returning body
            ch = Chunk()
            err = _compile(body, ch, {})
            if err is not None:
                return err
            ch.emit(Op.RETURN)
            image.functions[str(item.name)] = FuncInfo(
                str(item.name), 0, ch, ()
            )
            continue
        local_names = [str(p[0]) for p in body.params]
        locs = {n: i for i, n in enumerate(local_names)}
        ch = Chunk()
        err = _compile(body.body, ch, locs)
        if err is not None:
            return err
        ch.emit(Op.RETURN)
        image.functions[str(item.name)] = FuncInfo(
            str(item.name), len(local_names), ch, tuple(local_names)
        )
    return image


def _compile(expr: object, ch: Chunk, locs: dict[str, int]) -> ErrorVal | None:
    if isinstance(expr, LitExpr):
        return _const(ch, _lit_value(expr.value))
    if isinstance(expr, TypedLit):
        return _const(ch, _lit_value(expr.value))
    if isinstance(expr, UnitExpr):
        return _const(ch, UnitVal())
    if isinstance(expr, IdentExpr):
        name = str(expr.id)
        if name not in locs:
            return ErrorVal(
                StructuredError(kind="compile", message="unbound local " + name)
            )
        ch.emit(Op.LOAD_LOCAL, locs[name])
        return None
    if isinstance(expr, HoleExpr):
        ch.emit(Op.HOLE_TRAP)
        return None
    if isinstance(expr, IfExpr):
        return _compile_if(expr.cond, expr.then_branch, expr.else_branch, ch, locs)
    if isinstance(expr, OpExpr):
        op = str(expr.op)
        kids = list(expr.children or [])
        if op in ("IF", "COND") and len(kids) == 3:
            return _compile_if(kids[0], kids[1], kids[2], ch, locs)
        if op in _BIN_OPS and len(kids) == 2:
            e = _compile(kids[0], ch, locs)
            if e:
                return e
            e = _compile(kids[1], ch, locs)
            if e:
                return e
            ch.emit(_BIN_OPS[op])
            return None
        if op == "NEG" and len(kids) == 1:
            e = _compile(kids[0], ch, locs)
            if e:
                return e
            ch.emit(Op.NEG)
            return None
        if op == "NOT" and len(kids) == 1:
            e = _compile(kids[0], ch, locs)
            if e:
                return e
            ch.emit(Op.NOT)
            return None
        # User call: name[args]
        e = None
        for a in kids:
            e = _compile(a, ch, locs)
            if e:
                return e
        idx = ch.add_const(op)
        ch.emit(Op.CALL, idx, len(kids))
        return None
    return ErrorVal(
        StructuredError(
            kind="compile",
            message="cannot compile " + type(expr).__name__,
        )
    )


def _compile_if(cond, then_b, else_b, ch, locs) -> ErrorVal | None:
    e = _compile(cond, ch, locs)
    if e:
        return e
    ch.emit(Op.JUMP_IF_FALSE, 0)  # patch
    jmp_false_at = len(ch) - 1
    e = _compile(then_b, ch, locs)
    if e:
        return e
    ch.emit(Op.JUMP, 0)
    jmp_end_at = len(ch) - 1
    else_ip = len(ch)
    ch.patch(jmp_false_at, else_ip)
    e = _compile(else_b, ch, locs)
    if e:
        return e
    ch.patch(jmp_end_at, len(ch))
    return None


def _const(ch: Chunk, value: Value) -> None:
    idx = ch.add_const(value)
    ch.emit(Op.LOAD_CONST, idx)
    return None


def _lit_value(v) -> Value:
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
    return StringVal(str(v))


_BIN_OPS = {
    "ADD": Op.ADD,
    "SUB": Op.SUB,
    "MUL": Op.MUL,
    "DIV": Op.DIV,
    "MOD": Op.MOD,
    "EQ": Op.EQ,
    "NE": Op.NE,
    "LT": Op.LT,
    "LE": Op.LE,
    "GT": Op.GT,
    "GE": Op.GE,
    "AND": Op.AND,
    "OR": Op.OR,
}
