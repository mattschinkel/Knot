"""Gate: golemc (Stage-1) compiles remaining deterministic AIR forms."""

from __future__ import annotations

import pytest

from golem.values import (
    ErrorVal,
    IntVal,
    RegionVal,
    StringVal,
    SumVal,
    TupleVal,
    UnitVal,
)
from selfhost.harness.compile_stage1 import (
    compile_air_source,
    load_stage1_program,
    program_from_sum,
    run_func,
)


def I(n: int) -> IntVal:
    return IntVal(32, n)


@pytest.fixture(scope="module")
def stage1_prog():
    return load_stage1_program()


def _run(prog, src: str):
    r = compile_air_source(prog, src)
    assert not isinstance(r, ErrorVal), r
    assert not (isinstance(r, SumVal) and r.tag == "Err"), r
    img = program_from_sum(r)
    assert not isinstance(img, ErrorVal), img
    return run_func(img, "__main")


@pytest.mark.parametrize(
    "src,check",
    [
        ("COND[true,10,20]", lambda v: v == I(10)),
        ("COND[false,10,20]", lambda v: v == I(20)),
        ("PAR[1,2]", lambda v: isinstance(v, TupleVal) and len(v.items) == 2),
        ("SEQ[1,2,3]", lambda v: v == I(3)),
        ("DEREF[REF[r,7]]", lambda v: v == I(7)),
        ("REF[r,1]", lambda v: isinstance(v, RegionVal)),
        ("unit", lambda v: isinstance(v, UnitVal)),
        ("nil", lambda v: isinstance(v, UnitVal)),
        ('"dq"', lambda v: v == StringVal("dq")),
        ("MATCH[SUM[Ok,1],CASE[Ok,x,x]]", lambda v: v == I(1)),
        ("MATCH[SUM['Ok',2],CASE['Ok',x,x]]", lambda v: v == I(2)),
        ("UNSAFE[CAPS[unsafe],MUL[3,3]]", lambda v: v == I(9)),
        ("DEPENDS[m,1]\nADD[2,2]", lambda v: v == I(4)),
        (
            "MODEL[x,IN[i32],OUT[i32],CONF[true],EFFECTS[]]\n1",
            lambda v: v == I(1),
        ),
        ("TOOL[t,IN[i32],OUT[i32],EFFECTS[]]\n2", lambda v: v == I(2)),
        ("VERSION[1]\n5", lambda v: v == I(5)),
        ("EXPORT[a]\n6", lambda v: v == I(6)),
        ("IMPORT[foo,a,b]\n99", lambda v: v == I(99)),
        ("1:i32", lambda v: v == I(1)),
    ],
)
def test_golemc_compile_all_forms(stage1_prog, src, check):
    assert check(_run(stage1_prog, src))


def test_golemc_semicolon_skipped(stage1_prog):
    assert _run(stage1_prog, ";ADD[1,2];") == I(3)


def test_golemc_invoke_compiles_host_stub(stage1_prog):
    r = compile_air_source(stage1_prog, "INVOKE[t,1]")
    assert isinstance(r, SumVal) and r.tag == "Program"
    img = program_from_sum(r)
    out = run_func(img, "__main")
    assert isinstance(out, ErrorVal)


def test_compile_root_links_fixture(stage1_prog):
    from golem.effects import Capability, CapabilitySet
    from selfhost.harness.compile_stage1 import FIXTURES, _call_def_values

    caps = CapabilitySet([Capability.FS_READ])
    r = _call_def_values(
        stage1_prog,
        "compile_root",
        [StringVal(str(FIXTURES)), StringVal("link_root.gol")],
        granted_caps=caps,
    )
    assert isinstance(r, SumVal) and r.tag == "Program"
    assert run_func(program_from_sum(r), "__main") == I(1)


def test_vm_compile_root_stage1():
    """In-Golem IMPORT link of full Stage-1 via VM compile_root."""
    from golem.effects import Capability, CapabilitySet
    from selfhost.harness.compile_stage1 import STAGE1
    from selfhost.harness.test_stage2 import _host_golemc
    from golem.vm.machine import VM

    caps = CapabilitySet([Capability.FS_READ])
    vm = VM(_host_golemc().image, granted_caps=caps)
    r = vm.call("compile_root", [StringVal(str(STAGE1)), StringVal("root.gol")])
    assert isinstance(r, SumVal) and r.tag == "Program"
    img = program_from_sum(r)
    assert "compile_source" in img.functions
    assert "compile_root" in img.functions
    linked = VM(img, granted_caps=caps)
    built = linked.call("compile_source", [StringVal("ADD[2,3]")])
    assert run_func(program_from_sum(built), "__main") == I(5)
