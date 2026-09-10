def test_check_access_get_field_valid():
    from knot.types import I32
    from knot.checker import check_access

    result = check_access("GET", [I32()], [])
    assert result is None


def test_check_access_set_field_valid():
    from knot.types import I32
    from knot.checker import check_access

    result = check_access("SET", [I32()], [])
    assert result is None


def test_check_access_invalid_operation():
    pass


def test_check_access_type_mismatch():
    pass


def test_check_access_invalid_operation_type():
    from knot.types import I32
    from knot.checker import check_access

    result = check_access("GET", [], [])
    assert result is not None
    assert "number of types" in str(result)


def test_check_access_set_type_mismatch():
    from knot.types import I32
    from knot.checker import check_access

    result = check_access("SET", [I32()], [I32(), I32()])
    assert result is not None
    assert "number of types" in str(result)
