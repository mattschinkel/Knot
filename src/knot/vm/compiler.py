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
    nlocals: int = 0  # total local slots (params + temps); 0 → arity


@dataclass
class ProgramImage:
    functions: dict[str, FuncInfo] = field(default_factory=dict)
    main: Chunk | None = None


@dataclass
class _LocEnv:
    """Local name → slot, with allocator for MATCH temps."""

    map: dict[str, int] = field(default_factory=dict)
    next_slot: int = 0

    @classmethod
    def from_params(cls, names: list[str]) -> "_LocEnv":
        return cls(map={n: i for i, n in enumerate(names)}, next_slot=len(names))

    def alloc(self, name: str) -> int:
        i = self.next_slot
        self.next_slot += 1
        self.map[name] = i
        return i


def compile_expr(
    expr: object,
    chunk: Chunk | None = None,
    *,
    locals_map: dict[str, int] | None = None,
) -> Chunk | ErrorVal:
    """Compile expression into chunk (creates one if needed)."""
    ch = chunk if chunk is not None else Chunk()
    env = (
        _LocEnv(map=dict(locals_map), next_slot=len(locals_map))
        if locals_map is not None
        else _LocEnv()
    )
    err = _compile(expr, ch, env)
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
            err = _compile(body, ch, _LocEnv())
            if err is not None:
                return err
            ch.emit(Op.RETURN)
            image.functions[str(item.name)] = FuncInfo(
                str(item.name), 0, ch, (), nlocals=0
            )
            continue
        local_names = [str(p[0]) for p in body.params]
        env = _LocEnv.from_params(local_names)
        ch = Chunk()
        err = _compile(body.body, ch, env)
        if err is not None:
            return err
        ch.emit(Op.RETURN)
        image.functions[str(item.name)] = FuncInfo(
            str(item.name),
            len(local_names),
            ch,
            tuple(local_names),
            nlocals=env.next_slot,
        )
    return image


