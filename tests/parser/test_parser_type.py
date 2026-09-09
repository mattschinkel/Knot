from knot.parser import parse_typed_lit
def test_parse_typed_lit_int():
    result = parse_typed_lit("IntLit 42", 0)
    assert result[0].__class__.__name__ == "IntLit"
    assert result[0].value == 42
    assert result[1] == 2

def test_parse_typed_lit_bool_true():
    result = parse_typed_lit("BoolLit True", 0)
    assert result[0].__class__.__name__ == "BoolLit"
    assert result[0].value is True
    assert result[1] == 7

def test_parse_typed_lit_bool_false():
    result = parse_typed_lit("BoolLit False", 0)
    assert result[0].__class__.__name__ == "BoolLit"
    assert result[0].value is False
    assert result[1] == 7


def test_parse_typed_lit_int_whitespace():
    result = parse_typed_lit("IntLit 42", 0)
    assert result[0].__class__.__name__ == "IntLit"
    assert result[0].value == 42
    assert result[1] == 2

def test_parse_typed_lit_bool_true_whitespace():
    result = parse_typed_lit("BoolLit True", 0)
    assert result[0].__class__.__name__ == "BoolLit"
    assert result[0].value is True
    assert result[1] == 7

def test_parse_typed_lit_bool_false_whitespace():
    result = parse_typed_lit("BoolLit False", 0)
    assert result[0].__class__.__name__ == "BoolLit"
    assert result[0].value is False
    assert result[1] == 7


def test_parse_typed_lit_int_whitespace():
    result = parse_typed_lit("IntLit 42  ", 0)
    assert result[0].__class__.__name__ == "IntLit"
    assert result[0].value == 42
    assert result[1] == 2

def test_parse_typed_lit_bool_true_whitespace():
    result = parse_typed_lit("BoolLit True  ", 0)
    assert result[0].__class__.__name__ == "BoolLit"
    assert result[0].value is True
    assert result[1] == 7

def test_parse_typed_lit_bool_false_whitespace():
    result = parse_typed_lit("BoolLit False  ", 0)
    assert result[0].__class__.__name__ == "BoolLit"
    assert result[0].value is False
    assert result[1] == 7
