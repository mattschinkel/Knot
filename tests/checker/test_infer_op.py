def test_infer_type_ident_expr():
    from knot.checker import infer_type
    from knot.values import IntVal
    from knot.ast import IdentExpr
    from knot.types import Type

    expr = IdentExpr(id=1)
    result = infer_type(expr)
    assert result is not None


def test_infer_type_lit_expr():
    from knot.checker import infer_type
    from knot.ast import LitExpr
    from knot.types import I32

    expr = LitExpr(value=I32(5))
    result = infer_type(expr)
    assert result is not None


def test_infer_type_unit_expr():
    from knot.checker import infer_type
    from knot.ast import UnitExpr
    from knot.types import I32

    expr = UnitExpr()
    result = infer_type(expr)
    assert result is not None


def test_infer_type_add_expr():
    from knot.checker import infer_type
    from knot.ast import BinOpExpr
    from knot.types import I32

    expr = BinOpExpr(left=I32(5), right=I32(3), op='+')
    result = infer_type(expr)
    assert result is not None


def test_infer_type_sub_expr():
    from knot.checker import infer_type
    from knot.ast import BinOpExpr
    from knot.types import I32

    expr = BinOpExpr(left=I32(5), right=I32(3), op='-')
    result = infer_type(expr)
    assert result is not None


def test_infer_type_mul_expr():
    from knot.checker import infer_type
    from knot.ast import BinOpExpr
    from knot.types import I32

    expr = BinOpExpr(left=I32(5), right=I32(3), op='*')
    result = infer_type(expr)
    assert result is not None


def test_infer_type_neg_expr():
    from knot.checker import infer_type
    from knot.ast import UnOpExpr
    from knot.types import I32

    expr = UnOpExpr(op='-', value=I32(5))
    result = infer_type(expr)
    assert result is not None


def test_infer_type_not_expr():
    from knot.checker import infer_type
    from knot.ast import UnOpExpr
    from knot.types import I32

    expr = UnOpExpr(op='not', value=I32(5))
    result = infer_type(expr)
    assert result is not None


def test_infer_type_ident_with_env():
    from knot.checker import infer_type
    from knot.ast import IdentExpr
    from knot.types import Type

    expr = IdentExpr(id=1)
    result = infer_type(expr)
    assert result is not None


def test_infer_type_nested_binop():
    from knot.checker import infer_type
    from knot.ast import BinOpExpr
    from knot.types import I32

    expr = BinOpExpr(left=BinOpExpr(left=I32(5), right=I32(3), op='+'),
                    right=I32(2), op='*')
    result = infer_type(expr)
    assert result is not None


def test_infer_type_op_expr():
    from knot.checker import infer_type
    from knot.ast import OpExpr
    from knot.types import I32

    expr = OpExpr(op='+', left=I32(5), right=I32(3))
    result = infer_type(expr)
    assert result is not None


def test_infer_type_invalid_type():
    from knot.checker import infer_type
    from knot.ast import IdentExpr

    expr = IdentExpr(id=1)
    result = infer_type(expr)
    assert result is not None


def test_infer_type_binop_expr():
    from knot.checker import infer_type
    from knot.ast import BinOpExpr
    from knot.types import I32

    expr = BinOpExpr(
        left=I32(5),
        right=I32(3),
        op='+'
    )
    result = infer_type(expr)
    assert result is not None
