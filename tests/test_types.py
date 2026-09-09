"""Property tests for the type algebra (Phase 0)."""

from __future__ import annotations

from knot.types import (
    BaseType, NominalType, OptionType, ListType, RecordType, SumType,
    UnitType, RegionType, subtype, unify,
    I32, I64, F64, BOOL, STRING, UNIT, NEVER,
)
from knot.units import m


def test_reflexive():
    assert subtype(I32, I32)
    assert subtype(STRING, STRING)


def test_never_subtype_of_everything():
    assert subtype(NEVER, I32)
    assert subtype(NEVER, STRING)
    assert subtype(NEVER, OptionType(I32))


def test_never_not_supertype():
    # only never <: never
    assert subtype(NEVER, NEVER)
    assert not subtype(I32, NEVER)


def test_option_lifting():
    assert subtype(I32, OptionType(I32))
    assert subtype(OptionType(I32), OptionType(OptionType(I32)))


def test_option_inner_not_converse():
    # a None (OptionType(I32)) is not an I32
    assert not subtype(OptionType(I32), I32)


def test_nominal_subtype_of_def():
    distance = NominalType("Distance", F64)
    assert subtype(distance, F64)
    # nominal is reflexive
    assert subtype(distance, distance)


def test_nominal_not_supertype_of_def():
    distance = NominalType("Distance", F64)
    assert not subtype(F64, distance)


def test_unify_reflexive():
    assert unify(I32, I32) is I32
    assert unify(STRING, STRING) is STRING


def test_unify_stub_returns_none():
    assert unify(I32, I64) is None
    assert unify(I32, STRING) is None


def test_unit_type_carries_dimension():
    t = UnitType(F64, m)
    assert t.base == F64
    assert t.dim == m
    assert subtype(t, t)


def test_region_type_shape_only():
    # Phase 0 only defines the shape; no subtyping rule for regions.
    rt = RegionType(I32, "r1")
    assert rt.inner == I32
    assert rt.region == "r1"


def test_distinct_int_types_not_subtype():
    # Q1: i32 and i64 are distinct types
    assert not subtype(I32, I64)
    assert not subtype(I64, I32)
