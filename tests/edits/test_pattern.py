"""REPLACE_MATCH with _ wildcard (Phase 6 T3)."""

from __future__ import annotations

from golem.ast import IdentExpr, LitExpr, OpExpr
from golem.edits import apply_edit, find_matches, matches, replace_match


def test_wildcard_matches():
    pat = OpExpr("GE", [IdentExpr("_"), LitExpr(18)])
    node = OpExpr("GE", [IdentExpr("age"), LitExpr(18)])
    assert matches(pat, node)
    assert not matches(pat, OpExpr("GT", [IdentExpr("age"), LitExpr(18)]))


def test_replace_match_unique():
    root = OpExpr(
        "ADD",
        [OpExpr("GE", [IdentExpr("x"), LitExpr(18)]), LitExpr(1)],
    )
    pat = OpExpr("GE", [IdentExpr("_"), LitExpr(18)])
    rep = OpExpr("GT", [IdentExpr("x"), LitExpr(18)])
    out = replace_match(root, pat, rep)
    assert out.children[0].op == "GT"


def test_replace_match_none():
    root = OpExpr("ADD", [LitExpr(1), LitExpr(2)])
    try:
        replace_match(root, OpExpr("GE", [IdentExpr("_"), LitExpr(18)]), LitExpr(0))
        assert False
    except LookupError as e:
        assert "no match" in str(e)


def test_replace_match_ambiguous():
    root = OpExpr(
        "ADD",
        [
            OpExpr("GE", [IdentExpr("a"), LitExpr(18)]),
            OpExpr("GE", [IdentExpr("b"), LitExpr(18)]),
        ],
    )
    pat = OpExpr("GE", [IdentExpr("_"), LitExpr(18)])
    try:
        replace_match(root, pat, LitExpr(0))
        assert False
    except LookupError as e:
        assert "ambiguous" in str(e)


def test_apply_replace_match():
    root = OpExpr(
        "IF",
        [
            OpExpr("GE", [IdentExpr("x"), LitExpr(18)]),
            LitExpr(1),
            LitExpr(0),
        ],
    )
    edit = OpExpr(
        "REPLACE_MATCH",
        [
            OpExpr("GE", [IdentExpr("_"), LitExpr(18)]),
            OpExpr("GT", [IdentExpr("x"), LitExpr(18)]),
        ],
    )
    r = apply_edit(root, edit)
    assert r.ok
    assert r.root.children[0].op == "GT"
