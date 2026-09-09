from knot.ast import FnExpr
def test_fnexpr_id():
    expr = FnExpr(id=1, path=[1, 2], label=None, children=())
    assert expr.id == 1
    assert expr.path == [1, 2]
    assert expr.label is None
    assert len(list(expr.children)) == 0

def test_fnexpr_with_children():
    child1 = FnExpr(id=10, path=[10], label=None, children=())
    child2 = FnExpr(id=11, path=[11], label=None, children=())
    expr = FnExpr(id=1, path=[1, 2], label=None, children=(child1, child2))
    assert expr.id == 1
    assert expr.path == [1, 2]
    assert expr.label is None
    assert len(list(expr.children)) == 2


def test_fnexpr_id():
    expr = FnExpr(1, [1, 2], label=None, children=())
    assert expr.id == 1
    assert expr.path == [1, 2]
    assert expr.label is None
    assert len(list(expr.children)) == 0

def test_fnexpr_with_children():
    child1 = FnExpr(10, [10], label=None, children=())
    child2 = FnExpr(11, [11], label=None, children=())
    expr = FnExpr(1, [1, 2], label=None, children=(child1, child2))
    assert expr.id == 1
    assert expr.path == [1, 2]
    assert expr.label is None
    assert len(list(expr.children)) == 2
