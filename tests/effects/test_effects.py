"""EffectCategory and EffectSet (Phase 3 T1)."""

from __future__ import annotations

from knot.effects import PURE, EffectCategory, EffectSet


def test_effect_categories_exist():
    assert EffectCategory.FS_READ.value == "fs.read"
    assert EffectCategory.NET_REQUEST.value == "net.request"
    assert EffectCategory.AI.value == "ai"


def test_effectset_empty_is_pure():
    assert PURE.is_pure()
    assert len(PURE) == 0


def test_effectset_membership():
    es = EffectSet([EffectCategory.FS_READ, EffectCategory.IO_STDOUT])
    assert EffectCategory.FS_READ in es
    assert EffectCategory.NET_REQUEST not in es
    assert len(es) == 2


def test_effectset_union():
    a = EffectSet([EffectCategory.FS_READ])
    b = EffectSet([EffectCategory.NET_REQUEST])
    u = a.union(b)
    assert EffectCategory.FS_READ in u and EffectCategory.NET_REQUEST in u


def test_effectset_frozen():
    es = EffectSet([EffectCategory.RANDOM])
    try:
        es.effects.add(EffectCategory.AI)  # type: ignore[attr-defined]
        assert False, "frozenset should be immutable"
    except AttributeError:
        pass
