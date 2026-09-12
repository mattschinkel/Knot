"""VM hole trap + M5 (Phase 9 T5)."""

from __future__ import annotations

from knot.parser import parse_expr
from knot.vm import measure_m5, run
from knot.values import ErrorVal


def test_vm_hole_trap():
    r = run(parse_expr("ADD[1,?]"))
    assert isinstance(r, ErrorVal)
    assert r.err.kind == "hole_trap"


def test_m5_under_200ms():
    ms = measure_m5()
    assert ms < 200.0
    assert ms >= 0.0


def test_vm_prop_no_raise():
    for s in ("ADD[1,1]", "IF[true,0,1]", "MUL[3,3]"):
        run(parse_expr(s))
