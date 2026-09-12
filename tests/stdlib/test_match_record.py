"""MATCH / RECORD / GET / SUM (Stage 0.5)."""

from __future__ import annotations

from golem.ast import MatchExpr
from golem.canonical import normalize, print_canonical
from golem.parser import parse_expr
from golem.partial import evaluate
from golem.values import IntVal, RecordVal, StringVal, SumVal


def test_parse_match():
    n = parse_expr("MATCH[SUM['A',1],CASE[A,10],CASE[B,20]]")
    assert isinstance(n, MatchExpr)
    assert len(n.cases) == 2
    assert normalize("MATCH[SUM['A',1],CASE[A,10],CASE[B,20]]") == print_canonical(n)


def test_eval_match():
    r = evaluate(parse_expr("MATCH[SUM['Lit',42],CASE[Lit,PAYLOAD[SUM['Lit',42]]],CASE[Op,0]]"))
    # simpler: CASE with binding
    r = evaluate(parse_expr("MATCH[SUM['Lit',42],CASE[Lit,x,x],CASE[Op,0]]"))
    assert isinstance(r, IntVal) and r.value == 42


def test_record_get():
    r = evaluate(
        parse_expr("GET[RECORD['Pt',FIELD[x,1],FIELD[y,2]],x]")
    )
    assert isinstance(r, IntVal) and r.value == 1


def test_tag_payload():
    s = evaluate(parse_expr("SUM['T','hi']"))
    assert isinstance(s, SumVal)
    assert evaluate(parse_expr("TAG[SUM['T',1]]")).value == "T"
    assert evaluate(parse_expr("PAYLOAD[SUM['T',9]]")).value == 9
