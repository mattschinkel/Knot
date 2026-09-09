"""Canonical bracket-notation parser for Knot (phase1_spec Γö¼┬║4).

Input form: OP[arg1, arg2, ...]  (the only canonical form; F(...) is not).
Also parses bare literals, identifiers, UNIT, and holes (? / ?:Type).
"""
from __future__ import annotations

import re

from knot.addressing import generate_id
from knot.ast import HoleExpr, IdentExpr, LitExpr, OpExpr, UnitExpr, FieldAccess, TypedLit, DefNode, FnExpr

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
        j += 1
        j2 = _skip_ws(s, j)
        if j2 < len(s) and s[j2] == ":":
            j2 += 1
            m2 = _IDENT.match(s, j2)
            if not m2:
                raise ParseError("expected type name after ':'")
            return TypedLit(node.value, m2.group(0), id=generate_id()), m2.end()
        return node, j

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
        # typed lit sugar: 2:i32
        i2 = _skip_ws(s, i)
        if i2 < len(s) and s[i2] == ":":
            i2 += 1
            m2 = _IDENT.match(s, i2)
            if not m2:
                raise ParseError("expected type name after ':'")
            return TypedLit(val, m2.group(0), id=generate_id()), m2.end()
        return LitExpr(val), i
    if tok in ("true", "false"):
        return LitExpr(tok == "true"), i
    if tok == "nil":
        return LitExpr(None), i
    # string already handled above; typed string would be 'x':Type after quote parse
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


def parse_typed_lit(text: str) -> TypedLit:
    """Parse a typed literal in canonical form: `2:i32`, `'hi':str`, `10:meters`."""
    if text is None or not str(text).strip():
        raise ParseError("empty typed lit")
    node = parse_expr(str(text).strip())
    if not isinstance(node, TypedLit):
        raise ParseError("not a typed literal (expected value:Type)")
    return node

def parse_hole(text: str) -> HoleExpr:
    """Parse a hole: `?` or `?:Type`. Returns a HoleExpr."""
    if text is None or not str(text).strip():
        raise ParseError("empty hole")
    node = parse_expr(str(text).strip())
    if not isinstance(node, HoleExpr):
        raise ParseError("not a hole expression")
    return node


def _parse_param(s: str, i: int):
    """Parse one FN param: name or name:Type. Returns ((name, type|None), new_i)."""
    i = _skip_ws(s, i)
    m = _IDENT.match(s, i)
    if not m:
        raise ParseError("expected param name")
    name = m.group(0)
    i = m.end()
    i = _skip_ws(s, i)
    typ = None
    if i < len(s) and s[i] == ":":
        i += 1
        m2 = _IDENT.match(s, i)
        if not m2:
            raise ParseError("expected type after ':' in param")
        typ = m2.group(0)
        i = m2.end()
    return (name, typ), i


def parse_fn(text: str) -> FnExpr:
    """Parse FN[params...] body  e.g. FN[x:i32] MUL[x, x]."""
    if text is None or not str(text).strip():
        raise ParseError("empty fn")
    s = str(text).strip()
    i = 0
    i = _skip_ws(s, i)
    if not s[i:].upper().startswith("FN"):
        raise ParseError("expected FN")
    i += 2
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "[":
        raise ParseError("FN requires [params]")
    i += 1
    params = []
    i = _skip_ws(s, i)
    if i < len(s) and s[i] == "]":
        i += 1
    else:
        while True:
            param, i = _parse_param(s, i)
            params.append(param)
            i = _skip_ws(s, i)
            if i >= len(s):
                raise ParseError("unclosed FN params")
            if s[i] == "]":
                i += 1
                break
            if s[i] in ",;":
                i += 1
                continue
            raise ParseError("expected ',' or ']' in FN params")
    body, i = _parse_atom(s, i)
    i = _skip_ws(s, i)
    if i < len(s):
        raise ParseError(f"trailing input: {s[i:]!r}")
    return FnExpr(params=params, body=body, id=generate_id())


def parse_def(text: str) -> DefNode:
    """Parse a definition: `name = expr` or `def name = expr`."""
    if text is None or not str(text).strip():
        raise ParseError("empty def")
    s = str(text).strip()
    i = 0
    i = _skip_ws(s, i)
    if s[i:].lower().startswith("def") and (len(s) == i + 3 or not s[i + 3].isalnum()):
        i += 3
        i = _skip_ws(s, i)
    m = _IDENT.match(s, i)
    if not m:
        raise ParseError("expected name in def")
    name = m.group(0)
    i = m.end()
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "=":
        raise ParseError("expected '=' in def")
    i += 1
    i = _skip_ws(s, i)
    # Body may be an FN[...] expr — use parse_fn when it starts with FN
    if s[i:].upper().startswith("FN"):
        body = parse_fn(s[i:])
        return DefNode(name=name, body=body, id=generate_id())
    body, i = _parse_atom(s, i)
    i = _skip_ws(s, i)
    if i < len(s):
        raise ParseError(f"trailing input: {s[i:]!r}")
    return DefNode(name=name, body=body, id=generate_id())