def _compile(expr: object, ch: Chunk, locs: _LocEnv) -> ErrorVal | None:
    from knot.ast import HoleExpr, IdentExpr, MatchExpr, OpExpr
    from knot.runtime_ops import RUNTIME_OPS

    if isinstance(expr, LitExpr):
        return _const(ch, _lit_value(expr.value))
    if isinstance(expr, TypedLit):
        return _const(ch, _lit_value(expr.value))
    if isinstance(expr, UnitExpr):
        return _const(ch, UnitVal())
    if isinstance(expr, IdentExpr):
        name = str(expr.id)
        if name in ("true", "false"):
            return _const(ch, BoolVal(name == "true"))
        if name not in locs.map:
            return ErrorVal(
                StructuredError(kind="compile", message="unbound local " + name)
            )
        ch.emit(Op.LOAD_LOCAL, locs.map[name])
        return None
    if isinstance(expr, HoleExpr):
        ch.emit(Op.HOLE_TRAP)
        return None
    if isinstance(expr, IfExpr):
        return _compile_if(expr.cond, expr.then_branch, expr.else_branch, ch, locs)
    from knot.ast import (
        DerefExpr,
        ParExpr,
        RefExpr,
        SeqExpr,
        UnsafeExpr,
    )

    if isinstance(expr, ParExpr):
        for a in expr.branches:
            e = _compile(a, ch, locs)
            if e:
                return e
        ch.emit(Op.PAR, len(expr.branches))
        return None
    if isinstance(expr, SeqExpr):
        for a in expr.steps:
            e = _compile(a, ch, locs)
            if e:
                return e
        ch.emit(Op.SEQ, len(expr.steps))
        return None
    if isinstance(expr, RefExpr):
        e = _const(ch, StringVal(str(expr.region)))
        if e:
            return e
        e = _compile(expr.expr, ch, locs)
        if e:
            return e
        idx = ch.add_const("REF")
        ch.emit(Op.NATIVE, idx, 2)
        return None
    if isinstance(expr, DerefExpr):
        e = _compile(expr.expr, ch, locs)
        if e:
            return e
        idx = ch.add_const("DEREF")
        ch.emit(Op.NATIVE, idx, 1)
        return None
    if isinstance(expr, UnsafeExpr):
        # Caps checked at eval time; VM just runs body
        return _compile(expr.body, ch, locs)
    if isinstance(expr, OpExpr):
        op = str(expr.op)
        kids = list(expr.children or [])
        if op in ("IF", "COND") and len(kids) == 3:
            return _compile_if(kids[0], kids[1], kids[2], ch, locs)
        if op == "PAR":
            for a in kids:
                e = _compile(a, ch, locs)
                if e:
                    return e
            ch.emit(Op.PAR, len(kids))
            return None
        if op == "SEQ":
            for a in kids:
                e = _compile(a, ch, locs)
                if e:
                    return e
            ch.emit(Op.SEQ, len(kids))
            return None
        # Short-circuit AND/OR (same as evaluate)
        if op == "AND" and len(kids) == 2:
            return _compile_if(kids[0], kids[1], LitExpr(False), ch, locs)
        if op == "OR" and len(kids) == 2:
            return _compile_if(kids[0], LitExpr(True), kids[1], ch, locs)
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
        if op in RUNTIME_OPS:
            flat_kids = kids
            if op == "RECORD":
                flat_kids = []
                if kids:
                    flat_kids.append(kids[0])
                for f in kids[1:]:
                    if isinstance(f, OpExpr) and str(f.op).upper() == "FIELD":
                        fk = list(f.children or [])
                        if len(fk) != 2:
                            return ErrorVal(
                                StructuredError(
                                    kind="compile", message="FIELD[k,v] required"
                                )
                            )
                        kn, vv = fk[0], fk[1]
                        if isinstance(kn, IdentExpr):
                            flat_kids.append(LitExpr(str(kn.id)))
                        else:
                            flat_kids.append(kn)
                        flat_kids.append(vv)
                    else:
                        return ErrorVal(
                            StructuredError(
                                kind="compile", message="RECORD expects FIELD"
                            )
                        )
            elif op == "GET" and len(kids) == 2 and isinstance(kids[1], IdentExpr):
                flat_kids = [kids[0], LitExpr(str(kids[1].id))]
            for a in flat_kids:
                e = _compile(a, ch, locs)
                if e:
                    return e
            name_idx = ch.add_const(op)
            ch.emit(Op.NATIVE, name_idx, len(flat_kids))
            return None
        for a in kids:
            e = _compile(a, ch, locs)
            if e:
                return e
        idx = ch.add_const(op)
        ch.emit(Op.CALL, idx, len(kids))
        return None
    if isinstance(expr, MatchExpr):
        scr = expr.scrutinee
        if not expr.cases:
            return ErrorVal(StructuredError(kind="compile", message="empty MATCH"))
        # Evaluate scrutinee once into a temp local (avoid exponential re-eval).
        temp = "__match_" + str(locs.next_slot)
        locs.alloc(temp)
        e = _compile(scr, ch, locs)
        if e:
            return e
        ch.emit(Op.STORE_LOCAL, locs.map[temp])
        ref = IdentExpr(temp)
        tree: object | None = None
        for case in reversed(expr.cases):
            cond = OpExpr("EQ", [OpExpr("TAG", [ref]), LitExpr(case.tag)])
            body = case.body
            if case.binding:
                body = _subst_ident(body, case.binding, OpExpr("PAYLOAD", [ref]))
            if tree is None:
                tree = IfExpr(cond, body, HoleExpr(id=None))
            else:
                tree = IfExpr(cond, body, tree)
        assert tree is not None
        return _compile(tree, ch, locs)
    return ErrorVal(
        StructuredError(
            kind="compile",
            message="cannot compile " + type(expr).__name__,
        )
    )


def _subst_ident(expr: object, name: str, repl: object) -> object:
    """Replace IdentExpr(name) with repl (MATCH binding → PAYLOAD[scr])."""
    from knot.ast import CallExpr, IdentExpr, IfExpr, MatchCase, MatchExpr, OpExpr

    if isinstance(expr, IdentExpr):
        return repl if str(expr.id) == name else expr
    if isinstance(expr, OpExpr):
        return OpExpr(
            expr.op,
            [_subst_ident(c, name, repl) for c in (expr.children or [])],
            id=getattr(expr, "id", None),
        )
    if isinstance(expr, CallExpr):
        return CallExpr(
            _subst_ident(expr.fn, name, repl),
            [_subst_ident(a, name, repl) for a in (expr.args or [])],
        )
    if isinstance(expr, IfExpr):
        return IfExpr(
            _subst_ident(expr.cond, name, repl),
            _subst_ident(expr.then_branch, name, repl),
            _subst_ident(expr.else_branch, name, repl),
        )
    if isinstance(expr, MatchExpr):
        cases = []
        for c in expr.cases:
            if c.binding == name:
                cases.append(c)  # shadowed
            else:
                cases.append(
                    MatchCase(
                        c.tag,
                        _subst_ident(c.body, name, repl),
                        binding=c.binding,
                    )
                )
        return MatchExpr(
            _subst_ident(expr.scrutinee, name, repl),
            cases,
            id=getattr(expr, "id", None),
        )
    return expr


def _compile_if(cond, then_b, else_b, ch, locs: _LocEnv) -> ErrorVal | None:
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
}
