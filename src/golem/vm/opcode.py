"""Bytecode opcodes for the Golem stack VM (Phase 9)."""

from __future__ import annotations

from enum import IntEnum


class Op(IntEnum):
    LOAD_CONST = 1
    LOAD_LOCAL = 2
    STORE_LOCAL = 3
    ADD = 10
    SUB = 11
    MUL = 12
    DIV = 13
    MOD = 14
    NEG = 15
    EQ = 20
    NE = 21
    LT = 22
    LE = 23
    GT = 24
    GE = 25
    NOT = 26
    AND = 27
    OR = 28
    JUMP = 30
    JUMP_IF_FALSE = 31
    CALL = 40  # operand: const index of function name (str)
    RETURN = 41
    POP = 50
    HOLE_TRAP = 60
    NATIVE = 70  # next: const_idx of op name (str), then arity
    PAR = 80  # next: arity N; pop N values → TupleVal (source order)
    SEQ = 81  # next: arity N; pop N values, keep last (or unit)
