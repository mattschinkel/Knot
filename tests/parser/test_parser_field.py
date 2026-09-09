def test_parse_field_access_valid():
    from knot.parser import parse_field_access

    result = parse_field_access("x", 0)
    assert result[0].id == 0
    assert result[0].path == []
    assert result[0].label is None
    assert result[1] == 1

    result = parse_field_access("x[1]", 0)
    assert result[0].id == 0
    assert result[0].path == []
    assert result[0].label is None
    assert result[1] == 2

    result = parse_field_access("x[1][2]", 0)
    assert result[0].id == 0
    assert result[0].path == [1, 2]
    assert result[0].label is None
    assert result[1] == 3


def test_parse_field_access_missing_bracket():
    from knot.parser import parse_field_access

    try:
        parse_field_access("x", 0)
        assert False, "Should raise ParseError"
    except ParseError:
        pass

    try:
        parse_field_access("x[", 0)
        assert False, "Should raise ParseError"
    except ParseError:
        pass

    try:
        parse_field_access("x[", 1)
        assert False, "Should raise ParseError"
    except ParseError:
        pass

    try:
        parse_field_access("x[", 2)
        assert False, "Should raise ParseError"
    except ParseError:
        pass


def test_parse_field_access_invalid_identifier():
    from knot.parser import parse_field_access

    try:
        parse_field_access("x[1]", 0)
        assert False, "Should raise ParseError"
    except ParseError:
        pass

    try:
        parse_field_access("x[1]", 1)
        assert False, "Should raise ParseError"
    except ParseError:
        pass

    try:
        parse_field_access("x[1]", 2)
        assert False, "Should raise ParseError"
    except ParseError:
        pass


def test_parse_field_access_empty_string():
    from knot.parser import parse_field_access

    try:
        parse_field_access("", 0)
        assert False, "Should raise ParseError"
    except ParseError:
        pass

    try:
        parse_field_access("")
        assert False, "Should raise ParseError"
    except ParseError:
        pass


def test_parse_field_access_valid():
    from knot.parser import parse_field_access

    result = parse_field_access("Ident", 0)
    assert result[0].id == 1
    assert result[1] == 0


def test_parse_field_access_missing_bracket():
    from knot.parser import parse_field_access

    try:
        parse_field_access("Ident", 0)
        assert False, "Should raise ParseError"
    except ParseError:
        pass
    else:
        assert False, "Should raise ParseError"


def test_parse_field_access_invalid_identifier():
    from knot.parser import parse_field_access

    try:
        parse_field_access("Iden", 0)
        assert False, "Should raise ParseError"
    except ParseError:
        pass
    else:
        assert False, "Should raise ParseError"


def test_parse_field_access_empty():
    from knot.parser import parse_field_access

    try:
        parse_field_access("", 0)
        assert False, "Should raise ParseError"
    except ParseError:
        pass
    else:
        assert False, "Should raise ParseError"


def test_parse_field_access_with_whitespace():
    from knot.parser import parse_field_access

    result = parse_field_access("Ident [ ", 0)
    assert result[0].id == 1
    assert result[1] == 2


def test_parse_field_access_with_content():
    from knot.parser import parse_field_access

    result = parse_field_access("Ident [ 123 ]", 0)
    assert result[0].id == 1
    assert result[1] == 10


def test_parse_field_access_valid():
    result = parse_field_access("x", 0)
    assert result[0].id == 0
    assert result[1] == 1

def test_parse_field_access_with_brackets():
    result = parse_field_access("x[1]", 0)
    assert result[0].id == 0
    assert result[1] == 2

def test_parse_field_access_missing_bracket():
    result = parse_field_access("x", 0)
    assert result[0].id == 0
    assert result[1] == 1

def test_parse_field_access_invalid_identifier():
    try:
        parse_field_access("\n", 0)
        assert False
    except ParseError:
        pass

def test_parse_field_access_unexpected_end():
    try:
        parse_field_access("x[", 0)
        assert False
    except ParseError:
        pass


def test_parse_field_access_valid():
    from knot.parser import parse_field_access

    result = parse_field_access("x", 0)
    assert result[0].id == 0
    assert result[0].path == []
    assert result[0].label is None
    assert result[1] == 1

    result = parse_field_access("x[1]", 0)
    assert result[0].id == 0
    assert result[0].path == []
    assert result[0].label is None
    assert result[1] == 2

    result = parse_field_access("x[1][2]", 0)
    assert result[0].id == 0
    assert result[0].path == [1, 2]
    assert result[0].label is None
    assert result[1] == 3


