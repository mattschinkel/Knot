"""run_test (Phase 7 T2)."""

from __future__ import annotations

from golem.parser import parse_expr
from golem.testing import run_suite, run_test


def _square_prog():
    return [
        parse_expr("DEF[square,FN[[x:i32],MUL[x,x]]]"),
        parse_expr("TEST[square,CASE[5,25],CASE[-3,9],CASE[0,0]]"),
    ]


def test_run_test_passes():
    prog = _square_prog()
    r = run_test(prog, prog[1])
    assert r.ok
    assert len(r.cases) == 3


def test_run_test_fails_wrong_out():
    prog = [
        parse_expr("DEF[square,FN[[x:i32],MUL[x,x]]]"),
        parse_expr("TEST[square,CASE[5,24]]"),
    ]
    r = run_test(prog, prog[1])
    assert not r.ok


def test_suite_ok():
    assert run_suite(_square_prog()).ok
