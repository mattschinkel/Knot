"""Golem bytecode VM public API (Phase 9)."""

from __future__ import annotations

import statistics
import time

from golem.ast import DefNode
from golem.parser import parse_expr
from golem.values import ErrorVal, IntVal, Value
from golem.vm.chunk import Chunk
from golem.vm.compiler import ProgramImage, compile_expr, compile_program
from golem.vm.machine import VM
from golem.vm.opcode import Op

__all__ = [
    "Chunk",
    "Op",
    "ProgramImage",
    "VM",
    "compile_expr",
    "compile_program",
    "run",
    "measure_m5",
]


def run(
    expr_or_program: object,
    *,
    call: str | None = None,
    args: list[Value] | None = None,
    granted_caps=None,
) -> Value:
    """Compile and execute. If call= is set, treat input as program of DEFs."""
    if call is not None:
        items = (
            expr_or_program
            if isinstance(expr_or_program, list)
            else [expr_or_program]
        )
        image = compile_program(items)
        if isinstance(image, ErrorVal):
            return image
        return VM(image, granted_caps=granted_caps).call(call, list(args or []))
    ch = compile_expr(expr_or_program)
    if isinstance(ch, ErrorVal):
        return ch
    return VM(ProgramImage(), granted_caps=granted_caps).run_chunk(ch)


def measure_m5(*, warmup: int = 3, runs: int = 21) -> float:
    """Median ms for compile_program + call on fixed suite (Phase 9 D5)."""
    src = [
        parse_expr("DEF[square,FN[[x:i32],MUL[x,x]]]"),
        parse_expr("DEF[add,FN[[a:i32,b:i32],ADD[a,b]]]"),
    ]

    def once() -> None:
        image = compile_program(src)
        assert not isinstance(image, ErrorVal)
        vm = VM(image)
        r = vm.call("square", [IntVal(32, 12)])
        assert isinstance(r, IntVal) and r.value == 144
        r2 = vm.call("add", [IntVal(32, 2), IntVal(32, 3)])
        assert isinstance(r2, IntVal) and r2.value == 5

    for _ in range(warmup):
        once()
    samples = []
    for _ in range(runs):
        t0 = time.perf_counter()
        once()
        samples.append((time.perf_counter() - t0) * 1000.0)
    return float(statistics.median(samples))
