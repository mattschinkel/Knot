from knot.checker import check_collection
def test_check_collection_len():
    from knot.values import IntVal
    from knot.types import Type, TypeError

    env = {}
    call_expr = CallExpr("LEN", [IntVal(1, 2)])
    base_type = ListType(IntVal)

    result = check_collection(env, call_expr, base_type)
    assert isinstance(result, Type)
    assert result == IntVal


def test_check_collection_at():
    from knot.values import IntVal
    from knot.types import Type, TypeError

    env = {}
    call_expr = CallExpr("AT", [IntVal(1, 2), IntVal(1, 2)])
    base_type = ListType(IntVal)

    result = check_collection(env, call_expr, base_type)
    assert isinstance(result, Type)
    assert result == IntVal


def test_check_collection_append():
    from knot.values import IntVal
    from knot.types import Type, TypeError

    env = {}
    call_expr = CallExpr("APPEND", [IntVal(1, 2), IntVal(1, 2)])
    base_type = ListType(IntVal)

    result = check_collection(env, call_expr, base_type)
    assert isinstance(result, Type)
    assert result == ListType(IntVal)


def test_check_collection_concat():
    from knot.values import IntVal
    from knot.types import Type, TypeError

    env = {}
    call_expr = CallExpr("CONCAT", [IntVal(1, 2), IntVal(1, 2)])
    base_type = ListType(IntVal)

    result = check_collection(env, call_expr, base_type)
    assert isinstance(result, Type)
    assert result == ListType(IntVal)


def test_check_collection_map():
    from knot.values import IntVal
    from knot.types import Type, TypeError

    env = {}
    call_expr = CallExpr("MAP", [IntVal(1, 2), IntVal(1, 2)])
    base_type = ListType(IntVal)

    result = check_collection(env, call_expr, base_type)
    assert isinstance(result, Type)
    assert result == ListType(IntVal)


def test_check_collection_filter():
    from knot.values import IntVal
    from knot.types import Type, TypeError

    env = {}
    call_expr = CallExpr("FILTER", [IntVal(1, 2), IntVal(1, 2)])
    base_type = ListType(IntVal)

    result = check_collection(env, call_expr, base_type)
    assert isinstance(result, Type)
    assert result == ListType(IntVal)


def test_check_collection_len_unique():
    from knot.values import IntVal
    from knot.types import Type, TypeError

    env = {}
    call_expr = CallExpr("LEN", [IntVal(1, 2)])
    base_type = ListType(IntVal)

    result = check_collection(env, call_expr, base_type)
    assert isinstance(result, Type)
    assert result == IntVal


def test_check_collection_at_unique():
    from knot.values import IntVal
    from knot.types import Type, TypeError

    env = {}
    call_expr = CallExpr("AT", [IntVal(1, 2), IntVal(1, 2)])
    base_type = ListType(IntVal)

    result = check_collection(env, call_expr, base_type)
    assert isinstance(result, Type)
    assert result == IntVal


def test_check_collection_append_unique():
    from knot.values import IntVal
    from knot.types import Type, TypeError

    env = {}
    call_expr = CallExpr("APPEND", [IntVal(1, 2), IntVal(1, 2)])
    base_type = ListType(IntVal)

    result = check_collection(env, call_expr, base_type)
    assert isinstance(result, Type)
    assert result == ListType(IntVal)


def test_check_collection_concat_unique():
    from knot.values import IntVal
    from knot.types import Type, TypeError

    env = {}
    call_expr = CallExpr("CONCAT", [ListType(IntVal), ListType(IntVal)])
    base_type = ListType(IntVal)

    result = check_collection(env, call_expr, base_type)
    assert isinstance(result, Type)
    assert result == ListType(IntVal)


def test_check_collection_map_unique():
    from knot.values import IntVal
    from knot.types import Type, TypeError

    env = {}
    call_expr = CallExpr("MAP", [IntVal(1, 2), IntVal(1, 2)])
    base_type = ListType(IntVal)

    result = check_collection(env, call_expr, base_type)
    assert isinstance(result, Type)
    assert result == ListType(IntVal)


def test_check_collection_filter_unique():
    from knot.values import IntVal
    from knot.types import Type, TypeError

    env = {}
    call_expr = CallExpr("FILTER", [IntVal(1, 2), IntVal(1, 2)])
    base_type = ListType(IntVal)

    result = check_collection(env, call_expr, base_type)
    assert isinstance(result, Type)
    assert result == ListType(IntVal)
