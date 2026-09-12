"""Stage 2 self-host gate.

Stage 0 host-compiles Stage-1 golemc to bytecode; that image compiles
fixtures and the Stage-1 sources themselves (Golem compiling Golem).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from golem.parser import parse_expr, parse_program
from golem.partial import evaluate
from golem.values import ErrorVal, IntVal, StringVal, SumVal
from golem.vm.compiler import compile_program
from golem.vm.machine import VM
from selfhost.harness.compile_stage1 import (
    FIXTURES,
    STAGE1,
    chunk_from_sum,
    compile_air_source,
    load_stage1_program,
    program_from_sum,
    resolve_stage1_imports,
    run_chunk,
    run_func,
)


def _stage1_files():
    return resolve_stage1_imports()


def _host_golemc() -> VM:
    nodes = []
    for name in _stage1_files():
        text = (STAGE1 / name).read_text(encoding="utf-8")
        lines = [
            ln
            for ln in text.splitlines()
            if ln.strip() and not ln.strip().upper().startswith("REM")
        ]
        nodes.extend(parse_program("\n".join(lines)))
    img = compile_program(nodes)
    assert not isinstance(img, ErrorVal), img
    return VM(img)


def _stage1_source(name: str) -> str:
    text = (STAGE1 / name).read_text(encoding="utf-8")
    return "\n".join(
        ln
        for ln in text.splitlines()
        if ln.strip() and not ln.strip().upper().startswith("REM")
    )


def _chunk_parts(chunk_sum):
    ch = chunk_from_sum(chunk_sum)
    assert not isinstance(ch, ErrorVal), ch
    return list(ch.code), list(ch.constants)


def test_stage2_stable_chunk():
    prog = load_stage1_program()
    src = (FIXTURES / "expr_muladd.gol").read_text(encoding="utf-8").strip()
    a = compile_air_source(prog, src)
    b = compile_air_source(prog, src)
    assert _chunk_parts(a) == _chunk_parts(b)


def test_stage2_matches_host_eval():
    prog = load_stage1_program()
    src = "ADD[10,32]"
    host = evaluate(parse_expr(src))
    kn = run_chunk(chunk_from_sum(compile_air_source(prog, src)))
    assert isinstance(host, IntVal) and isinstance(kn, IntVal)
    assert host.value == kn.value == 42


def test_stage2_vm_golemc_square_fact():
    vm = _host_golemc()
    for path, name, arg, expect in [
        (FIXTURES / "square.gol", "square", 7, 49),
        (FIXTURES / "fact.gol", "fact", 5, 120),
    ]:
        src = path.read_text(encoding="utf-8").strip()
        result = vm.call("compile_source", [StringVal(src)])
        assert isinstance(result, SumVal) and result.tag == "Program", result
        img = program_from_sum(result)
        assert not isinstance(img, ErrorVal), img
        out = run_func(img, name, [IntVal(32, arg)])
        assert isinstance(out, IntVal) and out.value == expect, (name, out)


def test_stage2_vm_golemc_compiles_stage1_sources():
    """Host-compiled golemc compiles each Stage-1 .gol file to a Program."""
    vm = _host_golemc()
    total = 0
    for name in _stage1_files():
        result = vm.call("compile_source", [StringVal(_stage1_source(name))])
        assert isinstance(result, SumVal) and result.tag == "Program", (name, result)
        total += len(result.payload.items)
    assert total >= 60


def test_stage2_self_compile_roundtrip_square():
    """golemc compiles itself; the resulting image compiles square → 49."""
    vm0 = _host_golemc()
    combined = "\n".join(_stage1_source(n) for n in _stage1_files())
    built = vm0.call("compile_source", [StringVal(combined)])
    assert isinstance(built, SumVal) and built.tag == "Program", built
    assert len(built.payload.items) >= 60
    img1 = program_from_sum(built)
    assert not isinstance(img1, ErrorVal), img1
    vm1 = VM(img1)
    src = (FIXTURES / "square.gol").read_text(encoding="utf-8").strip()
    result = vm1.call("compile_source", [StringVal(src)])
    assert isinstance(result, SumVal) and result.tag == "Program", result
    out = run_func(program_from_sum(result), "square", [IntVal(32, 7)])
    assert isinstance(out, IntVal) and out.value == 49


def test_stage2_self_compile_fact_and_hole():
    vm0 = _host_golemc()
    combined = "\n".join(_stage1_source(n) for n in _stage1_files())
    vm1 = VM(program_from_sum(vm0.call("compile_source", [StringVal(combined)])))
    fact = vm1.call(
        "compile_source",
        [StringVal((FIXTURES / "fact.gol").read_text(encoding="utf-8").strip())],
    )
    assert isinstance(fact, SumVal) and fact.tag == "Program", fact
    assert run_func(program_from_sum(fact), "fact", [IntVal(32, 4)]).value == 24
    hole = vm1.call("compile_source", [StringVal("?")])
    assert isinstance(hole, SumVal) and hole.tag == "Program", hole
    out = run_chunk(chunk_from_sum(hole))
    assert isinstance(out, ErrorVal) and out.err.kind == "hole_trap"


def test_stage2_match_and_import_parse():
    prog = load_stage1_program()
    src = "MATCH[SUM['A',1],CASE[A,x,x],CASE[B,0]]"
    result = compile_air_source(prog, src)
    assert not isinstance(result, ErrorVal), result
    out = run_chunk(chunk_from_sum(result))
    assert isinstance(out, IntVal) and out.value == 1
    from selfhost.harness.compile_stage1 import _call_def_values

    ast = _call_def_values(
        prog, "parse", [_call_def_values(prog, "lex", [StringVal("IMPORT[lexer]")])]
    )
    assert isinstance(ast, SumVal) and ast.tag == "Prog"
