from knot.ast import HoleExpr
def test_holeexpr_id():
    h = HoleExpr(id=1)
    assert h.id == 1


def test_holeexpr_path():
    h = HoleExpr(path=[1, 2, 3])
    assert h.path == [1, 2, 3]


def test_holeexpr_label():
    h = HoleExpr(label="test_label")
    assert h.label == "test_label"


def test_holeexpr_children():
    h = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    assert h.children == []


def test_holeexpr_repr():
    h = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    assert repr(h) == 'HoleExpr(id=1, path=[1, 2], label="label", children=[])'


def test_holeexpr_eq():
    h1 = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    h2 = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    assert h1 == h2


def test_holeexpr_hash():
    h1 = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    h2 = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    assert hash(h1) == hash(h2)


def test_holeexpr_lt():
    h1 = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    h2 = HoleExpr(id=2, path=[1, 2], label="label", children=[])  # children is a property
    assert h1 < h2


def test_holeexpr_id():
    h = HoleExpr(id=1)
    assert h.id == 1


def test_holeexpr_path():
    h = HoleExpr(id=1, path=[1, 2, 3])
    assert h.path == [1, 2, 3]


def test_holeexpr_label():
    h = HoleExpr(id=1, label="test_label")
    assert h.label == "test_label"


def test_holeexpr_children_property():
    h = HoleExpr(id=1)
    assert h.children is None


def test_holeexpr_repr():
    h = HoleExpr(id=1, path=[1, 2], label="label")
    assert repr(h) == 'HoleExpr(id=1, path=[1, 2], label="label")'


def test_holeexpr_eq():
    h1 = HoleExpr(id=1, path=[1, 2], label="label")
    h2 = HoleExpr(id=1, path=[1, 2], label="label")
    assert h1 == h2


def test_holeexpr_hash():
    h1 = HoleExpr(id=1, path=[1, 2], label="label")
    h2 = HoleExpr(id=1, path=[1, 2], label="label")
    assert hash(h1) == hash(h2)


def test_holeexpr_lt():
    h1 = HoleExpr(id=1, path=[1, 2], label="label")
    h2 = HoleExpr(id=2, path=[1, 2], label="label")
    assert h1 < h2


def test_holeexpr_id():
    expr = HoleExpr(id=1)
    assert expr.id == 1


def test_holeexpr_path():
    expr = HoleExpr(path=[1, 2, 3])
    assert expr.path == [1, 2, 3]


def test_holeexpr_label():
    expr = HoleExpr(label="test_label")
    assert expr.label == "test_label"


def test_holeexpr_children():
    expr = HoleExpr(id=1, path=[1, 2], label="test")
    assert expr.children == ()


def test_holeexpr_repr():
    expr = HoleExpr(id=1, path=[1, 2], label="test")
    assert repr(expr) == "HoleExpr(id=1, path=[1, 2], label='test')"


def test_holeexpr_eq():
    expr1 = HoleExpr(id=1, path=[1, 2], label="test")
    expr2 = HoleExpr(id=1, path=[1, 2], label="test")
    assert expr1 == expr2


def test_holeexpr_hash():
    expr = HoleExpr(id=1, path=[1, 2], label="test")
    assert hash(expr) == hash((1, [1, 2], "test"))


def test_holeexpr_lt():
    expr1 = HoleExpr(id=1, path=[1, 2], label="test")
    expr2 = HoleExpr(id=2, path=[1, 2], label="test")
    assert expr1 < expr2


def test_holeexpr_hash_collision():
    expr1 = HoleExpr(id=1, path=[1, 2], label="test")
    expr2 = HoleExpr(id=1, path=[1, 2], label="test")
    assert hash(expr1) == hash(expr2)


def test_holeexpr_id():
    expr = HoleExpr(id=1, path=[1])
    assert expr.id == 1


def test_holeexpr_path():
    expr = HoleExpr(id=1, path=[1, 2, 3])
    assert expr.path == [1, 2, 3]


