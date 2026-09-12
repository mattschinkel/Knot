from golem.ast import HoleExpr
def test_holeexpr_id():
    expr = HoleExpr(id=1)
    assert expr.id == 1


def test_holeexpr_path():
    expr = HoleExpr(id=1, path=[1, 2, 3])
    assert expr.path == [1, 2, 3]


def test_holeexpr_label():
    expr = HoleExpr(id=1, label="test_label")
    assert expr.label == "test_label"


def test_holeexpr_children():
    expr = HoleExpr(id=1)
    assert expr.children == ()


def test_holeexpr_eq():
    expr1 = HoleExpr(id=1)
    expr2 = HoleExpr(id=1)
    assert expr1 == expr2


def test_holeexpr_hash():
    expr1 = HoleExpr(id=1)
    expr2 = HoleExpr(id=1)
    assert hash(expr1) == hash(expr2)


def test_holeexpr_lt():
    expr1 = HoleExpr(id=1)
    expr2 = HoleExpr(id=2)
    assert expr1 < expr2


def test_holeexpr_repr():
    expr = HoleExpr(id=1)
    assert expr.id == 1
    assert "HoleExpr" in repr(expr)
    assert "1" in repr(expr)


def test_holeexpr_repr_fixed():
    expr = HoleExpr(id=1)
    assert repr(expr) == "HoleExpr(id=1, path=[], label=None, children=())"


def test_holeexpr_repr_correct():
    expr = HoleExpr(id=1)
    assert repr(expr) == "HoleExpr(id=1, path=[], label=None, children=())"


def test_holeexpr_repr_expected():
    expr = HoleExpr(id=1)
    assert repr(expr) == "HoleExpr(id=1, path=[], label=None, children=())"


def test_holeexpr_repr_exact():
    expr = HoleExpr(id=1)
    assert repr(expr) == "HoleExpr(id=1, path=[], label=None, children=())"


def test_holeexpr_all_fields():
    expr = HoleExpr(id=1, path=[1, 2, 3], label="test_label")
    assert expr.id == 1
    assert expr.path == [1, 2, 3]
    assert expr.label == "test_label"
    assert expr.children == ()
