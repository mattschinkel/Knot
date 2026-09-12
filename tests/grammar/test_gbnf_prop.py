"""Property-style tests for GBNF grammar constraints."""
from golem.grammar.gbnf import RULES, grammar_text, has_numeric_node_ids, uses_paren_shorthand


def test_valid_syntax():
    text = grammar_text()
    assert "program ::=" in text
    assert "expr ::=" in text
    for name, rule in RULES.items():
        assert "::=" in rule, name
        assert rule.strip()


def test_no_numeric_ids():
    assert has_numeric_node_ids() is False
    text = grammar_text()
    assert "node-id" not in text.lower()
    assert "node_id" not in text.lower()


def test_bracket_only_in_ops():
    text = grammar_text()
    assert "GET[" in text
    assert "FN[" in text
    assert uses_paren_shorthand() is False
