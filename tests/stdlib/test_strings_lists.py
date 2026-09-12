"""Stage 0.5 string/list/map runtime tests."""

from __future__ import annotations

from golem.parser import parse_expr
from golem.partial import evaluate
from golem.values import ErrorVal, IntVal, ListVal, StringVal
from golem.vm import run


def test_string_len_at_concat():
    assert evaluate(parse_expr("LEN['hi']")).value == 2
    assert evaluate(parse_expr("AT['hi',0]")).value == "h"
    assert evaluate(parse_expr("CONCAT['a','b']")).value == "ab"
    assert evaluate(parse_expr("SLICE['abcd',1,3]")).value == "bc"


def test_codepoint():
    assert evaluate(parse_expr("CODEPOINT['A']")).value == 65
    assert evaluate(parse_expr("FROM_CODEPOINT[65]")).value == "A"


def test_list_ops():
    r = evaluate(parse_expr("LIST[1,2,3]"))
    assert isinstance(r, ListVal) and len(r.items) == 3
    assert evaluate(parse_expr("LEN[LIST[1,2]]")).value == 2
    assert evaluate(parse_expr("AT[LIST[10,20],1]")).value == 20
    assert evaluate(parse_expr("APPEND[LIST[1],2]")).items[-1].value == 2


def test_vm_string_list():
    assert run(parse_expr("CONCAT['x','y']")).value == "xy"
    assert run(parse_expr("LEN[LIST[1,2,3]]")).value == 3


def test_map_ops():
    r = evaluate(
        parse_expr("MAP_GET[MAP_SET[MAP_NEW[],'k',1],'k']")
    )
    assert isinstance(r, IntVal) and r.value == 1


def test_fact_recursion_eval_and_vm():
    prog = [
        parse_expr(
            "DEF[fact,FN[[n:i32],IF[LE[n,1],1,MUL[n,fact[SUB[n,1]]]]]]"
        )
    ]
    from golem.partial import evaluate as ev

    r = ev(parse_expr("fact[5]"), program=prog)
    assert isinstance(r, IntVal) and r.value == 120
    r2 = run(prog, call="fact", args=[IntVal(32, 5)])
    assert isinstance(r2, IntVal) and r2.value == 120
