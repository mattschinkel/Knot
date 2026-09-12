"""link_program (Phase 8 T3)."""

from __future__ import annotations

from knot.ast import DefNode
from knot.modules import ModuleRegistry, link_program
from knot.parser import parse_expr
from knot.testing import run_test
from knot.values import ErrorVal


def test_link_import_def():
    reg = ModuleRegistry()
    reg.register(
        parse_expr(
            "MODULE[math,DEF[square,FN[[x:i32],MUL[x,x]]],EXPORT[square]]"
        ),
        version="1",
    )
    prog = [
        parse_expr("IMPORT[math,square]"),
        parse_expr("TEST[square,CASE[5,25]]"),
    ]
    linked = link_program(prog, reg)
    assert not isinstance(linked, ErrorVal)
    assert any(isinstance(x, DefNode) and x.name == "square" for x in linked.items)
    # run test against linked items
    from knot.ast import InlineTest

    test = next(x for x in linked.items if isinstance(x, InlineTest))
    assert run_test(list(linked.items), test).ok


def test_link_missing_export():
    reg = ModuleRegistry()
    reg.register(parse_expr("MODULE[m,DEF[a,1],EXPORT[a]]"), version="0")
    linked = link_program([parse_expr("IMPORT[m,b]")], reg)
    assert isinstance(linked, ErrorVal)
    assert linked.err.kind == "import"


def test_link_unknown_module():
    reg = ModuleRegistry()
    linked = link_program([parse_expr("IMPORT[nope]")], reg)
    assert isinstance(linked, ErrorVal)
