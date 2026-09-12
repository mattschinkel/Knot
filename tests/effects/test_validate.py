"""validate_call_effects at call sites (Phase 3 T10)."""

from __future__ import annotations

from knot.effects import (
    Capability,
    CapabilitySet,
    EffectCategory,
    EffectSet,
    validate_call_effects,
)
from knot.types import FnType, I32, STRING


def test_validate_pure_always_ok():
    ft = FnType((I32,), I32)
    assert validate_call_effects(ft, CapabilitySet()) is True


def test_validate_effect_needs_matching_cap():
    ft = FnType(
        (STRING,),
        STRING,
        effects=EffectSet([EffectCategory.NET_REQUEST]),
    )
    assert validate_call_effects(ft, CapabilitySet()) is False
    granted = CapabilitySet([Capability.NET_REQUEST])
    assert validate_call_effects(ft, granted) is True


def test_validate_explicit_caps():
    ft = FnType(
        (I32,),
        I32,
        caps=CapabilitySet([Capability.FS_READ, Capability.FS_WRITE]),
    )
    assert validate_call_effects(ft, CapabilitySet([Capability.FS_READ])) is False
    full = CapabilitySet([Capability.FS_READ, Capability.FS_WRITE])
    assert validate_call_effects(ft, full) is True


def test_validate_effects_and_caps_union():
    ft = FnType(
        (I32,),
        I32,
        effects=EffectSet([EffectCategory.AI]),
        caps=CapabilitySet([Capability.RANDOM]),
    )
    only_ai = CapabilitySet([Capability.AI])
    assert validate_call_effects(ft, only_ai) is False
    both = CapabilitySet([Capability.AI, Capability.RANDOM])
    assert validate_call_effects(ft, both) is True
