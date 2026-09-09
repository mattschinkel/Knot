from knot.grammar.gbnf import Program
def test_program_id():
    p = Program(rules=["a -> b"])
    assert p.id == 1


def test_program_path():
    p = Program(rules=["a -> b"])
    assert p.path == [1]


def test_program_label():
    p = Program(rules=["a -> b"])
    assert p.label is None


def test_program_children():
    p = Program(rules=["a -> b"])
    assert p.children == []
