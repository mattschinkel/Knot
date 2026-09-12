"""blast_radius + revalidation (Phase 6 T4)."""

from __future__ import annotations

from golem.ast import LitExpr, OpExpr
from golem.edits import apply_edit, blast_radius
from golem.partial import CompileStatus


def test_blast_radius_ancestors():
    assert blast_radius((1, 2)) == ((), (1,), (1, 2))


def test_edit_reports_blast_and_revalidation():
    root = OpExpr("ADD", [LitExpr(1), LitExpr(2)])
    edit = OpExpr("REPLACE", [OpExpr("LIST", [LitExpr(1)]), LitExpr(True)])
    r = apply_edit(root, edit)
    assert r.ok  # edit applied
    assert (1,) in r.blast_radius
    assert () in r.blast_radius
    # ADD[1,true] is INVALID after revalidation
    assert r.revalidation.status is CompileStatus.INVALID


def test_good_edit_still_valid():
    root = OpExpr("ADD", [LitExpr(1), LitExpr(2)])
    edit = OpExpr("REPLACE", [OpExpr("LIST", [LitExpr(1)]), LitExpr(3)])
    r = apply_edit(root, edit)
    assert r.revalidation.status is CompileStatus.VALID
