"""Phase 10 properties — no raises on happy paths."""

from __future__ import annotations

from knot.ai_ffi import ToolRegistry, invoke, invoke_expr
from knot.ast import ModelDecl, ToolDecl
from knot.canonical import normalize
from knot.effects import Capability, CapabilitySet
from knot.parser import parse_expr
from knot.values import AiResult, BytesVal, StringVal


def test_parse_invoke_end_to_end():
    reg = ToolRegistry()
    m = parse_expr(
        "MODEL[classifier,IN[string],OUT[string],CONF[true],EFFECTS[ai]]"
    )
    assert isinstance(m, ModelDecl)
    reg.register_model(m, lambda a: StringVal("ok"))
    inv = parse_expr("INVOKE[classifier,'x']")
    r = invoke_expr(reg, inv, CapabilitySet([Capability.AI]))
    assert isinstance(r, AiResult)


def test_normalize_idempotent():
    for s in (
        "MODEL[a,IN[i32],OUT[i32],CONF[true],EFFECTS[ai]]",
        "TOOL[b,IN[string],OUT[bytes],EFFECTS[fs.read]]",
        "INVOKE[b,'p']",
    ):
        assert normalize(normalize(s)) == normalize(s)


def test_tool_roundtrip_prop():
    reg = ToolRegistry()
    t = parse_expr("TOOL[fs_read,IN[string],OUT[bytes],EFFECTS[fs.read]]")
    assert isinstance(t, ToolDecl)
    reg.register_tool(t, lambda a: BytesVal(b"z"))
    r = invoke(reg, "fs_read", [StringVal("q")], CapabilitySet([Capability.FS_READ]))
    assert isinstance(r, BytesVal)
