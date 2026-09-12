"""VM arith and IF (Phase 9 T3)."""

from __future__ import annotations

from golem.parser import parse_expr
from golem.vm import run
from golem.values import BoolVal, IntVal


def test_vm_add_mul():
    r = run(parse_expr("MUL[ADD[2,3],4]"))
    assert isinstance(r, IntVal) and r.value == 20


def test_vm_compare():
    r = run(parse_expr("GE[5,5]"))
    assert isinstance(r, BoolVal) and r.value is True


def test_vm_if():
    assert run(parse_expr("IF[true,1,2]")).value == 1
    assert run(parse_expr("IF[false,1,2]")).value == 2
