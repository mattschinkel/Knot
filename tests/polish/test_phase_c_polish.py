"""Phase C polish tests: pretty-view, PAR opcodes, borrow, MODEL handler shape."""

from golem.ast import (
    IdentExpr,
    LitExpr,
    MatchCase,
    MatchExpr,
    ModuleDecl,
    ParExpr,
    RefExpr,
    DefNode,
)
from golem.concurrency import borrow_check
from golem.printer import print_ast
from golem.values import ErrorVal, IntVal, TupleVal
from golem.vm.chunk import Chunk
from golem.vm.compiler import compile_expr
from golem.vm.machine import VM
from golem.vm.opcode import Op
from golem.parser import parse_expr
from golem.ai_ffi import make_openai_compatible_handler
from golem.values import StringVal


def test_pretty_module_and_match():
    m = ModuleDecl("demo", [DefNode("x", LitExpr(1))], exports=["x"])
    s = print_ast(m)
    assert "module demo" in s and "export x" in s
    mx = MatchExpr(LitExpr(1), [MatchCase("A", LitExpr(2), binding="x")])
    assert "match" in print_ast(mx) and "case A" in print_ast(mx)


def test_pretty_par_ref():
    p = ParExpr([LitExpr(1), LitExpr(2)])
    assert print_ast(p).startswith("par(")
    r = RefExpr("heap", LitExpr(3))
    assert "ref@heap" in print_ast(r)


def test_vm_par_opcode():
    ch = Chunk()
    ch.emit(Op.LOAD_CONST, ch.add_const(IntVal(32, 1)))
    ch.emit(Op.LOAD_CONST, ch.add_const(IntVal(32, 2)))
    ch.emit(Op.PAR, 2)
    ch.emit(Op.RETURN)
    out = VM().run_chunk(ch)
    assert isinstance(out, TupleVal) and len(out.items) == 2


def test_compile_par_expr():
    from golem.ast import OpExpr

    ch = compile_expr(OpExpr("PAR", [LitExpr(10), LitExpr(20)]))
    assert not isinstance(ch, ErrorVal)
    ch.emit(Op.RETURN)
    out = VM().run_chunk(ch)
    assert isinstance(out, TupleVal)


def test_borrow_nested_same_region():
    inner = RefExpr("r", LitExpr(1))
    outer = RefExpr("r", inner)
    err = borrow_check(outer)
    assert isinstance(err, ErrorVal) and err.err.kind == "borrow"


def test_borrow_ok_distinct_regions():
    expr = RefExpr("a", RefExpr("b", LitExpr(1)))
    assert borrow_check(expr) is None


def test_openai_handler_rejects_non_string():
    h = make_openai_compatible_handler(base_url="http://127.0.0.1:9/v1")
    r = h((IntVal(32, 1),))
    assert isinstance(r, ErrorVal)
