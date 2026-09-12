from golem.ast import LitExpr
def test_litexpr_id():
    expr = LitExpr(value=42)
    assert expr.id == 42


def test_litexpr_path():
    expr = LitExpr(value=42)
    assert expr.path == []


def test_litexpr_label():
    expr = LitExpr(value=42)
    assert expr.label is None


def test_litexpr_children_tuple():
    expr = LitExpr(value=42)
    assert isinstance(expr.children, tuple)


def test_litexpr_children_single():
    expr = LitExpr(value=42)
    assert len(expr.children) == 1


def test_litexpr_children_value():
    expr = LitExpr(value=42)
    assert expr.children[0] == 42


def test_litexpr_repr():
    expr = LitExpr(value=42)
    assert repr(expr) == 'LitExpr(42)'


def test_litexpr_eq():
    expr1 = LitExpr(value=42)
    expr2 = LitExpr(value=42)
    assert expr1 == expr2


def test_litexpr_hash():
    expr1 = LitExpr(value=42)
    expr2 = LitExpr(value=42)
    assert hash(expr1) == hash(expr2)


def test_litexpr_lt():
    expr1 = LitExpr(value=42)
    expr2 = LitExpr(value=43)
    assert expr1 < expr2


def test_litexpr_id_negative():
    expr = LitExpr(value=-42)
    assert expr.id == -42

def test_litexpr_path_negative():
    expr = LitExpr(value=-42)
    assert expr.path == []

def test_litexpr_label_negative():
    expr = LitExpr(value=-42)
    assert expr.label is None

def test_litexpr_children_tuple_negative():
    expr = LitExpr(value=-42)
    assert isinstance(expr.children, tuple)

def test_litexpr_children_single_negative():
    expr = LitExpr(value=-42)
    assert len(expr.children) == 1

def test_litexpr_children_value_negative():
    expr = LitExpr(value=-42)
    assert expr.children[0] == -42

def test_litexpr_repr_negative():
    expr = LitExpr(value=-42)
    assert repr(expr) == 'LitExpr(-42)'
