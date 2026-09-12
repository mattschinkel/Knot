"""Stage 1 harness tests."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from golem.values import ErrorVal, IntVal, ListVal, StringVal, SumVal
from selfhost.harness.compile_stage1 import (
    FIXTURES,
    _call_def_values,
    chunk_from_sum,
    compile_air_source,
    load_stage1_program,
    program_from_sum,
    run_chunk,
    run_func,
)


def test_load_stage1():
    prog = load_stage1_program()
    assert any(getattr(n, "name", None) == "lex" for n in prog)
    assert any(getattr(n, "name", None) == "compile_source" for n in prog)


def test_lex_add():
    prog = load_stage1_program()
    toks = _call_def_values(prog, "lex", [StringVal("ADD[1,2]")])
    assert isinstance(toks, ListVal)
    tags = [t.tag for t in toks.items if isinstance(t, SumVal)]
    assert tags[0] == "Ident"
    assert "Num" in tags
    assert tags[-1] == "Eof"


def test_compile_muladd_fixture():
    prog = load_stage1_program()
    src = (FIXTURES / "expr_muladd.gol").read_text(encoding="utf-8").strip()
    result = compile_air_source(prog, src)
    assert not isinstance(result, ErrorVal), result
    ch = chunk_from_sum(result)
    assert not isinstance(ch, ErrorVal), ch
    out = run_chunk(ch)
    assert isinstance(out, IntVal) and out.value == 20


def test_lex_number():
    prog = load_stage1_program()
    toks = _call_def_values(prog, "lex", [StringVal("42")])
    assert isinstance(toks, ListVal)
    assert isinstance(toks.items[0], SumVal)
    assert toks.items[0].tag == "Num"
    assert toks.items[0].payload.value == 42


def test_lex_number_three_digits():
    prog = load_stage1_program()
    toks = _call_def_values(prog, "lex", [StringVal("122")])
    assert isinstance(toks, ListVal)
    assert toks.items[0].tag == "Num"
    assert toks.items[0].payload.value == 122


def test_compile_square():
    prog = load_stage1_program()
    src = (FIXTURES / "square.gol").read_text(encoding="utf-8").strip()
    result = compile_air_source(prog, src)
    assert not isinstance(result, ErrorVal), result
    img = program_from_sum(result)
    assert not isinstance(img, ErrorVal), img
    out = run_func(img, "square", [IntVal(32, 7)])
    assert isinstance(out, IntVal) and out.value == 49


def test_compile_fact():
    prog = load_stage1_program()
    src = (FIXTURES / "fact.gol").read_text(encoding="utf-8").strip()
    result = compile_air_source(prog, src)
    assert not isinstance(result, ErrorVal), result
    img = program_from_sum(result)
    assert not isinstance(img, ErrorVal), img
    out = run_func(img, "fact", [IntVal(32, 5)])
    assert isinstance(out, IntVal) and out.value == 120


def test_lex_hole_and_float():
    prog = load_stage1_program()
    toks = _call_def_values(prog, "lex", [StringVal("?:i32 1.5")])
    assert isinstance(toks, ListVal)
    tags = [t.tag for t in toks.items if isinstance(t, SumVal)]
    assert "Hole" in tags and "Colon" in tags and "Float" in tags


def test_compile_typed_lit_and_neg():
    prog = load_stage1_program()
    result = compile_air_source(prog, "NEG[3]")
    assert not isinstance(result, ErrorVal), result
    out = run_chunk(chunk_from_sum(result))
    assert isinstance(out, IntVal) and out.value == -3


def test_compile_hole_traps():
    prog = load_stage1_program()
    result = compile_air_source(prog, "?")
    assert not isinstance(result, ErrorVal), result
    out = run_chunk(chunk_from_sum(result))
    assert isinstance(out, ErrorVal)
    assert out.err.kind == "hole_trap"
