"""Structural subtype tests (Phase 2 T2)."""

from __future__ import annotations

from golem.types import (
    subtype,
    ListType, SetType, MapType, TupleType, OptionType, NominalType,
    I32, I64, STRING, F64, NEVER,
)


def test_reflexive_and_never():
    assert subtype(I32, I32)
    assert subtype(NEVER, I32)
    assert subtype(NEVER, ListType(I32))
    assert not subtype(I32, NEVER)


def test_option_lifting():
    assert subtype(I32, OptionType(I32))
    assert not subtype(OptionType(I32), I32)


def test_nominal_subtype_of_def():
    distance = NominalType("Distance", F64)
    assert subtype(distance, F64)
    assert not subtype(F64, distance)


def test_list_covariant():
    assert subtype(ListType(I32), ListType(I32))
    assert subtype(ListType(NEVER), ListType(I32))
    assert not subtype(ListType(I32), ListType(STRING))
    assert not subtype(ListType(I32), I32)


def test_set_covariant():
    assert subtype(SetType(I32), SetType(I32))
    assert subtype(SetType(NEVER), SetType(I32))
    assert not subtype(SetType(I32), SetType(STRING))


def test_map_structural():
    assert subtype(MapType(I32, STRING), MapType(I32, STRING))
    assert subtype(MapType(NEVER, NEVER), MapType(I32, STRING))
    assert not subtype(MapType(I32, STRING), MapType(STRING, I32))


def test_tuple_structural():
    assert subtype(TupleType((I32, STRING)), TupleType((I32, STRING)))
    assert subtype(TupleType((NEVER, NEVER)), TupleType((I32, STRING)))
    assert not subtype(TupleType((I32,)), TupleType((I32, STRING)))
    assert not subtype(TupleType((I32, STRING)), TupleType((STRING, I32)))


def test_distinct_base_not_subtype():
    assert not subtype(I32, I64)
    assert not subtype(I64, I32)


def test_nested_list():
    inner = ListType(I32)
    assert subtype(ListType(inner), ListType(ListType(I32)))
    assert not subtype(ListType(inner), ListType(ListType(STRING)))
