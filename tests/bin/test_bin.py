def test_serialize_int():
    from knot.bin import serialize
    from knot.values import IntVal

    val = IntVal(42)
    result = serialize(val, (1,))
    assert result == '{"id": 1, "path": [1], "label": null, "children": []}'


def test_serialize_string():
    from knot.bin import serialize
    from knot.values import StringVal

    val = StringVal("hello")
    result = serialize(val, (1,))
    assert result == '{"id": 1, "path": [1], "label": null, "children": []}'


def test_serialize_bool():
    from knot.bin import serialize
    from knot.values import BoolVal

    val = BoolVal(True)
    result = serialize(val, (1,))
    assert result == '{"id": 1, "path": [1], "label": null, "children": []}'


def test_serialize_list():
    from knot.bin import serialize
    from knot.values import ListVal

    val = ListVal([IntVal(1), IntVal(2)])
    result = serialize(val, (1,))
    assert result == '{"id": 1, "path": [1], "label": null, "children": []}'


def test_serialize_dict():
    from knot.bin import serialize
    from knot.values import DictVal

    val = DictVal({IntVal(1): StringVal("a")})
    result = serialize(val, (1,))
    assert result == '{"id": 1, "path": [1], "label": null, "children": []}'


def test_serialize_nested():
    from knot.bin import serialize
    from knot.values import IntVal

    val = IntVal(42)
    result = serialize(val, (1, 2))
    assert result == '{"id": 1, "path": [1, 2], "label": null, "children": []}'


def test_serialize_with_label():
    from knot.bin import serialize
    from knot.values import IntVal

    val = IntVal(42)
    result = serialize(val, (1,))
    assert result == '{"id": 1, "path": [1], "label": null, "children": []}'


def test_serialize_empty_children():
    from knot.bin import serialize
    from knot.values import IntVal

    val = IntVal(42)
    result = serialize(val, (1,))
    assert result == '{"id": 1, "path": [1], "label": null, "children": []}'


def test_serialize_with_path_tuple():
    from knot.bin import serialize
    from knot.values import IntVal

    val = IntVal(42)
    result = serialize(val, (1, 2, 3))
    assert result == '{"id": 1, "path": [1, 2, 3], "label": null, "children": []}'
