"""fuzz_samples + run_property (Phase 7 T3)."""

from __future__ import annotations

from golem.parser import parse_expr
from golem.testing import fuzz_samples, run_property
from golem.values import IntVal


def test_fuzz_deterministic():
    a = fuzz_samples("i32", n=5, seed=0)
    b = fuzz_samples("i32", n=5, seed=0)
    assert [x.value for x in a] == [x.value for x in b]
    assert isinstance(a[0], IntVal)


def test_property_passes():
    prog = [
        parse_expr("DEF[square,FN[[x:i32],MUL[x,x]]]"),
        parse_expr("PROPERTY[nonneg,[[x:i32],GE[square[x],0]]]"),
    ]
    r = run_property(prog, prog[1], n=8, seed=0)
    assert r.ok
    assert r.samples_run == 8


def test_property_fails():
    prog = [
        parse_expr("DEF[neg,FN[[x:i32],MUL[x,-1]]]"),
        parse_expr("PROPERTY[always_pos,[[x:i32],GT[neg[x],0]]]"),
    ]
    r = run_property(prog, prog[1], n=8, seed=0)
    assert not r.ok
    assert r.failing_sample is not None
