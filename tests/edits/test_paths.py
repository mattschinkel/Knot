"""Structural path get/replace/delete/insert (Phase 6 T1)."""

from __future__ import annotations

from golem.ast import DefNode, IdentExpr, LitExpr, OpExpr
from golem.edits import delete_at, get_at, insert_at, replace_at


def test_get_at_index():
    root = OpExpr("ADD", [LitExpr(1), LitExpr(2)])
    assert get_at(root, (0,)).value == 1
    assert get_at(root, (1,)).value == 2


def test_replace_at_immutable():
    root = OpExpr("ADD", [LitExpr(1), LitExpr(2)])
    new = replace_at(root, (1,), LitExpr(9))
    assert get_at(new, (1,)).value == 9
    assert get_at(root, (1,)).value == 2


def test_replace_def_body():
    d = DefNode("x", OpExpr("ADD", [LitExpr(1), LitExpr(2)]))
    new = replace_at(d, ("body", 0), LitExpr(7))
    assert get_at(new, ("body", 0)).value == 7
    assert d.body.children[0].value == 1


def test_delete_at():
    root = OpExpr("ADD", [LitExpr(1), LitExpr(2), LitExpr(3)])
    new = delete_at(root, (1,))
    assert [c.value for c in new.children] == [1, 3]


def test_insert_at():
    root = OpExpr("ADD", [LitExpr(1), LitExpr(3)])
    new = insert_at(root, (), 1, LitExpr(2))
    assert [c.value for c in new.children] == [1, 2, 3]


def test_program_list_by_name():
    prog = [DefNode("a", LitExpr(1)), DefNode("b", LitExpr(2))]
    assert get_at(prog, ("b",)).name == "b"
    new = replace_at(prog, ("a",), DefNode("a", LitExpr(9)))
    assert get_at(new, ("a", "body")).value == 9
