"""Canonical bracket-notation parser for Knot (phase1_spec §4).

Input form: OP[arg1, arg2, ...]  (the only canonical form; F(...) is not).
Also parses bare literals, identifiers, UNIT, and holes (? / ?:Type).
"""
from __future__ import annotations

import re

from knot.addressing import generate_id
from knot.ast import HoleExpr, IdentExpr, LitExpr, OpExpr, UnitExpr

_NUM = re.compile(r"^-?\d+(?:\.\d+)?$")
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class ParseError(ValueError):
    pass


def _skip_ws(s: str, i: int) -> int:
    while i < len(s) and s[i].isspace():
        i += 1
    return i


def _parse_atom(s: str, i: int):
    """Parse one expression starting at i. Returns (node, new_index)."""
    i = _skip_ws(s, i)
    if i >= len(s):
        raise ParseError("unexpected end of input")

    # Hole: ? or ?:Type
    if s[i] == "?":
        i += 1
        typ = None
        if i < len(s) and s[i] == ":":
            i += 1
            m = _IDENT.match(s, i)
            if not m:
                raise ParseError("expected type after ?:")
            typ = m.group(0)
            i = m.end()
        node = HoleExpr(id=generate_id(), path=[], label=typ)
        return node, i

    # String literal
    if s[i] in "'\"":
        quote = s[i]
        j = i + 1
        while j < len(s) and s[j] != quote:
            if s[j] == "\\":
                j += 2
            else:
                j += 1
        if j >= len(s):
            raise ParseError("unterminated string")
        node = LitExpr(s[i + 1:j])
        return node, j + 1

    # Number or Ident or OP[...] or UNIT
    m = re.match(r"[A-Za-z_][A-Za-z0-9_]*|-?\d+(?:\.\d+)?", s[i:])
    if not m:
        raise ParseError(f"unexpected char at {i}: {s[i]!r}")
    tok = m.group(0)
    i = i + m.end()

    i = _skip_ws(s, i)
    if i < len(s) and s[i] == "[":
        # OP[args...]
        args, i = _parse_arglist(s, i)
        return OpExpr(op=tok, children=args, id=generate_id()), i

    if tok.upper() == "UNIT":
        return UnitExpr(id=generate_id()), i
    if _NUM.match(tok):
        val: int | float = float(tok) if "." in tok else int(tok)
        return LitExpr(val), i
    if tok in ("true", "false"):
        return LitExpr(tok == "true"), i
    if tok == "nil":
        return LitExpr(None), i
    return IdentExpr(id=tok), i


def _parse_arglist(s: str, i: int):
    """Parse [arg, arg, ...] starting at '['. Returns (list, new_index)."""
    assert s[i] == "["
    i += 1
    args = []
    i = _skip_ws(s, i)
    if i < len(s) and s[i] == "]":
        return args, i + 1
    while True:
        node, i = _parse_atom(s, i)
        args.append(node)
        i = _skip_ws(s, i)
        if i >= len(s):
            raise ParseError("unclosed '['")
        if s[i] == "]":
            return args, i + 1
        if s[i] in ",;":
            i += 1
            i = _skip_ws(s, i)
            continue
        raise ParseError(f"expected ',' or ']' at {i}, got {s[i]!r}")


def parse_expr(text: str):
    """Parse a single expression in bracket notation. Returns an AST node."""
    if text is None or not str(text).strip():
        raise ParseError("empty expression")
    node, i = _parse_atom(str(text), 0)
    i = _skip_ws(str(text), i)
    if i != len(str(text).strip()) and i < len(text):
        # allow trailing whitespace only
        rest = text[i:].strip()
        if rest:
            raise ParseError(f"trailing input: {rest!r}")
    return node


def parse_program(text: str) -> list:
    """Parse a program: zero or more expressions (newline / semicolon separated).

    Returns a list of AST nodes. Empty input -> [].
    """
    if text is None or not str(text).strip():
        return []
    s = str(text)
    nodes = []
    i = 0
    while True:
        i = _skip_ws(s, i)
        if i >= len(s):
            break
        if s[i] in ";\n":
            i += 1
            continue
        node, i = _parse_atom(s, i)
        nodes.append(node)
        i = _skip_ws(s, i)
        if i < len(s) and s[i] in ";\n":
            i += 1
    return nodes

from knot.parser import parse_field_access
from knot.parser import ParseError

# Tests

def test_parse_field_access_valid():
    result = parse_field_access("x", 0)
    assert result[0].id == 0
    assert result[1] == 1

def test_parse_field_access_with_brackets():
    result = parse_field_access("x[1]", 0)
    assert result[0].id == 0
    assert result[1] == 2

def test_parse_field_access_missing_bracket():
    try:
        parse_field_access("x", 0)
        assert False
    except ParseError:
        pass

def test_parse_field_access_invalid_identifier():
    try:
        parse_field_access("\n", 0)
        assert False
    except ParseError:
        pass

def test_parse_field_access_empty_string():
    try:
        parse_field_access("", 0)
        assert False, "Should raise ParseError"
    except ParseError:
        pass

def test_parse_field_access_empty():
    try:
        parse_field_access("", 0)
        assert False, "Should raise ParseError"
    except ParseError:
        pass

def test_parse_field_access_with_whitespace():
    try:
        parse_field_access("Ident [ ", 0)
        assert False
    except ParseError:
        pass

def test_parse_field_access_with_content():
    try:
        parse_field_access("Ident [ 123 ]", 0)
        assert False
    except ParseError:
        pass

def test_parse_field_access_unexpected_end():
    try:
        parse_field_access("x[", 0)
        assert False
    except ParseError:
        pass

def parse_field_access(s: str, i: int) -> tuple[IdentExpr, int]:
    """Parse field access: Ident[...] -> IdentExpr"""
    i = _skip_ws(s, i)
    if i >= len(s):
        raise ParseError("unexpected end of input")

    # Parse identifier
    m = _IDENT.match(s, i)
    if not m:
        raise ParseError(f"expected identifier at position {i}")
    ident = IdentExpr(m.group())
    i = m.end()

    # Skip whitespace
    i = _skip_ws(s, i)

    # Expect [
    if s[i] != '[':
        raise ParseError(f"expected '[' at position {i}")
    i += 1

    # Parse content (anything between brackets)
    content = []
    while i < len(s) and s[i] != ']':
        content.append(parse_field_access_content(s, i))
        i = content[-1][1]

    # Expect ]
    if i >= len(s) or s[i] != ']':
        raise ParseError(f"expected ']' at position {i}")
    i += 1

    # Reconstruct: Ident[...] -> IdentExpr
    return ident, i


def parse_field_access_content(s: str, i: int) -> tuple[str, int]:
    """Parse content between brackets: e.g., "123" or "x" or "x[...]"""
    i = _skip_ws(s, i)
    if i >= len(s):
        raise ParseError("unexpected end of input")

    # Parse atom
    atom = _parse_atom(s, i)
    return atom[0], atom[1]
