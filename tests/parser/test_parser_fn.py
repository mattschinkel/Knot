from knot.parser import parse_def
def test_parse_def_simple():
    result = parse_def("def f() = 1")
    assert result[0].id == 1
    assert result[0].name == 'f'
    assert result[0].args == []
    assert result[0].body == [1]


def test_parse_def_with_args():
    result = parse_def("def f(x, y) = 1")
    assert result[0].id == 1
    assert result[0].name == 'f'
    assert result[0].args == ['x', 'y']
    assert result[0].body == [1]


def test_parse_def_with_multiple_body():
    result = parse_def("def f() = 1, 2")
    assert result[0].id == 1
    assert result[0].name == 'f'
    assert result[0].args == []
    assert result[0].body == [1, 2]


def test_parse_def_with_whitespace():
    result = parse_def("def f() = 1\n    ")
    assert result[0].id == 1
    assert result[0].name == 'f'
    assert result[0].args == []
    assert result[0].body == [1]


def test_parse_def_with_error():
    try:
        parse_def("def f() = 1, 2, 3")
        assert False, "Should have raised ParseError"
    except ParseError:
        pass
    else:
        assert False, "Should have raised ParseError"


def test_parse_def_with_nested_parens():
    result = parse_def("def f(x, y) = 1, 2")
    assert result[0].id == 1
    assert result[0].name == 'f'
    assert result[0].args == ['x', 'y']
    assert result[0].body == [1, 2]


def test_parse_def_with_empty_body():
    result = parse_def("def f() = ")
    assert result[0].id == 1
    assert result[0].name == 'f'
    assert result[0].args == []
    assert result[0].body == []


def test_parse_def_with_return_type():
    result = parse_def("def f() = 1")
    assert result[0].id == 1
    assert result[0].name == 'f'
    assert result[0].args == []
    assert result[0].body == [1]


from knot.parser import ParseError

def test_parse_def_simple():
    result = parse_def("def f() = 1", 0)
    assert result[0].id == 1
    assert result[0].name == 'f'
    assert result[0].args == []
    assert result[0].body == [1]


def test_parse_def_with_args():
    result = parse_def("def f(x, y) = 1", 0)
    assert result[0].id == 1
    assert result[0].name == 'f'
    assert result[0].args == ['x', 'y']
    assert result[0].body == [1]


def test_parse_def_with_multiple_body():
    result = parse_def("def f() = 1, 2", 0)
    assert result[0].id == 1
    assert result[0].name == 'f'
    assert result[0].args == []
    assert result[0].body == [1, 2]


def test_parse_def_with_whitespace():
    result = parse_def("def f() = 1\n    ", 0)
    assert result[0].id == 1
    assert result[0].name == 'f'
    assert result[0].args == []
    assert result[0].body == [1]


def test_parse_def_with_args():
    result = parse_def("def f(x, y) = 1")
    assert result[0].name == 'f'
    assert result[0].args == ('x', 'y')
    assert result[0].body == (1,)
0].body == (1,)
