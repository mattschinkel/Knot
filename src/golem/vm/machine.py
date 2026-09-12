"""Stack virtual machine (Phase 9)."""

from __future__ import annotations

from dataclasses import dataclass, field

from golem.errors import StructuredError
from golem.values import (
    BoolVal,
    ErrorVal,
    FloatVal,
    IntVal,
    StringVal,
    Value,
)
from golem.vm.chunk import Chunk
from golem.vm.compiler import FuncInfo, ProgramImage
from golem.vm.opcode import Op


def _name_from_const(c: object) -> str:
    if isinstance(c, StringVal):
        return c.value
    return str(c)


@dataclass
class Frame:
    chunk: Chunk
    ip: int = 0
    locals: list[Value] = field(default_factory=list)
    stack_base: int = 0


class VM:
    def __init__(self, image: ProgramImage | None = None, granted_caps=None) -> None:
        self.image = image or ProgramImage()
        self.stack: list[Value] = []
        self.frames: list[Frame] = []
        self.granted_caps = granted_caps

    def run_chunk(self, chunk: Chunk, *, arity_locals: int = 0) -> Value:
        self.stack.clear()
        self.frames = [Frame(chunk=chunk, locals=[None] * arity_locals)]  # type: ignore
        return self._interpret()

    def call(self, name: str, args: list[Value]) -> Value:
        fn = self.image.functions.get(name)
        if fn is None:
            return ErrorVal(
                StructuredError(kind="vm", message="unknown function " + name)
            )
        if len(args) != fn.arity:
            return ErrorVal(
                StructuredError(kind="vm", message="arity mismatch " + name)
            )
        self.stack.clear()
        nlocals = fn.nlocals if fn.nlocals else fn.arity
        if nlocals < len(args):
            nlocals = len(args)
        frame_locals: list = list(args) + [None] * (nlocals - len(args))
        self.frames = [Frame(chunk=fn.chunk, locals=frame_locals)]
        return self._interpret()

    def _interpret(self) -> Value:
        while self.frames:
            frame = self.frames[-1]
            ch = frame.chunk
            if frame.ip >= len(ch.code):
                # implicit return top or unit error
                if self.stack:
                    return self.stack.pop()
                return ErrorVal(
                    StructuredError(kind="vm", message="fell off end")
                )
            op = ch.code[frame.ip]
            frame.ip += 1
            if op == Op.LOAD_CONST:
                idx = ch.code[frame.ip]
                frame.ip += 1
                self.stack.append(ch.constants[idx])  # type: ignore
            elif op == Op.LOAD_LOCAL:
                idx = ch.code[frame.ip]
                frame.ip += 1
                self.stack.append(frame.locals[idx])
            elif op == Op.STORE_LOCAL:
                idx = ch.code[frame.ip]
                frame.ip += 1
                frame.locals[idx] = self.stack.pop()
            elif op == Op.ADD:
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(_arith("ADD", a, b))
            elif op == Op.SUB:
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(_arith("SUB", a, b))
            elif op == Op.MUL:
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(_arith("MUL", a, b))
            elif op == Op.DIV:
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(_arith("DIV", a, b))
            elif op == Op.MOD:
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(_arith("MOD", a, b))
            elif op == Op.NEG:
                a = self.stack.pop()
                if isinstance(a, IntVal):
                    self.stack.append(IntVal(a.bits, -a.value))
                elif isinstance(a, FloatVal):
                    self.stack.append(FloatVal(a.bits, -a.value))
                else:
                    return ErrorVal(
                        StructuredError(kind="vm", op="NEG", message="bad")
                    )
            elif op in (Op.EQ, Op.NE, Op.LT, Op.LE, Op.GT, Op.GE):
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(_cmp(op, a, b))
            elif op == Op.NOT:
                a = self.stack.pop()
                if isinstance(a, BoolVal):
                    self.stack.append(BoolVal(not a.value))
                else:
                    return ErrorVal(
                        StructuredError(kind="vm", op="NOT", message="bad")
                    )
            elif op == Op.AND:
                b, a = self.stack.pop(), self.stack.pop()
                if isinstance(a, BoolVal) and isinstance(b, BoolVal):
                    self.stack.append(BoolVal(a.value and b.value))
                else:
                    return ErrorVal(
                        StructuredError(kind="vm", op="AND", message="bad")
                    )
            elif op == Op.OR:
                b, a = self.stack.pop(), self.stack.pop()
                if isinstance(a, BoolVal) and isinstance(b, BoolVal):
                    self.stack.append(BoolVal(a.value or b.value))
                else:
                    return ErrorVal(
                        StructuredError(kind="vm", op="OR", message="bad")
                    )
            elif op == Op.JUMP:
                target = ch.code[frame.ip]
                frame.ip = target
            elif op == Op.JUMP_IF_FALSE:
                target = ch.code[frame.ip]
                frame.ip += 1
                cond = self.stack.pop()
                if isinstance(cond, ErrorVal):
                    return cond
                if not (isinstance(cond, BoolVal) and cond.value):
                    frame.ip = target
            elif op == Op.CALL:
                name_idx = ch.code[frame.ip]
                frame.ip += 1
                arity = ch.code[frame.ip]
                frame.ip += 1
                name = _name_from_const(ch.constants[name_idx])
                fn = self.image.functions.get(name)
                if fn is None:
                    return ErrorVal(
                        StructuredError(
                            kind="vm", message="unknown function " + name
                        )
                    )
                if arity != fn.arity:
                    return ErrorVal(
                        StructuredError(
                            kind="vm", message="arity mismatch " + name
                        )
                    )
                args = [self.stack.pop() for _ in range(arity)]
                args.reverse()
                # Check for ErrorVal in args
                for a in args:
                    if isinstance(a, ErrorVal):
                        return a
                nlocals = fn.nlocals if fn.nlocals else fn.arity
                if nlocals < arity:
                    nlocals = arity
                frame_locals: list = list(args) + [None] * (nlocals - arity)
                self.frames.append(Frame(chunk=fn.chunk, locals=frame_locals))
            elif op == Op.RETURN:
                ret = self.stack.pop() if self.stack else ErrorVal(
                    StructuredError(kind="vm", message="empty return")
                )
                self.frames.pop()
                if not self.frames:
                    return ret
                self.stack.append(ret)
            elif op == Op.POP:
                if self.stack:
                    self.stack.pop()
            elif op == Op.HOLE_TRAP:
                return ErrorVal(
                    StructuredError(
                        kind="hole_trap", message="VM reached a hole"
                    )
                )
            elif op == Op.NATIVE:
                name_idx = ch.code[frame.ip]
                frame.ip += 1
                arity = ch.code[frame.ip]
                frame.ip += 1
                name = _name_from_const(ch.constants[name_idx])
                args = [self.stack.pop() for _ in range(arity)]
                args.reverse()
                for a in args:
                    if isinstance(a, ErrorVal):
                        return a
                from golem.runtime_ops import eval_op

                result = eval_op(name, args, granted=self.granted_caps)
                if isinstance(result, ErrorVal):
                    return result
                self.stack.append(result)
            elif op == Op.PAR:
                arity = ch.code[frame.ip]
                frame.ip += 1
                args = [self.stack.pop() for _ in range(arity)]
                args.reverse()
                for a in args:
                    if isinstance(a, ErrorVal):
                        return a
                from golem.values import TupleVal

                types = tuple(a.type for a in args)
                self.stack.append(TupleVal(tuple(args), types))
            elif op == Op.SEQ:
                arity = ch.code[frame.ip]
                frame.ip += 1
                args = [self.stack.pop() for _ in range(arity)]
                args.reverse()
                for a in args:
                    if isinstance(a, ErrorVal):
                        return a
                from golem.values import UnitVal

                self.stack.append(args[-1] if args else UnitVal())
            else:
                return ErrorVal(
                    StructuredError(kind="vm", message="unknown opcode " + str(op))
                )
            # propagate ErrorVal left on stack from arith
            if self.stack and isinstance(self.stack[-1], ErrorVal):
                return self.stack[-1]
        return ErrorVal(StructuredError(kind="vm", message="no frames"))


