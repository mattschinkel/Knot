"""Prefer Stage-1 golemc for deterministic AIR → bytecode when supported."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from golem.errors import StructuredError
from golem.parser import parse_program
from golem.values import ErrorVal, StringVal, SumVal, Value
from golem.vm.compiler import ProgramImage, compile_program
from golem.vm.machine import VM

_STAGE1 = Path(__file__).resolve().parents[2] / "selfhost" / "stage1"
_ROOT = Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def host_golemc_image() -> ProgramImage | ErrorVal:
    """Host-compile Stage-1 sources once (cached)."""
    from selfhost.harness.compile_stage1 import resolve_stage1_imports

    nodes: list = []
    for name in resolve_stage1_imports():
        path = _STAGE1 / name
        if not path.is_file():
            return ErrorVal(
                StructuredError(kind="golemc", message="missing " + str(path))
            )
        text = "\n".join(
            ln
            for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().upper().startswith("REM")
        )
        nodes.extend(parse_program(text))
    return compile_program(nodes)


def invalidate_golemc_cache() -> None:
    host_golemc_image.cache_clear()


def golemc_vm(granted_caps=None) -> VM | ErrorVal:
    """Bootstrapped Stage-1 golemc VM (host-compiled image)."""
    img = host_golemc_image()
    if isinstance(img, ErrorVal):
        return img
    return VM(img, granted_caps=granted_caps)


def compile_with_golemc(source: str, *, granted_caps=None) -> ProgramImage | ErrorVal:
    """Compile AIR source via Stage-1 golemc bytecode image."""
    vm = golemc_vm(granted_caps=granted_caps)
    if isinstance(vm, ErrorVal):
        return vm
    result = vm.call("compile_source", [StringVal(source)])
    if isinstance(result, ErrorVal):
        return result
    if not isinstance(result, SumVal) or result.tag != "Program":
        return ErrorVal(
            StructuredError(kind="golemc", message="expected Program from golemc")
        )
    return _program_from_sum(result)


def compile_path_with_golemc(path: str | Path, *, granted_caps=None) -> ProgramImage | ErrorVal:
    """Compile a .gol file (single source; IMPORT not expanded)."""
    text = Path(path).read_text(encoding="utf-8")
    return compile_with_golemc(text, granted_caps=granted_caps)


def compile_root_with_golemc(
    directory: str | Path,
    root: str = "root.gol",
    *,
    granted_caps=None,
) -> ProgramImage | ErrorVal:
    """Compile IMPORT graph via golemc ``compile_root`` (needs fs.read)."""
    from golem.effects import Capability, CapabilitySet

    caps = granted_caps
    if caps is None:
        caps = CapabilitySet([Capability.FS_READ])
    vm = golemc_vm(granted_caps=caps)
    if isinstance(vm, ErrorVal):
        return vm
    result = vm.call(
        "compile_root",
        [StringVal(str(Path(directory).resolve())), StringVal(root)],
    )
    if isinstance(result, ErrorVal):
        return result
    if not isinstance(result, SumVal) or result.tag != "Program":
        return ErrorVal(
            StructuredError(kind="golemc", message="expected Program from compile_root")
        )
    return _program_from_sum(result)


def run_with_golemc(
    source: str,
    *,
    entry: str = "__main",
    args: list[Value] | None = None,
    granted_caps=None,
    host_fallback: bool = False,
) -> Value:
    """Compile source with golemc and call ``entry``."""
    img = (
        compile_prefer_golemc(source, granted_caps=granted_caps)
        if host_fallback
        else compile_with_golemc(source, granted_caps=granted_caps)
    )
    if isinstance(img, ErrorVal):
        return img
    return VM(img, granted_caps=granted_caps).call(entry, list(args or []))


def rebuild_golemc(
    stage_dir: str | Path | None = None,
    *,
    probe: str = "ADD[1,1]",
) -> SumVal | ErrorVal:
    """Self-host rebuild loop implemented in Golem (``rebuild_roundtrip``).

    Bootstraps host golemc once, then runs Golem ``rebuild_roundtrip`` which
    ``compile_root``s stage1 and ``CALL_PROGRAM``s the new image on ``probe``.
    """
    from golem.effects import Capability, CapabilitySet

    d = Path(stage_dir) if stage_dir else _STAGE1
    caps = CapabilitySet([Capability.FS_READ])
    vm = golemc_vm(granted_caps=caps)
    if isinstance(vm, ErrorVal):
        return vm
    return vm.call(
        "rebuild_roundtrip",
        [StringVal(str(d.resolve())), StringVal(probe)],
    )


def _program_from_sum(result: SumVal) -> ProgramImage | ErrorVal:
    from golem.values import IntVal, ListVal, StringVal
    from golem.vm.chunk import Chunk
    from golem.vm.compiler import FuncInfo
    from golem.vm.opcode import Op

    funcs = result.payload
    if not isinstance(funcs, ListVal):
        return ErrorVal(StructuredError(kind="golemc", message="bad program"))
    image = ProgramImage()
    for item in funcs.items:
        if not isinstance(item, SumVal) or item.tag != "Func":
            return ErrorVal(StructuredError(kind="golemc", message="bad Func"))
        pack = item.payload
        if not isinstance(pack, ListVal) or len(pack.items) != 4:
            return ErrorVal(StructuredError(kind="golemc", message="bad Func pack"))
        name_v, arity_v, code_v, consts_v = pack.items
        name = str(name_v.value) if isinstance(name_v, StringVal) else str(name_v)
        if not isinstance(arity_v, IntVal):
            return ErrorVal(StructuredError(kind="golemc", message="arity"))
        if not isinstance(code_v, ListVal) or not isinstance(consts_v, ListVal):
            return ErrorVal(StructuredError(kind="golemc", message="code/consts"))
        code = [c.value for c in code_v.items if isinstance(c, IntVal)]
        if len(code) != len(code_v.items):
            return ErrorVal(StructuredError(kind="golemc", message="code not int"))
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
            elif op in (Op.CALL, Op.NATIVE, Op.PAR, Op.SEQ):
                if op in (Op.PAR, Op.SEQ):
                    i += 1
                else:
                    i += 2
        nlocals = max(arity_v.value, hi + 1)
        image.functions[name] = FuncInfo(name, arity_v.value, ch, (), nlocals=nlocals)
        if name == "__main":
            image.main = ch
    return image


def compile_prefer_golemc(source: str, *, granted_caps=None) -> ProgramImage | ErrorVal:
    """Try golemc; on failure fall back to host compile_program of parse_program."""
    kn = compile_with_golemc(source, granted_caps=granted_caps)
    if not isinstance(kn, ErrorVal):
        return kn
    nodes = parse_program(source)
    return compile_program(nodes)
