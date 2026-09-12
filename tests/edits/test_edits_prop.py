"""Property tests for edits (Phase 6 T5)."""

from __future__ import annotations

from knot.ast import IdentExpr, LitExpr, OpExpr
from knot.edits import apply_edit, get_at, replace_at


def test_no_raise():
    roots = [
        OpExpr("ADD", [LitExpr(1), LitExpr(2)]),
        OpExpr("GE", [IdentExpr("x"), LitExpr(18)]),
    ]
    edits = [
        OpExpr("REPLACE", [OpExpr("LIST", [LitExpr(0)]), LitExpr(9)]),
        OpExpr("DELETE", [OpExpr("LIST", [LitExpr(0)])]),
        OpExpr(
            "REPLACE_MATCH",
            [
                OpExpr("GE", [IdentExpr("_"), LitExpr(18)]),
                OpExpr("GT", [IdentExpr("x"), LitExpr(18)]),
            ],
        ),
    ]
    for root in roots:
        for edit in edits:
            r = apply_edit(root, edit)
            assert r.ok in (True, False)
            if r.ok:
                assert r.root is not None
                assert isinstance(r.blast_radius, tuple)


def test_replace_preserves_untouched():
    root = OpExpr("ADD", [LitExpr(1), LitExpr(2)])
    new = replace_at(root, (0,), LitExpr(8))
    assert get_at(new, (1,)).value == 2
    assert get_at(root, (0,)).value == 1
