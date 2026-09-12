"""REF / DEREF / RegionVal / RegionType subtype (Phase 11 T3/T5)."""

from __future__ import annotations

from knot.checker import infer_type
from knot.parser import parse_expr
from knot.partial import evaluate
from knot.types import I32, RegionType, subtype
from knot.values import ErrorVal, IntVal, RegionVal


def test_ref_deref_roundtrip():
    r = evaluate(parse_expr("DEREF[REF[heap,42]]"))
    assert isinstance(r, IntVal) and r.value == 42


def test_ref_value_type():
    r = evaluate(parse_expr("REF[r1,7]"))
    assert isinstance(r, RegionVal)
    assert r.region == "r1"
    assert isinstance(r.type, RegionType)


def test_deref_non_region():
    r = evaluate(parse_expr("DEREF[1]"))
    assert isinstance(r, ErrorVal)
    assert r.err.kind == "region"


def test_region_subtype_same_region():
    a = RegionType(I32, "r1")
    b = RegionType(I32, "r1")
    assert subtype(a, b)
    assert not subtype(RegionType(I32, "r1"), RegionType(I32, "r2"))


def test_infer_ref():
    t = infer_type(parse_expr("REF[r1,1]"))
    assert isinstance(t, RegionType)
    assert t.region == "r1"
