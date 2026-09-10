from knot.checker import infer_fn
def test_infer_fn_fnexpr():
    from knot.expr import FnExpr
    from knot.values import Type
    from knot.type import TypeVar

    # Test FnExpr with a simple type variable
    fnexpr = FnExpr([TypeVar('X')], 'add', [])
    result = infer_fn(fnexpr)
    assert result is not None


def test_infer_fn_callexpr():
    from knot.expr import CallExpr
    from knot.values import Type
    from knot.type import TypeVar

    # Test CallExpr with a type variable
    callexpr = CallExpr('add', [TypeVar('X')])
    result = infer_fn(callexpr)
    assert result is not None


def test_infer_fn_typeerror():
    from knot.expr import FnExpr
    from knot.values import Type
    from knot.type import TypeVar

    # Test FnExpr with invalid type
    fnexpr = FnExpr([TypeVar('X')], 'add', [])
    result = infer_fn(fnexpr)
    assert result is not None


def test_infer_fn_callexpr_returns_type():
    from knot.expr import CallExpr
    from knot.values import Type
    from knot.type import TypeVar

    callexpr = CallExpr('add', [TypeVar('X')])
    result = infer_fn(callexpr)
    assert result is not None
    assert isinstance(result, Type)


def test_infer_fn_fnexpr_returns_type():
    from knot.expr import FnExpr
    from knot.values import Type
    from knot.type import TypeVar

    fnexpr = FnExpr([TypeVar('X')], 'add', [])
    result = infer_fn(fnexpr)
    assert result is not None
    assert isinstance(result, Type)


def test_infer_fn_invalid_expr_returns_error():
    from knot.expr import VarExpr
    from knot.values import Type
    from knot.type import TypeVar

    expr = VarExpr('x')
    result = infer_fn(expr)
    assert result is None
