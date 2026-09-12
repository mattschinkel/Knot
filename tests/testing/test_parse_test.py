"""TEST/PROPERTY parse + canonical (Phase 7 T1)."""

from __future__ import annotations

from knot.ast import PropertyDecl, InlineTest
from knot.canonical import normalize, print_canonical
from knot.parser import parse_expr


def test_parse_test():
    n = parse_expr("TEST[square,CASE[5,25],CASE[0,0]]")
    assert isinstance(n, InlineTest)
    assert n.name == "square"
    assert len(n.cases) == 2


def test_parse_property():
    n = parse_expr("PROPERTY[nonneg,[[x:i32],GE[square[x],0]]]")
    assert isinstance(n, PropertyDecl)
    assert n.name == "nonneg"
    assert n.params == [("x", "i32")]


def test_canonical_roundtrip():
    s = "TEST[square,CASE[5,25]]"
    assert normalize("TEST[ square , CASE[ 5 , 25 ] ]") == s
    p = "PROPERTY[nonneg,[[x:i32],GE[square[x],0]]]"
    assert print_canonical(parse_expr(p)) == p
