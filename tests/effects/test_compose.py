"""compose_effects — union of EffectSets (Phase 3 T3)."""

from __future__ import annotations

from golem.effects import EffectCategory, EffectSet, compose_effects


def test_compose_empty():
    assert compose_effects().is_pure()


def test_compose_single():
    a = EffectSet([EffectCategory.FS_READ])
    assert compose_effects(a) == a


def test_compose_union():
    a = EffectSet([EffectCategory.FS_READ])
    b = EffectSet([EffectCategory.NET_REQUEST])
    u = compose_effects(a, b)
    assert EffectCategory.FS_READ in u
    assert EffectCategory.NET_REQUEST in u


def test_compose_idempotent():
    a = EffectSet([EffectCategory.AI])
    assert compose_effects(a, a) == a
