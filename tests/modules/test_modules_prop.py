"""Property tests for modules (Phase 8 T5)."""

from __future__ import annotations

from knot.canonical import normalize
from knot.modules import ModuleRegistry, link_program
from knot.parser import parse_expr


def test_no_raise():
    reg = ModuleRegistry()
    m = parse_expr("MODULE[u,DEF[id,FN[[x:i32],x]],EXPORT[id]]")
    reg.register(m)
    prog = [parse_expr("IMPORT[u,id]"), parse_expr("DEPENDS[u,0]")]
    linked = link_program(prog, reg)
    assert linked.items
    _ = normalize("IMPORT[u,id]")
    _ = normalize("DEPENDS[u,0]")
