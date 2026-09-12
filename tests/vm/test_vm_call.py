"""VM DEF/FN calls (Phase 9 T4)."""

from __future__ import annotations

from golem.parser import parse_expr
from golem.vm import run
from golem.values import IntVal


def test_vm_square():
    prog = [parse_expr("DEF[square,FN[[x:i32],MUL[x,x]]]")]
    r = run(prog, call="square", args=[IntVal(32, 7)])
    assert isinstance(r, IntVal) and r.value == 49


def test_vm_nested_call():
    prog = [
        parse_expr("DEF[double,FN[[x:i32],MUL[x,2]]]"),
        parse_expr("DEF[quad,FN[[x:i32],double[double[x]]]]"),
    ]
    r = run(prog, call="quad", args=[IntVal(32, 3)])
    assert isinstance(r, IntVal) and r.value == 12
