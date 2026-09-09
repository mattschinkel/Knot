from knot.parser import parse_program
def test_parse_program_empty():
    assert parse_program("") is None

def test_parse_program_simple():
    result = parse_program("[1, 2, 3]")
    assert result is not None
    assert len(result) == 3
    assert result[0].id == 1
    assert result[1].id == 2
    assert result[2].id == 3

def test_parse_program_nested():
    result = parse_program("[[1, 2], [3, 4]]")
    assert result is not None
    assert len(result) == 2
    assert result[0][0].id == 1
    assert result[0][1].id == 2
    assert result[1][0].id == 3
    assert result[1][1].id == 4

def test_parse_program_mixed():
    result = parse_program("[1, [2, 3], 4]")
    assert result is not None
    assert len(result) == 3
    assert result[0].id == 1
    assert result[1][0].id == 2
    assert result[1][1].id == 3
    assert result[2].id == 4

def test_parse_program_with_commas():
    result = parse_program("[1, 2, 3, 4]")
    assert result is not None
    assert len(result) == 4
    assert result[0].id == 1
    assert result[1].id == 2
    assert result[2].id == 3
    assert result[3].id == 4

def test_parse_program_with_semicolons():
    result = parse_program("[1; 2; 3]")
    assert result is not None
    assert len(result) == 3
    assert result[0].id == 1
    assert result[1].id == 2
    assert result[2].id == 3

def test_parse_program_with_both():
    result = parse_program("[1, 2; 3, 4]")
    assert result is not None
    assert len(result) == 4
    assert result[0].id == 1
    assert result[1].id == 2
    assert result[2].id == 3
    assert result[3].id == 4


def test_parse_program_empty():
    assert parse_program("") is None

def test_parse_program_simple():
    result = parse_program("a, b; c")
    assert result is not None
    assert len(result) == 3
    assert result[0].label == 'a'
    assert result[1].label == 'b'
    assert result[2].label == 'c'

def test_parse_program_nested():
    result = parse_program("[a, b; c], d")
    assert result is not None
    assert len(result) == 2
    assert result[0].label == 'a'
    assert result[0].children == [result[0].children[0], result[0].children[1]]
