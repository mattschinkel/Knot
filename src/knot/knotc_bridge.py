"""Prefer Stage-1 knotc for deterministic AIR → bytecode when supported."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from knot.errors import StructuredError
from knot.parser import parse_program
from knot.values import ErrorVal, StringVal, SumVal, Value
from knot.vm.compiler import ProgramImage, compile_program
from knot.vm.machine import VM

_STAGE1 = Path(__file__).resolve().parents[2] / "selfhost" / "stage1"


@lru_cache(maxsize=1)
def host_knotc_image() -> ProgramImage | ErrorVal:
    """Host-compile Stage-1 sources once (cached)."""
    from selfhost.harness.compile_stage1 import resolve_stage1_imports

    nodes: list = []
    for name in resolve_stage1_imports():
        path = _STAGE1 / name
        if not path.is_file():
            return ErrorVal(
                StructuredError(kind="knotc", message="missing " + str(path))
            )
        text = "\n".join(
            ln
            for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().upper().startswith("REM")
        )
        nodes.extend(parse_program(text))
    return compile_program(nodes)


def compile_with_knotc(source: str) -> ProgramImage | ErrorVal:
    """Compile AIR source via Stage-1 knotc bytecode image."""
    img = host_knotc_image()
    if isinstance(img, ErrorVal):
        return img
    result = VM(img).call("compile_source", [StringVal(source)])
    if isinstance(result, ErrorVal):
        return result
    if not isinstance(result, SumVal) or result.tag != "Program":
        return ErrorVal(
            StructuredError(kind="knotc", message="expected Program from knotc")
        )
    return _program_from_sum(result)


def _program_from_sum(result: SumVal) -> ProgramImage | ErrorVal:
    from knot.values import IntVal, ListVal, StringVal
    from knot.vm.chunk import Chunk
    from knot.vm.compiler import FuncInfo
    from knot.vm.opcode import Op

    funcs = result.payload
    if not isinstance(funcs, ListVal):
        return ErrorVal(StructuredError(kind="knotc", message="bad program"))
    image = ProgramImage()
    for item in funcs.items:
        if not isinstance(item, SumVal) or item.tag != "Func":
            return ErrorVal(StructuredError(kind="knotc", message="bad Func"))
        pack = item.payload
        if not isinstance(pack, ListVal) or len(pack.items) != 4:
            return ErrorVal(StructuredError(kind="knotc", message="bad Func pack"))
        name_v, arity_v, code_v, consts_v = pack.items
        name = str(name_v.value) if isinstance(name_v, StringVal) else str(name_v)
        if not isinstance(arity_v, IntVal):
            return ErrorVal(StructuredError(kind="knotc", message="arity"))
        if not isinstance(code_v, ListVal) or not isinstance(consts_v, ListVal):
            return ErrorVal(StructuredError(kind="knotc", message="code/consts"))
        code = [c.value for c in code_v.items if isinstance(c, IntVal)]
        if len(code) != len(code_v.items):
            return ErrorVal(StructuredError(kind="knotc", message="code not int"))
        ch = Chunk(code=code, constants=list(consts_v.items))
        hi = -1
        i = 0
        while i < len(code):
            op = code[i]
            i += 1
            if op in (Op.LOAD_CONST, Op.LOAD_LOCAL, Op.STORE_LOCAL, Op.JUMP, Op.JUMP_IF_FALSE):
                if i < len(code) and op in (Op.LOAD_LOCAL, Op.STORE_LOCAL):
                    hi = max(hi, code[i])
                i += 1
            elif op in (Op.CALL, Op.NATIVE):
                i += 2
        nlocals = max(arity_v.value, hi + 1)
        image.functions[name] = FuncInfo(name, arity_v.value, ch, (), nlocals=nlocals)
        if name == "__main":
            image.main = ch
    return image


def compile_prefer_knotc(source: str) -> ProgramImage | ErrorVal:
    """Try knotc; on failure fall back to host compile_program of parse_program."""
    kn = compile_with_knotc(source)
    if not isinstance(kn, ErrorVal):
        return kn
    nodes = parse_program(source)
    return compile_program(nodes)
