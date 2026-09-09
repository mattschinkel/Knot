def test_check_unary_op_neg_numeric():
    from knot.types import I32, I64, F32, F64
    from knot.checker import check_unary_op
    from knot.errors import TypeErrorVal

    # NEG on I32
    result = check_unary_op(I32, 5)
    assert result is not TypeErrorVal
    assert result.type == I32

    # NEG on I64
    result = check_unary_op(I64, 10)
    assert result is not TypeErrorVal
    assert result.type == I64

    # NEG on F32
    result = check_unary_op(F32, 3.14)
    assert result is not TypeErrorVal
    assert result.type == F32

    # NEG on F64
    result = check_unary_op(F64, 2.718)
    assert result is not TypeErrorVal
    assert result.type == F64


def test_check_unary_op_neg_non_numeric():
    from knot.types import I32, I64, F32, F64
    from knot.checker import check_unary_op
    from knot.errors import TypeErrorVal

    # NEG on BOOL
    result = check_unary_op(I32, True)
    assert result is TypeErrorVal

    # NEG on String
    result = check_unary_op(I32, "hello")
    assert result is TypeErrorVal

    # NEG on List
    result = check_unary_op(I32, [])
    assert result is TypeErrorVal

    # NEG on Unknown
    result = check_unary_op(I32, None)
    assert result is TypeErrorVal


def test_check_unary_op_not_bool():
    from knot.types import BOOL
    from knot.checker import check_unary_op
    from knot.errors import TypeErrorVal

    # NOT on BOOL
    result = check_unary_op(BOOL, True)
    assert result is not TypeErrorVal
    assert result.type == BOOL

    # NOT on non-BOOL
    result = check_unary_op(BOOL, 5)
    assert result is TypeErrorVal

    result = check_unary_op(BOOL, 3.14)
    assert result is TypeErrorVal

    result = check_unary_op(BOOL, [])
    assert result is TypeErrorVal

    result = check_unary_op(BOOL, None)
    assert result is TypeErrorVal

    result = check_unary_op(BOOL, "hello")
    assert result is TypeErrorVal


def test_check_unary_op_unknown_op():
    from knot.checker import check_unary_op
    from knot.errors import TypeErrorVal

    # Unknown op (should be TypeError)
    result = check_unary_op("unknown", 5)
    assert result is TypeErrorVal

    result = check_unary_op("unknown", True)
    assert result is TypeErrorVal

    result = check_unary_op("unknown", None)
    assert result is TypeErrorVal

    result = check_unary_op("unknown", [])
    assert result is TypeErrorVal

    result = check_unary_op("unknown", "hello")
    assert result is TypeErrorVal


def test_check_unary_op_neg_bool():
    from knot.types import BOOL
    from knot.checker import check_unary_op
    from knot.values import BoolVal

    result = check_unary_op(BOOL, BoolVal(True))
    assert result is not TypeErrorVal
    assert result.type == BOOL

    result = check_unary_op(BOOL, BoolVal(False))
    assert result is not TypeErrorVal
    assert result.type == BOOL


def test_check_unary_op_neg_invalid_type():
    from knot.checker import check_unary_op
    from knot.errors import TypeErrorVal

    result = check_unary_op(str, "hello")
    assert result is TypeErrorVal


def test_check_unary_op_not_invalid_type():
    from knot.checker import check_unary_op
    from knot.errors import TypeErrorVal

    result = check_unary_op(int, 5)
    assert result is TypeErrorVal
