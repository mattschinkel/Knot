from knot.ast import FnExpr
def test_fnexpr_repr():
    fnexpr = FnExpr(1, [2, 3])
    assert fnexpr.name == 1
    assert fnexpr.args == [2, 3]


def test_fnexpr_children():
    fnexpr = FnExpr(1, [2, 3])
    assert list(fnexpr.children) == [2, 3]
r1 == fnexpr2
    assert fnexpr1 != FnExpr(1, [4, 5])
