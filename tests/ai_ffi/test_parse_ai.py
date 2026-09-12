"""Parse/canonical MODEL TOOL INVOKE (Phase 10 T1)."""

from __future__ import annotations

from knot.ast import InvokeExpr, ModelDecl, ToolDecl
from knot.canonical import normalize, print_canonical
from knot.parser import parse_expr


def test_parse_model():
    n = parse_expr(
        "MODEL[classifier,IN[string],OUT[string],CONF[true],EFFECTS[ai]]"
    )
    assert isinstance(n, ModelDecl)
    assert n.name == "classifier"
    assert n.in_type == "string"
    assert n.out_type == "string"
    assert n.confidence is True
    assert n.effects == ["ai"]


def test_parse_tool():
    n = parse_expr("TOOL[fs_read,IN[string],OUT[bytes],EFFECTS[fs.read]]")
    assert isinstance(n, ToolDecl)
    assert n.effects == ["fs.read"]


def test_parse_invoke():
    n = parse_expr("INVOKE[classifier,'doc']")
    assert isinstance(n, InvokeExpr)
    assert n.name == "classifier"
    assert len(n.args) == 1


def test_canonical_roundtrip():
    src = "MODEL[c,IN[i32],OUT[bool],CONF[false],EFFECTS[ai]]"
    assert normalize(src) == src
    src2 = "TOOL[t,IN[string],OUT[bytes],EFFECTS[fs.read]]"
    assert normalize(src2) == src2
    assert print_canonical(parse_expr("INVOKE[t,'x']")) == "INVOKE[t,'x']"
