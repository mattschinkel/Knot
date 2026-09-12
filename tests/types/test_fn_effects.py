"""FnType carries optional effects and caps (Phase 3 T8)."""

from __future__ import annotations

from golem.effects import Capability, CapabilitySet, EffectCategory, EffectSet
from golem.types import FnType, I32, STRING


def test_fntype_defaults_pure():
    ft = FnType((I32,), I32)
    assert ft.effects.is_pure()
    assert len(ft.caps) == 0


def test_fntype_with_effects():
    es = EffectSet([EffectCategory.NET_REQUEST])
    ft = FnType((STRING,), STRING, effects=es)
    assert EffectCategory.NET_REQUEST in ft.effects
    assert not ft.effects.is_pure()


def test_fntype_with_caps():
    caps = CapabilitySet([Capability.NET_REQUEST, Capability.FS_READ])
    ft = FnType((I32,), I32, caps=caps)
    assert Capability.NET_REQUEST in ft.caps
    assert Capability.FS_READ in ft.caps


def test_fntype_equality_includes_effects():
    a = FnType((I32,), I32)
    b = FnType((I32,), I32, effects=EffectSet([EffectCategory.AI]))
    assert a != b
    assert a == FnType((I32,), I32)
