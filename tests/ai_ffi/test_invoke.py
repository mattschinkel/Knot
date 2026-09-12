"""invoke + AiResult + caps (Phase 10 T2/T4)."""

from __future__ import annotations

from golem.ai_ffi import ToolRegistry, invoke
from golem.ast import ModelDecl, ToolDecl
from golem.effects import Capability, CapabilitySet
from golem.values import AiResult, BytesVal, ErrorVal, StringVal


def test_model_invoke_returns_ai_result():
    reg = ToolRegistry()
    decl = ModelDecl("classifier", "string", "string", True, effects=["ai"])

    def handler(args):
        return StringVal("label")

    reg.register_model(decl, handler, version="1")
    r = invoke(reg, "classifier", [StringVal("doc")], CapabilitySet([Capability.AI]))
    assert isinstance(r, AiResult)
    assert r.value.value == "label"
    assert r.confidence == 1.0
    assert r.model == "classifier"
    assert r.version == "1"


def test_model_conf_false_no_confidence():
    reg = ToolRegistry()
    decl = ModelDecl("c", "string", "string", False, effects=["ai"])
    reg.register_model(decl, lambda a: StringVal("x"))
    r = invoke(reg, "c", [StringVal("a")], CapabilitySet([Capability.AI]))
    assert isinstance(r, AiResult)
    assert r.confidence is None


def test_invoke_needs_capability():
    reg = ToolRegistry()
    decl = ModelDecl("c", "string", "string", True, effects=["ai"])
    reg.register_model(decl, lambda a: StringVal("x"))
    r = invoke(reg, "c", [StringVal("a")], CapabilitySet())
    assert isinstance(r, ErrorVal)
    assert r.err.kind == "capability"


def test_tool_invoke_no_ai_wrapper():
    reg = ToolRegistry()
    decl = ToolDecl("fs_read", "string", "bytes", effects=["fs.read"])
    reg.register_tool(decl, lambda a: BytesVal(b"hi"))
    r = invoke(
        reg, "fs_read", [StringVal("p")], CapabilitySet([Capability.FS_READ])
    )
    assert isinstance(r, BytesVal)
    assert r.value == b"hi"


def test_unknown_invoke():
    reg = ToolRegistry()
    r = invoke(reg, "nope", [])
    assert isinstance(r, ErrorVal)
    assert r.err.kind == "unknown_invoke"
