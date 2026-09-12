"""Property tests for testing module (Phase 7 T5)."""

from __future__ import annotations

from knot.canonical import normalize
from knot.parser import parse_expr
from knot.testing import fuzz_samples, run_suite


def test_no_raise():
    prog = [
        parse_expr("DEF[id,FN[[x:i32],x]]"),
        parse_expr("TEST[id,CASE[1,1]]"),
        parse_expr("PROPERTY[eq,[[x:i32],EQ[id[x],x]]]"),
    ]
    s = run_suite(prog)
    assert s.ok
    _ = fuzz_samples("bool", 4, 1)
    _ = normalize("TEST[id,CASE[1,1]]")


def test_empty_suite_not_ok():
    assert not run_suite([parse_expr("DEF[x,1]")]).ok