def _arith(op: str, a: Value, b: Value) -> Value:
    if isinstance(a, ErrorVal):
        return a
    if isinstance(b, ErrorVal):
        return b
    if isinstance(a, IntVal) and isinstance(b, IntVal):
        if op == "ADD":
            return IntVal(a.bits, a.value + b.value)
        if op == "SUB":
            return IntVal(a.bits, a.value - b.value)
        if op == "MUL":
            return IntVal(a.bits, a.value * b.value)
        if op == "DIV":
            if b.value == 0:
                return ErrorVal(
                    StructuredError(kind="vm", op=op, message="div0")
                )
            return IntVal(a.bits, a.value // b.value)
        if op == "MOD":
            if b.value == 0:
                return ErrorVal(
                    StructuredError(kind="vm", op=op, message="mod0")
                )
            return IntVal(a.bits, a.value % b.value)
    return ErrorVal(StructuredError(kind="vm", op=op, message="bad operands"))


def _cmp(op: int, a: Value, b: Value) -> Value:
    if isinstance(a, ErrorVal):
        return a
    if isinstance(b, ErrorVal):
        return b
    if isinstance(a, IntVal) and isinstance(b, IntVal):
        x, y = a.value, b.value
    elif isinstance(a, StringVal) and isinstance(b, StringVal) and op in (Op.EQ, Op.NE):
        x, y = a.value, b.value
    else:
        return ErrorVal(StructuredError(kind="vm", message="bad cmp"))
    if op == Op.EQ:
        return BoolVal(x == y)
    if op == Op.NE:
        return BoolVal(x != y)
    if op == Op.LT:
        return BoolVal(x < y)
    if op == Op.LE:
        return BoolVal(x <= y)
    if op == Op.GT:
        return BoolVal(x > y)
    if op == Op.GE:
        return BoolVal(x >= y)
    return ErrorVal(StructuredError(kind="vm", message="bad cmp op"))
