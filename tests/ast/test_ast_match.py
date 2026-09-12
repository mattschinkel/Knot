"""MatchExpr Stage 0.5 shape: MATCH[scrutinee, CASE...]."""

from golem.ast import LitExpr, MatchCase, MatchExpr


def test_matchexpr_repr():
    node = MatchExpr(scrutinee=LitExpr(1), cases=[])
    assert "MatchExpr" in repr(node)


def test_matchexpr_eq():
    a = MatchExpr(LitExpr(1), [MatchCase("A", LitExpr(2))])
    b = MatchExpr(LitExpr(1), [MatchCase("A", LitExpr(2))])
    assert a == b


def test_matchexpr_hash():
    node = MatchExpr(LitExpr(1), [])
    assert hash(node) is not None


def test_matchexpr_children():
    body = LitExpr(9)
    node = MatchExpr(LitExpr(1), [MatchCase("T", body)])
    kids = node.children
    assert kids[0] == LitExpr(1)
    assert kids[1] == body


def test_matchcase_binding():
    c = MatchCase("Lit", LitExpr(0), binding="x")
    assert c.tag == "Lit" and c.binding == "x"
