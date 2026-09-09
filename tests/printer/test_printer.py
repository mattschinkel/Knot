from knot.addressing import reset_ids
from knot.parser import parse_expr, parse_def, parse_field_access, parse_hole
from knot.printer import print_ast


def setup_function():
    reset_ids()


def test_print_ast_lit():
    assert print_ast(parse_expr("42")) == "42"


def test_print_ast_bool_nil():
    assert print_ast(parse_expr("true")) == "true"
    assert print_ast(parse_expr("nil")) == "nil"


def test_print_ast_infix_add():
    out = print_ast(parse_expr("ADD[1, 2]"))
    assert out == "1 + 2"
    assert "[" not in out
    assert "]" not in out


def test_print_ast_mul_idents():
    out = print_ast(parse_expr("MUL[x, x]"))
    assert out == "x * x"


def test_print_ast_fn_shorthand():
    out = print_ast(parse_expr("MAP[xs, f]"))
    assert out == "MAP(xs, f)"
    assert "[" not in out


def test_print_ast_field_sugar():
    out = print_ast(parse_field_access("user.name"))
    assert out == "user.name"


def test_print_ast_get_as_field():
    out = print_ast(parse_expr("GET[user, name]"))
    assert out == "user.name"


def test_print_ast_hole():
    assert print_ast(parse_hole("?")) == "?"
    assert print_ast(parse_hole("?:i32")) == "?:i32"


def test_print_ast_def_fn():
    out = print_ast(parse_def("square = FN[x:i32] MUL[x, x]"))
    assert out.startswith("fn square(x: i32)")
    assert "x * x" in out
    assert "{" in out and "}" in out
    assert "[" not in out


def test_print_ast_program_list():
    from knot.parser import parse_program
    out = print_ast(parse_program("ADD[1, 2]\nMUL[3, 4]"))
    assert "1 + 2" in out
    assert "3 * 4" in out
