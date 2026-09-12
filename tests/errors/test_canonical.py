"""print_canonical + normalize (Phase 5 T3 / D-FB11)."""

from __future__ import annotations

from knot.canonical import normalize, print_canonical
from knot.parser import parse_expr


def test_canonical_add_no_spaces():
    assert print_canonical(parse_expr("ADD[1, 2]")) == "ADD[1,2]"
    assert normalize("ADD[ 1 , 2 ]") == "ADD[1,2]"


def test_canonical_err_roundtrip():
    src = "ERR[TYPE_MISMATCH,[body,0],i32,bool,REPLACE[x,?:i32]]"
    assert normalize(src) == src
    spaced = "ERR[ TYPE_MISMATCH , [body, 0] , i32 , bool , REPLACE[x, ?:i32] ]"
    assert normalize(spaced) == src


def test_canonical_def_fn():
    assert normalize("DEF[ square , FN[ [x:i32] , MUL[x,x] ] ]") == (
        "DEF[square,FN[[x:i32],MUL[x,x]]]"
    )


def test_canonical_hole():
    assert normalize("?") == "?"
    assert normalize("?:i32") == "?:i32"