def test_parse_field_access_missing_bracket():
    from knot.parser import parse_field_access

    try:
        parse_field_access("x", 0)
        assert False, "Should raise ParseError"
    except ParseError:
        pass

    try:
        parse_field_access("x[", 0)
        assert False, "Should raise ParseError"
    except ParseError:
        pass

    try:
        parse_field_access("x[", 1)
        assert False, "Should raise ParseError"
    except ParseError:
        pass


def test_parse_field_access_with_content():
    from knot.parser import parse_field_access

    result = parse_field_access("Ident [ 123 ]", 0)
    assert result[0].id == 1
    assert result[1] == 10


def test_parse_field_access_invalid_identifier():
    from knot.parser import parse_field_access

    try:
        parse_field_access("\n", 0)
        assert False
    except ParseError:
        pass


def test_parse_field_access_unexpected_end():
    from knot.parser import parse_field_access

    try:
        parse_field_access("x[", 0)
        assert False
    except ParseError:
        pass


def test_parse_field_access_valid():
    from knot.parser import parse_field_access

    result = parse_field_access("x", 0)
    assert result[0].id == 0
    assert result[0].path == []
    assert result[0].label is None
    assert result[1] == 1

    result = parse_field_access("x[1]", 0)
    assert result[0].id == 0
    assert result[0].path == []
    assert result[0].label is None
    assert result[1] == 2

    result = parse_field_access("x[1][2]", 0)
    assert result[0].id == 0
    assert result[0].path == [1, 2]
    assert result[0].label is None
    assert result[1] == 3


def test_parse_field_access_missing_bracket():
    from knot.parser import parse_field_access

    try:
        parse_field_access("x", 0)
        assert False, "Should raise ParseError"
    except ParseError:
        pass

    try:
        parse_field_access("x[", 0)
        assert False, "Should raise ParseError"
    except ParseError:
        pass

    try:
        parse_field_access("x[", 1)
        assert False, "Should raise ParseError"
    except ParseError:
        pass


def test_parse_field_access_with_content():
    from knot.parser import parse_field_access

    result = parse_field_access("Ident [ 123 ]", 0)
    assert result[0].id == 1
    assert result[1] == 10


def test_parse_field_access_invalid_identifier():
    from knot.parser import parse_field_access

    try:
        parse_field_access("\n", 0)
        assert False
    except ParseError:
        pass


def test_parse_field_access_unexpected_end():
    from knot.parser import parse_field_access

    try:
        parse_field_access("x[", 0)
        assert False
    except ParseError:
        pass


def test_parse_field_access_valid():
    from knot.parser import parse_field_access

    result = parse_field_access("x", 0)
    assert result[0].id == 0
    assert result[0].path == []
    assert result[0].label is None
    assert result[1] == 1

    result = parse_field_access("x[1]", 0)
    assert result[0].id == 0
    assert result[0].path == []
    assert result[0].label is None
    assert result[1] == 2

    result = parse_field_access("x[1][2]", 0)
    assert result[0].id == 0
    assert result[0].path == [1, 2]
    assert result[0].label is None
    assert result[1] == 3


def test_parse_field_access_missing_bracket():
    from knot.parser import parse_field_access

    try:
        parse_field_access("x", 0)
        assert False, "Should raise ParseError"
    except ParseError:
        pass

    try:
        parse_field_access("x[", 0)
        assert False, "Should raise ParseError"
    except ParseError:
        pass

    try:
        parse_field_access("x[", 1)
        assert False, "Should raise ParseError"
    except ParseError:
        pass


def test_parse_field_access_with_content():
    from knot.parser import parse_field_access

    result = parse_field_access("Ident [ 123 ]", 0)
    assert result[0].id == 1
    assert result[1] == 10


def test_parse_field_access_invalid_identifier():
    from knot.parser import parse_field_access

    try:
        parse_field_access("\n", 0)
        assert False
    except ParseError:
        pass


def test_parse_field_access_unexpected_end():
    from knot.parser import parse_field_access

    try:
        parse_field_access("x[", 0)
        assert False
    except ParseError:
        pass
