"""diagnose bridge (Phase 5 T5)."""

from __future__ import annotations

from golem.ast import LitExpr, OpExpr
from golem.diagnose import DiagnoseErr, DiagnoseOk, diagnose
from golem.types import I32
from golem.values import ErrorVal


def test_diagnose_ok():
    r = diagnose(OpExpr("ADD", [LitExpr(1), LitExpr(2)]))
    assert isinstance(r, DiagnoseOk)
    assert r.ok
    assert r.typ is I32


def test_diagnose_mismatch():
    r = diagnose(OpExpr("ADD", [LitExpr(1), LitExpr(True)]))
    assert isinstance(r, DiagnoseErr)
    assert not r.ok
    assert isinstance(r.error, ErrorVal)
    assert r.error.err.kind == "TYPE_MISMATCH"
    assert r.error.err.op == "ADD"
    assert r.air.startswith("ERR[TYPE_MISMATCH")
    assert len(r.err_expr.fixes) >= 1
    assert r.error.err.repair  # machine-readable suggestions


def test_diagnose_unbound():
    from golem.ast import IdentExpr

    r = diagnose(IdentExpr("nope"))
    assert isinstance(r, DiagnoseErr)
