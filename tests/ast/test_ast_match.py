def test_matchexpr_repr():
    from knot.ast import MatchExpr
    node = MatchExpr(pattern=None, body=None)
    assert repr(node) == 'MatchExpr(pattern=None, body=None)'


def test_matchexpr_eq():
    from knot.ast import MatchExpr
    node1 = MatchExpr(pattern=None, body=None)
    node2 = MatchExpr(pattern=None, body=None)
    assert node1 == node2


def test_matchexpr_hash():
    from knot.ast import MatchExpr
    node = MatchExpr(pattern=None, body=None)
    assert hash(node) is not None


def test_matchexpr_lt():
    from knot.ast import MatchExpr
    node1 = MatchExpr(pattern=None, body=None)
    node2 = MatchExpr(pattern=None, body=None)
    assert node1 < node2


def test_matchexpr_children():
    from knot.ast import MatchExpr
    node = MatchExpr(pattern=None, body=None)
    children = node.children
    assert len(children) == 2
    assert children[0] is None
    assert children[1] is None


def test_matchexpr_pattern_repr():
    from knot.ast import MatchExpr
    node = MatchExpr(pattern=None, body=None)
    assert node.pattern is None


def test_matchexpr_body_repr():
    from knot.ast import MatchExpr
    node = MatchExpr(pattern=None, body=None)
    assert node.body is None
