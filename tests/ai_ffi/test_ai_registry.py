"""ToolRegistry (Phase 10 T3)."""

from __future__ import annotations

from golem.ai_ffi import ToolRegistry
from golem.ast import ModelDecl, ToolDecl
from golem.values import ErrorVal, StringVal


def test_register_model_requires_ai_effect():
    reg = ToolRegistry()
    bad = ModelDecl("m", "string", "string", True, effects=["fs.read"])
    err = reg.register_model(bad, lambda args: StringVal("x"))
    assert isinstance(err, ErrorVal)
    assert err.err.kind == "model_effects"


def test_register_and_lookup():
    reg = ToolRegistry()
    m = ModelDecl("m", "string", "string", True, effects=["ai"])
    assert reg.register_model(m, lambda args: StringVal("ok")) is None
    t = ToolDecl("rd", "string", "bytes", effects=["fs.read"])
    reg.register_tool(t, lambda args: StringVal("b"))
    assert reg.lookup("m") is not None
    assert reg.lookup("rd") is not None
    assert reg.names() == ["m", "rd"]
