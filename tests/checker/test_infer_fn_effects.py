"""infer_fn attaches AST effect/cap annotations to FnType (Phase 3 T9)."""

from __future__ import annotations

from golem.ast import FnExpr, IdentExpr, LitExpr
from golem.checker import infer_fn
from golem.effects import Capability, CapabilitySet, EffectCategory, EffectSet
from golem.types import FnType, I32


def test_infer_fn_no_annotations_pure():
    fn = FnExpr([("x", "i32")], IdentExpr("x"))
    t = infer_fn(fn)
    assert isinstance(t, FnType)
    assert t.effects.is_pure()
    assert len(t.caps) == 0


def test_infer_fn_with_effects():
    es = EffectSet([EffectCategory.FS_READ, EffectCategory.IO_STDOUT])
    fn = FnExpr(
        [("x", "i32")],
        LitExpr(1),
        effects=es,
    )
    t = infer_fn(fn)
    assert isinstance(t, FnType)
    assert EffectCategory.FS_READ in t.effects
    assert EffectCategory.IO_STDOUT in t.effects


def test_infer_fn_with_caps():
    caps = CapabilitySet([Capability.NET_REQUEST])
    fn = FnExpr([("x", "i32")], IdentExpr("x"), caps=caps)
    t = infer_fn(fn)
    assert isinstance(t, FnType)
    assert Capability.NET_REQUEST in t.caps
    assert t.params == (I32,)
