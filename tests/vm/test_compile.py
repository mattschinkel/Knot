"""compile AST → bytecode (Phase 9 T1–T2)."""

from __future__ import annotations

from knot.parser import parse_expr
from knot.vm import compile_expr
from knot.vm.opcode import Op
from knot.values import ErrorVal


def test_compile_add():
    ch = compile_expr(parse_expr("ADD[1,2]"))
    assert not isinstance(ch, ErrorVal)
    assert Op.ADD in ch.code
    assert Op.LOAD_CONST in ch.code


def test_compile_unbound_local():
    # Ident without locals map → compile error
    err = compile_expr(parse_expr("x"))
    assert isinstance(err, ErrorVal)
