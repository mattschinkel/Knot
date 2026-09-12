"""apply_edit REPLACE/DELETE/INSERT/RENAME (Phase 6 T2)."""

from __future__ import annotations

from golem.ast import DefNode, IdentExpr, LitExpr, OpExpr
from golem.edits import apply_edit, get_at
from golem.partial import CompileStatus


def test_apply_replace():
    root = OpExpr("ADD", [LitExpr(1), LitExpr(2)])
    edit = OpExpr("REPLACE", [OpExpr("LIST", [LitExpr(1)]), LitExpr(5)])
    r = apply_edit(root, edit)
    assert r.ok
    assert get_at(r.root, (1,)).value == 5
    assert r.revalidation.status is CompileStatus.VALID


def test_apply_delete():
    root = OpExpr("ADD", [LitExpr(1), LitExpr(2), LitExpr(3)])
    edit = OpExpr("DELETE", [OpExpr("LIST", [LitExpr(1)])])
    r = apply_edit(root, edit)
    assert r.ok
    assert len(r.root.children) == 2


def test_apply_insert():
    root = OpExpr("ADD", [LitExpr(1), LitExpr(3)])
    edit = OpExpr(
        "INSERT",
        [OpExpr("LIST", []), LitExpr(1), LitExpr(2)],
    )
    r = apply_edit(root, edit)
    assert r.ok
    assert [c.value for c in r.root.children] == [1, 2, 3]


def test_apply_rename_def():
    d = DefNode("old", LitExpr(1))
    edit = OpExpr("RENAME", [OpExpr("LIST", []), IdentExpr("new")])
    r = apply_edit(d, edit)
    assert r.ok
    assert r.root.name == "new"


def test_apply_bad_path():
    root = OpExpr("ADD", [LitExpr(1)])
    edit = OpExpr("REPLACE", [OpExpr("LIST", [LitExpr(9)]), LitExpr(0)])
    r = apply_edit(root, edit)
    assert not r.ok
    assert r.error is not None
