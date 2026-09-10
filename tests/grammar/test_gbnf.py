from knot.grammar.gbnf import (
    Program,
    Def,
    Expr,
    FieldAccess,
    Function,
    Get,
    Hole,
    Op,
    RULES,
    grammar_text,
    has_numeric_node_ids,
    uses_paren_shorthand,
)


def test_program_rule_defined():
    assert "program" in Program.lower()
    assert "def" in Program.lower()


def test_rules_cover_spec_names():
    for name in ("Program", "Def", "Expr", "Lit", "Ident", "FieldAccess",
                 "Get", "Set", "Op", "Hole", "Function", "Unit"):
        assert name in RULES
        assert "::=" in RULES[name]


def test_grammar_text_nonempty():
    text = grammar_text()
    assert "program ::=" in text
    assert "GET[" in text
    assert len(text) > 200


def test_no_numeric_node_ids():
    assert has_numeric_node_ids() is False


def test_no_paren_shorthand():
    assert uses_paren_shorthand() is False
    text = grammar_text()
    assert "FN[" in text
    assert '"FN" "("' not in text


def test_bracket_get_set():
    assert "GET[" in Get
    assert "[" in FieldAccess or "." in FieldAccess


def test_hole_forms():
    assert "?" in Hole


def test_grammar_has_def_and_err():
    text = grammar_text()
    assert 'DEF[' in text
    assert "FN[" in text
    assert "ERR[" in text or "ERROR[" in text
    assert "type ::= " in text or '"@"' in text
