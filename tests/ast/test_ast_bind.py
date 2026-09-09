from knot.ast import LetExpr
def test_letexpr_id():
    expr = LetExpr(id=1, path=[1], label=None, children=[1])
    assert expr.id == 1
    assert expr.path == [1]
    assert expr.label is None
    assert len(expr.children) == 1

def test_letexpr_path():
    expr = LetExpr(id=2, path=[2, 3], label=None, children=[2, 3])
    assert expr.id == 2
    assert expr.path == [2, 3]
    assert expr.label is None
    assert len(expr.children) == 2

def test_letexpr_label():
    expr = LetExpr(id=3, path=[3], label="test", children=[3])
    assert expr.id == 3
    assert expr.path == [3]
    assert expr.label == "test"
    assert len(expr.children) == 1


def test_letexpr_id():
    expr = LetExpr(id=1, path=[1], label=None)
    assert expr.id == 1
    assert expr.path == [1]
    assert expr.label is None
    assert len(expr.children) == 0

def test_letexpr_path():
    expr = LetExpr(id=2, path=[2, 3], label=None)
    assert expr.id == 2
    assert expr.path == [2, 3]
    assert expr.label is None
    assert len(expr.children) == 0

def test_letexpr_label():
    expr = LetExpr(id=3, path=[3], label="test")
    assert expr.id == 3
    assert expr.path == [3]
    assert expr.label == "test"
    assert len(expr.children) == 0
