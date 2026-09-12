"""Parse/canonical PAR SEQ REF DEREF UNSAFE (Phase 11 T1)."""

from __future__ import annotations

from knot.ast import DerefExpr, ParExpr, RefExpr, SeqExpr, UnsafeExpr
from knot.canonical import normalize, print_canonical
from knot.parser import parse_expr


def test_parse_par_seq():
    p = parse_expr("PAR[1,2,3]")
    assert isinstance(p, ParExpr) and len(p.branches) == 3
    s = parse_expr("SEQ[1,2]")
    assert isinstance(s, SeqExpr) and len(s.steps) == 2


def test_parse_ref_deref():
    r = parse_expr("REF[heap,ADD[1,1]]")
    assert isinstance(r, RefExpr) and r.region == "heap"
    d = parse_expr("DEREF[REF[heap,1]]")
    assert isinstance(d, DerefExpr)


def test_parse_unsafe():
    u = parse_expr("UNSAFE[CAPS[fs.write],ADD[1,1]]")
    assert isinstance(u, UnsafeExpr)
    assert u.caps == ["fs.write"]


def test_canonical_roundtrip():
    for src in (
        "PAR[ADD[1,2],ADD[3,4]]",
        "SEQ[1,2,3]",
        "REF[r1,5]",
        "DEREF[REF[r1,5]]",
        "UNSAFE[CAPS[unsafe],1]",
    ):
        assert normalize(src) == print_canonical(parse_expr(src))
        assert normalize(normalize(src)) == normalize(src)
