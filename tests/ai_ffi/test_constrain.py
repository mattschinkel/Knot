"""constrain output to declared OUT (Phase 10 T5)."""

from __future__ import annotations

from golem.ai_ffi import ToolRegistry, constrain, invoke, type_from_air
from golem.ast import ModelDecl
from golem.effects import Capability, CapabilitySet
from golem.types import BaseType
from golem.values import ErrorVal, IntVal, StringVal


def test_type_from_air():
    assert type_from_air("i32") == BaseType("i32")
    assert type_from_air("string") == BaseType("string")


def test_constrain_ok():
    v = constrain(StringVal("x"), "string")
    assert isinstance(v, StringVal)


def test_constrain_mismatch():
    v = constrain(IntVal(32, 1), "string")
    assert isinstance(v, ErrorVal)
    assert v.err.kind == "constrain"


def test_invoke_constrain_rejects_bad_handler():
    reg = ToolRegistry()
    decl = ModelDecl("c", "string", "string", True, effects=["ai"])
    reg.register_model(decl, lambda a: IntVal(32, 9))
    r = invoke(reg, "c", [StringVal("a")], CapabilitySet([Capability.AI]))
    assert isinstance(r, ErrorVal)
    assert r.err.kind == "constrain"
