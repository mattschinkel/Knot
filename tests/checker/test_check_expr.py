def test_check_expr_litexpr():
    from knot.ast import LitExpr
    from knot.values import IntVal
    from knot.checker import check_expr

    node = LitExpr(1)
    result = check_expr(node)
    assert result is not None
    assert isinstance(result, IntVal)


def test_check_expr_identexpr():
    from knot.ast import IdentExpr
    from knot.values import IntVal
    from knot.checker import check_expr

    node = IdentExpr('x')
    result = check_expr(node)
    assert result is not None
    assert isinstance(result, IntVal)


def test_check_expr_ifexpr():
    from knot.ast import IfExpr
    from knot.values import BoolVal
    from knot.checker import check_expr

    node = IfExpr(IfExpr(IfExpr(LitExpr(1), LitExpr(2), LitExpr(3)), LitExpr(4), LitExpr(5)), LitExpr(6), LitExpr(7))
    result = check_expr(node)
    assert result is not None
    assert isinstance(result, BoolVal)


def test_check_expr_callexpr():
    from knot.ast import CallExpr
    from knot.values import IntVal
    from knot.checker import check_expr

    node = CallExpr('f', [LitExpr(1)])
    result = check_expr(node)
    assert result is not None
    assert isinstance(result, IntVal)


def test_check_expr_defnode():
    from knot.ast import DefNode
    from knot.values import IntVal
    from knot.checker import check_expr

    node = DefNode('x', LitExpr(1))
    result = check_expr(node)
    assert result is not None
    assert isinstance(result, IntVal)


def test_check_expr_fnexpr():
    from knot.ast import FnExpr
    from knot.values import IntVal
    from knot.checker import check_expr

    node = FnExpr('f', [LitExpr(1)], LitExpr(2))
    result = check_expr(node)
    assert result is not None
    assert isinstance(result, IntVal)


def test_check_expr_holeexpr():
    from knot.ast import HoleExpr
    from knot.values import IntVal
    from knot.checker import check_expr

    node = HoleExpr()
    result = check_expr(node)
    assert result is not None
    assert isinstance(result, IntVal)


def test_check_expr_opexpr():
    from knot.ast import OpExpr
    from knot.values import IntVal
    from knot.checker import check_expr

    node = OpExpr('+', [LitExpr(1), LitExpr(2)])
    result = check_expr(node)
    assert result is not None
    assert isinstance(result, IntVal)
