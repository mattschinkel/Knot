def test_check_binary_op_add_int():
    from knot.values import IntVal
    from knot.types import I64
    from knot.checker import check_binary_op

    left = IntVal(10)
    right = IntVal(5)
    result = check_binary_op("ADD", left, right)
    assert result.type == I64


def test_check_binary_op_add_float():
    from knot.values import FloatVal
    from knot.types import F64
    from knot.checker import check_binary_op

    left = FloatVal(10.5)
    right = FloatVal(5.2)
    result = check_binary_op("ADD", left, right)
    assert result.type == F64


def test_check_binary_op_mul_int():
    from knot.values import IntVal
    from knot.types import I64
    from knot.checker import check_binary_op

    left = IntVal(10)
    right = IntVal(5)
    result = check_binary_op("MUL", left, right)
    assert result.type == I64


def test_check_binary_op_div_float():
    from knot.values import FloatVal
    from knot.types import F64
    from knot.checker import check_binary_op

    left = FloatVal(10.5)
    right = FloatVal(5.2)
    result = check_binary_op("DIV", left, right)
    assert result.type == F64


def test_check_binary_op_mod_int():
    from knot.values import IntVal
    from knot.types import I64
    from knot.checker import check_binary_op

    left = IntVal(10)
    right = IntVal(5)
    result = check_binary_op("MOD", left, right)
    assert result.type == I64


def test_check_binary_op_unknown_op():
    from knot.checker import check_binary_op

    left = IntVal(10)
    right = IntVal(5)
    try:
        check_binary_op("UNKNOWN", left, right)
        assert False, "Should raise TypeError"
    except TypeError:
        pass

    try:
        check_binary_op("ADD", FloatVal(10.5), IntVal(5))
        assert False, "Should raise TypeError"
    except TypeError:
        pass


def test_check_binary_op_sub_int():
    from knot.values import IntVal
    from knot.types import I64
    from knot.checker import check_binary_op

    left = IntVal(10)
    right = IntVal(5)
    result = check_binary_op("SUB", left, right)
    assert result.type == I64


def test_check_binary_op_mul_float():
    from knot.values import FloatVal
    from knot.types import F64
    from knot.checker import check_binary_op

    left = FloatVal(10.5)
    right = FloatVal(5.2)
    result = check_binary_op("MUL", left, right)
    assert result.type == F64