def test_holeexpr_label():
    expr = HoleExpr(id=1, path=[1], label="test_label")
    assert expr.label == "test_label"


def test_holeexpr_children():
    expr = HoleExpr(id=1, path=[1])
    assert expr.children == ()


def test_holeexpr_repr():
    expr = HoleExpr(id=1, path=[1], label="test")
    assert repr(expr) == "HoleExpr(id=1, path=[1], label='test')"


def test_holeexpr_eq():
    expr1 = HoleExpr(id=1, path=[1], label="test")
    expr2 = HoleExpr(id=1, path=[1], label="test")
    assert expr1 == expr2


def test_holeexpr_hash():
    expr = HoleExpr(id=1, path=[1], label="test")
    assert hash(expr) == hash((1, (1,), "test"))


def test_holeexpr_lt():
    expr1 = HoleExpr(id=1, path=[1], label="test")
    expr2 = HoleExpr(id=2, path=[1], label="test")
    assert expr1 < expr2


def test_holeexpr_hash_collision():
    expr1 = HoleExpr(id=1, path=[1], label="test")
    expr2 = HoleExpr(id=1, path=[1], label="test")
    assert hash(expr1) == hash(expr2)


def test_holeexpr_id():
    h = HoleExpr(id=1)
    assert h.id == 1


def test_holeexpr_path():
    h = HoleExpr(path=[1, 2, 3])
    assert h.path == [1, 2, 3]


def test_holeexpr_label():
    h = HoleExpr(label="test_label")
    assert h.label == "test_label"


def test_holeexpr_children():
    h = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    assert h.children == []


def test_holeexpr_repr():
    h = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    assert repr(h) == 'HoleExpr(id=1, path=[1, 2], label="label", children=[])'


def test_holeexpr_eq():
    h1 = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    h2 = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    assert h1 == h2


def test_holeexpr_hash():
    h1 = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    h2 = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    assert hash(h1) == hash(h2)


def test_holeexpr_lt():
    h1 = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    h2 = HoleExpr(id=2, path=[1, 2], label="label", children=[])  # children is a property
    assert h1 < h2


def test_holeexpr_children_property():
    h = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    assert h.children == []


def test_holeexpr_children_property_none():
    h = HoleExpr(id=1)
    assert h.children is None


def test_holeexpr_children_property_none():
    h = HoleExpr(id=1)
    assert h.children is None


def test_holeexpr_children_property_none():
    h = HoleExpr(id=1)
    assert h.children is None


def test_holeexpr_id():
    h = HoleExpr(id=1, path=[1])
    assert h.id == 1

def test_holeexpr_path():
    h = HoleExpr(id=1, path=[1, 2, 3])
    assert h.path == [1, 2, 3]

def test_holeexpr_label():
    h = HoleExpr(id=1, path=[1], label="test_label")
    assert h.label == "test_label"

def test_holeexpr_repr():
    h = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    assert repr(h) == 'HoleExpr(id=1, path=[1, 2], label="label", children=[])'

def test_holeexpr_hash():
    h1 = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    h2 = HoleExpr(id=1, path=[1, 2], label="label", children=[])  # children is a property
    assert hash(h1) == hash(h2)

def test_holeexpr_hash_collision():
    h1 = HoleExpr(id=1, path=[1], label="test")
    h2 = HoleExpr(id=1, path=[1], label="test")
    assert hash(h1) == hash(h2)

def test_holeexpr_children_property_none():
    h = HoleExpr(id=1, path=[1])
    assert h.children is None

def test_holeexpr_children_property_set():
    h = HoleExpr(id=1, path=[1])
    h.children = []
    assert h.children == []

def test_holeexpr_children_property_get():
    h = HoleExpr(id=1, path=[1], children=[])  # children is a property
    assert h.children == []

def test_holeexpr_children_property_set_list():
    h = HoleExpr(id=1, path=[1])
    h.children = [1, 2, 3]
    assert h.children == [1, 2, 3]
