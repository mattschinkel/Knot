from knot.ast import FnExpr, LitExpr


def test_fnexpr_params_and_body():
    body = LitExpr(1)
    expr = FnExpr([("x", None)], body, id=1, path=[1, 2])
    assert expr.id == 1
    assert expr.path == [1, 2]
    assert expr.params == [("x", None)]
    assert expr.body is body
    assert expr.children == (body,)


def test_fnexpr_eq():
    body = LitExpr(1)
    a = FnExpr([("x", None)], body)
    b = FnExpr([("x", None)], LitExpr(1))
    c = FnExpr([("y", None)], LitExpr(1))
    assert a == b
    assert a != c
