def test_infer_type_int():
    from knot.values import IntVal
    from knot.checker import infer_type

    node = IntVal(42)
    path = (1,)
    result = infer_type(node, path)
    assert result == IntVal(42)


def test_infer_type_int():
    from knot.values import IntVal
    from knot.checker import infer_type

    node = IntVal(42)
    path = (1,)
    result = infer_type(node, path)
    assert result == IntVal(42)


def test_infer_type_bool():
    from knot.values import BoolVal
    from knot.checker import infer_type

    node = BoolVal(True)
    path = (1,)
    result = infer_type(node, path)
    assert result == BoolVal(True)


def test_infer_type_int():
    from knot.values import IntVal
    from knot.checker import infer_type

    node = IntVal(42)
    path = (1,)
    result = infer_type(node, path)
    assert result == IntVal(42)

def test_infer_type_bool():
    from knot.values import BoolVal
    from knot.checker import infer_type

    node = BoolVal(True)
    path = (1,)
    result = infer_type(node, path)
    assert result == BoolVal(True)


def test_infer_type_int():
    from knot.values import IntVal
    from knot.checker import infer_type

    node = IntVal(42)
    path = (1,)
    result = infer_type(node, path)
    assert result == IntVal(42)

def test_infer_type_bool():
    from knot.values import BoolVal
    from knot.checker import infer_type

    node = BoolVal(True)
    path = (1,)
    result = infer_type(node, path)
    assert result == BoolVal(True)


def test_infer_type_tuple():
    from knot.values import TupleVal
    from knot.checker import infer_type

    node = TupleVal([IntVal(1), IntVal(2)])
    path = (1,)
    result = infer_type(node, path)
    assert result == TupleVal([IntVal(1), IntVal(2)])


def test_infer_type_bool():
    from knot.values import BoolVal
    from knot.checker import infer_type

    node = BoolVal(True)
    path = (1,)
    result = infer_type(node, path)
    assert result == BoolVal(True)


def test_infer_type_tuple():
    from knot.values import TupleVal
    from knot.checker import infer_type

    node = TupleVal([IntVal(1), IntVal(2)])
    path = (1,)
    result = infer_type(node, path)
    assert result == TupleVal([IntVal(1), IntVal(2)])


def test_infer_type_int():
    from knot.values import IntVal
    from knot.checker import infer_type

    node = IntVal(42)
    path = (1,)
    result = infer_type(node, path)
    assert result == IntVal(42)
l(True)


def test_infer_type_tuple():
    from knot.values import TupleVal, IntVal
    from knot.checker import infer_type

    node = TupleVal([IntVal(1), IntVal(2)])
    path = (1,)
    result = infer_type(node, path)
    assert result == TupleVal([IntVal(1), IntVal(2)])
