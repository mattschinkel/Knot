"""eval PAR / SEQ (Phase 11 T2)."""

from __future__ import annotations

from knot.concurrency import schedule_par
from knot.parser import parse_expr
from knot.partial import evaluate
from knot.values import IntVal, TupleVal, UnitVal


def test_eval_par_tuple_order():
    r = evaluate(parse_expr("PAR[ADD[1,2],MUL[3,4]]"))
    assert isinstance(r, TupleVal)
    assert r.items[0].value == 3 and r.items[1].value == 12


def test_eval_seq_last():
    r = evaluate(parse_expr("SEQ[1,2,ADD[10,1]]"))
    assert isinstance(r, IntVal) and r.value == 11


def test_eval_seq_empty():
    r = evaluate(parse_expr("SEQ[]"))
    assert isinstance(r, UnitVal)


def test_schedule_par_one_group():
    n = parse_expr("PAR[1,2,3]")
    groups = schedule_par(n.branches)
    assert len(groups) == 1
    assert len(groups[0]) == 3
