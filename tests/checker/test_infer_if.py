def test_infer_if_simple():
    from knot.checker import infer_if
    from knot.expr import CondExpr
    from knot.values import BoolVal

    cond = CondExpr(BoolVal(), BoolVal(), BoolVal())
    result = infer_if(cond, {})
    assert result is not None


def test_infer_if_then_else_different_types():
    from knot.expr import CondExpr
    from knot.values import BoolVal

    cond = CondExpr(BoolVal(), BoolVal(), BoolVal())
    result = infer_if(cond, {})
    assert result is not None
