"""Property tests for effects (Phase 3 T11)."""

from __future__ import annotations

from knot.effects import (
    PURE,
    Capability,
    CapabilitySet,
    EffectCategory,
    EffectSet,
    check_capabilities,
    compose_effects,
    validate_call_effects,
)
from knot.types import FnType, I32


def test_no_raise():
    """Public effect APIs never raise on well-typed inputs."""
    cats = list(EffectCategory)
    for c in cats:
        es = EffectSet([c])
        assert c in es or c is EffectCategory.PURE
        _ = es.union(PURE)
        _ = es.intersection(PURE)
        _ = es.issubset(es)
        _ = es.is_pure()
    compose_effects(PURE, EffectSet([EffectCategory.FS_READ]))
    check_capabilities(CapabilitySet(), CapabilitySet())
    validate_call_effects(FnType((I32,), I32), CapabilitySet())


def test_pure_ok():
    """Empty / pure effect sets are a subset of every effect set."""
    others = EffectSet(
        [
            EffectCategory.FS_READ,
            EffectCategory.NET_REQUEST,
            EffectCategory.AI,
        ]
    )
    assert PURE.issubset(others)
    assert PURE.issubset(PURE)
    assert compose_effects().is_pure()
    assert validate_call_effects(
        FnType((I32,), I32, effects=PURE),
        CapabilitySet([Capability.AI]),
    )
