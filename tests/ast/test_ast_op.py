from knot.ast import OpExpr


def test_opexpr_init():
    expr = OpExpr("+", [1, 2])
    assert expr.op == "+"
    assert expr.children == [1, 2]


def test_opexpr_repr():
    expr = OpExpr("+", [1, 2])
    assert repr(expr) == "OpExpr(op='+', children=[1, 2])"


def test_opexpr_eq():
    expr1 = OpExpr("+", [1, 2])
    expr2 = OpExpr("+", [1, 2])
    assert expr1 == expr2
    assert hash(expr1) == hash(expr2)


def test_opexpr_ne():
    expr1 = OpExpr("+", [1, 2])
    expr2 = OpExpr("*", [1, 2])
    assert expr1 != expr2
    expr3 = OpExpr("+", [1, 3])
    assert expr1 != expr3


def test_opexpr_lt_by_id():
    # OpExpr defaults id=0; ordering uses ExprNode.__lt__ (by id).
    expr1 = OpExpr("+", [1, 2], id=1)
    expr2 = OpExpr("+", [1, 3], id=2)
    assert expr1 < expr2


def test_opexpr_children():
    expr = OpExpr("+", [1, 2])
    assert len(expr.children) == 2
    assert expr.children[0] == 1
    assert expr.children[1] == 2


def test_opexpr_empty_children():
    expr = OpExpr("+", [])
    assert len(expr.children) == 0


def test_opexpr_op_type():
    expr = OpExpr("+", [1, 2])
    assert isinstance(expr.op, str)
    assert expr.op == "+"
