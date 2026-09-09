"""Canonical bracket-notation parser for Knot (phase1_spec §4).

Input form: OP[arg1, arg2, ...]  (the only canonical form; F(...) is not).
Also parses bare literals, identifiers, UNIT, and holes (? / ?:Type).
"""
from __future__ import annotations

import re

from knot.addressing import generate_id
from knot.ast import HoleExpr, IdentExpr, LitExpr, OpExpr, UnitExpr, FieldAccess

_NUM = re.compile(r"-?\d+(?:\.\d+)?")
_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


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
    # identifier, possibly with .field sugar (user.name -> FieldAccess)
    node: object = IdentExpr(id=tok)
    while True:
        i2 = _skip_ws(s, i)
        if i2 < len(s) and s[i2] == ".":
            i2 += 1
            m2 = _IDENT.match(s, i2)
            if not m2:
                raise ParseError("expected field name after '.'")
            field = m2.group(0)
            i2 = m2.end()
            node = FieldAccess(id=node, field_name=field, path=[])
            i = i2
            continue
        break
    return node, i


def parse_field_access(text: str):
    """Parse field-access sugar: `obj.field` (-> FieldAccess).

    Also accepts already-desugared `GET[obj, field]` via parse_expr.
    """
    if text is None or not str(text).strip():
        raise ParseError("empty field access")
    s = str(text).strip()
    if "." not in s:
        raise ParseError("field access requires obj.field")
    node, i = _parse_atom(s, 0)
    i = _skip_ws(s, i)
    if i < len(s):
        raise ParseError(f"trailing input: {s[i:]!r}")
    if not isinstance(node, FieldAccess):
        raise ParseError("not a field access expression")
    return node


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

def parse_typed_lit(s: str, i: int) -> tuple[LitExpr, int]:
    """Parse a typed literal expression: IntLit n, BoolLit b, or StrLit s.

    Args:
        s: The input string
        i: The starting index

    Returns:
        A tuple of (LitExpr, new_index) where new_index is the position after parsing.

    Raises:
        ParseError: If the literal is malformed.
    """
    # Skip whitespace
    i = _skip_ws(s, i)
    if i >= len(s):
        raise ParseError("unexpected end of input")

    # Parse the type prefix
    if s[i:i+8] == "IntLit ":
        i += 8
    elif s[i:i+8] == "BoolLit ":
        i += 8
    elif s[i:i+8] == "StrLit ":
        i += 8
    else:
        raise ParseError(f"expected IntLit, BoolLit, or StrLit, got {repr(s[i:i+8])}")

    # Parse the integer value
    m = _NUM.match(s, i)
    if not m:
        raise ParseError(f"expected integer literal, got {repr(s[i])}")

    # Parse the integer value
    result = IntLit(int(m.group()))
    i = m.end()

    return (result, i)
