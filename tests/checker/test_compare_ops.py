def test_check_compare_op_eq_any_type():
    from knot.types import I32, F64
    from knot.checker import check_compare_op
    from knot import TypeErrorVal

    # EQ with any type should return Bool
    assert check_compare_op(I32(1), I32(2), 'EQ') is not TypeErrorVal
    assert check_compare_op(F64(1.5), F64(2.5), 'EQ') is not TypeErrorVal

    # Should return Bool type
    result = check_compare_op(I32(1), I32(1), 'EQ')
    assert result.type == 'BOOL'


def test_check_compare_op_eq_int():
    from knot.types import I32
    from knot.checker import check_compare_op

    result = check_compare_op(I32(1), I32(2), 'EQ')
    assert result.type == 'BOOL'

    result = check_compare_op(I32(1), I32(1), 'EQ')
    assert result.type == 'BOOL'

    result = check_compare_op(I32(1), I32(2), 'NE')
    assert result.type == 'BOOL'

    result = check_compare_op(I32(1), I32(1), 'NE')
    assert result.type == 'BOOL'


def test_check_compare_op_lt_le_gt_ge_numeric():
    from knot.types import I32, F64
    from knot.checker import check_compare_op

    # LT, LE, GT, GE with numeric types
    assert check_compare_op(I32(1), I32(2), 'LT') is not TypeErrorVal
    assert check_compare_op(I32(1), I32(2), 'LE') is not TypeErrorVal
    assert check_compare_op(I32(2), I32(1), 'GT') is not TypeErrorVal
    assert check_compare_op(I32(2), I32(2), 'GE') is not TypeErrorVal

    # Should return Bool
    result = check_compare_op(I32(1), I32(2), 'LT')
    assert result.type == 'BOOL'

    result = check_compare_op(F64(1.5), F64(2.5), 'GT')
    assert result.type == 'BOOL'


def test_check_compare_op_lt_numeric():
    from knot.types import I32, F64
    from knot.checker import check_compare_op

    result = check_compare_op(I32(1), I32(2), 'LT')
    assert result.type == 'BOOL'

    result = check_compare_op(F64(1.5), F64(2.5), 'LT')
    assert result.type == 'BOOL'

    result = check_compare_op(I32(1), F64(2.5), 'LT')
    assert result.type == 'BOOL'


def test_check_compare_op_gt_numeric():
    from knot.types import I32, F64
    from knot.checker import check_compare_op

    result = check_compare_op(I32(1), I32(2), 'GT')
    assert result.type == 'BOOL'

    result = check_compare_op(F64(1.5), F64(2.5), 'GT')
    assert result.type == 'BOOL'

    result = check_compare_op(I32(1), F64(2.5), 'GT')
    assert result.type == 'BOOL'


def test_check_compare_op_le_numeric():
    from knot.types import I32, F64
    from knot.checker import check_compare_op

    result = check_compare_op(I32(1), I32(2), 'LE')
    assert result.type == 'BOOL'

    result = check_compare_op(F64(1.5), F64(2.5), 'LE')
    assert result.type == 'BOOL'

    result = check_compare_op(I32(1), F64(2.5), 'LE')
    assert result.type == 'BOOL'


def test_check_compare_op_ge_numeric():
    from knot.types import I32, F64
    from knot.checker import check_compare_op

    result = check_compare_op(I32(1), I32(2), 'GE')
    assert result.type == 'BOOL'

    result = check_compare_op(F64(1.5), F64(2.5), 'GE')
    assert result.type == 'BOOL'

    result = check_compare_op(I32(1), F64(2.5), 'GE')
    assert result.type == 'BOOL'
