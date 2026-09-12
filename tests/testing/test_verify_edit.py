"""verify_program after edit (Phase 7 T4)."""

from __future__ import annotations

from golem.ast import LitExpr, OpExpr
from golem.parser import parse_expr
from golem.testing import verify_program


def test_verify_after_good_edit():
    prog = [
        parse_expr("DEF[square,FN[[x:i32],MUL[x,x]]]"),
        parse_expr("TEST[square,CASE[5,25]]"),
    ]
    # Replace nothing critical — edit the test expected stays
    # Edit DEF body via REPLACE_MATCH MUL -> still MUL with same meaning: no-op replace path
    edit = OpExpr(
        "REPLACE",
        [
            OpExpr("LIST", [LitExpr(0)]),  # won't work on list root via LIST[0]
            prog[0],
        ],
    )
    # Program is a list — apply_edit on list with REPLACE at LIST[0]
    new_prog, suite, er = verify_program(prog, edit)
    assert er is not None and er.ok
    assert suite.ok


def test_verify_detects_break():
    prog = [
        parse_expr("DEF[square,FN[[x:i32],MUL[x,x]]]"),
        parse_expr("TEST[square,CASE[5,25]]"),
    ]
    # Break square: replace body with ADD[x,x]
    broken = parse_expr("DEF[square,FN[[x:i32],ADD[x,x]]]")
    edit = OpExpr("REPLACE", [OpExpr("LIST", [LitExpr(0)]), broken])
    _new, suite, er = verify_program(prog, edit)
    assert er.ok  # edit applied
    assert not suite.ok  # tests fail
