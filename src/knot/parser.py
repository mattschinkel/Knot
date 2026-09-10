"""Canonical bracket-notation parser for Knot (phase1_spec Γö¼┬║4).

Input form: OP[arg1, arg2, ...]  (the only canonical form; F(...) is not).
Also parses bare literals, identifiers, UNIT, and holes (? / ?:Type).
"""
from __future__ import annotations

import re

from knot.addressing import generate_id
from knot.ast import HoleExpr, IdentExpr, LitExpr, OpExpr, UnitExpr, TypedLit, DefNode, FnExpr

_NUM = re.compile(r"-?\d+(?:\.\d+)?")
_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class ParseError(ValueError):
    pass


def _skip_ws(s: str, i: int) -> int:
    while i < len(s) and s[i].isspace():
        i += 1
    return i


def _parse_type(s: str, i: int) -> tuple[str, int]:
    """Parse a type name: ident or ident@ident (D-FB3). Returns (type_str, new_i)."""
    i = _skip_ws(s, i)
    m = _IDENT.match(s, i)
    if not m:
        raise ParseError("expected type name")
    name = m.group(0)
    i = m.end()
    i2 = _skip_ws(s, i)
    if i2 < len(s) and s[i2] == "@":
        i2 += 1
        m2 = _IDENT.match(s, i2)
        if not m2:
            raise ParseError("expected dimension after '@'")
        name = name + "@" + m2.group(0)
        i = m2.end()
    return name, i


def _parse_atom(s: str, i: int):
    """Parse one expression starting at i. Returns (node, new_index)."""
    i = _skip_ws(s, i)
    if i >= len(s):
        raise ParseError("unexpected end of input")

    # Hole: ? or ?:Type (Type may be f64@meters)
    if s[i] == "?":
        i += 1
        typ = None
        if i < len(s) and s[i] == ":":
            i += 1
            typ, i = _parse_type(s, i)
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
            typ, j2 = _parse_type(s, j2)
            return TypedLit(node.value, typ, id=generate_id()), j2
        return node, j

    # Number or Ident or OP[...] or UNIT
    m = re.match(r"[A-Za-z_][A-Za-z0-9_]*|-?\d+(?:\.\d+)?", s[i:])
    if not m:
        raise ParseError(f"unexpected char at {i}: {s[i]!r}")
    tok = m.group(0)
    i = i + m.end()

    i = _skip_ws(s, i)
    if i < len(s) and s[i] == "[":
        # Canonical FN[[params], body] and DEF[name, expr]
        if tok.upper() == "FN":
            return _parse_fn_brackets(s, i)
        if tok.upper() == "DEF":
            return _parse_def_brackets(s, i)
        args, i = _parse_arglist(s, i)
        return OpExpr(op=tok, children=args, id=generate_id()), i

    if tok.upper() == "UNIT":
        return UnitExpr(id=generate_id()), i
    if _NUM.match(tok):
        val: int | float = float(tok) if "." in tok else int(tok)
        i2 = _skip_ws(s, i)
        if i2 < len(s) and s[i2] == ":":
            i2 += 1
            typ, i2 = _parse_type(s, i2)
            return TypedLit(val, typ, id=generate_id()), i2
        return LitExpr(val), i
    if tok in ("true", "false"):
        return LitExpr(tok == "true"), i
    if tok == "nil":
        return LitExpr(None), i
    # identifier — no `.` sugar in canonical (D-FB1); use GET[...]
    i2 = _skip_ws(s, i)
    if i2 < len(s) and s[i2] == ".":
        raise ParseError(
            "field-access sugar 'obj.field' is pretty-only; "
            "canonical form is GET[obj, field]"
        )
    return IdentExpr(id=tok), i


def parse_field_access(text: str):
    """Pretty-view helper only. Canonical AIR must use GET[obj, field] (D-FB1)."""
    raise ParseError(
        "field-access sugar is pretty-only; use GET[obj, field] in canonical AIR"
    )


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
        typ, i = _parse_type(s, i)
    return (name, typ), i


def _parse_param_list(s: str, i: int) -> tuple[list, int]:
    """Parse [param, ...] starting at '['."""
    if i >= len(s) or s[i] != "[":
        raise ParseError("expected '[' to start param list")
    i += 1
    params: list = []
    i = _skip_ws(s, i)
    if i < len(s) and s[i] == "]":
        return params, i + 1
    while True:
        param, i = _parse_param(s, i)
        params.append(param)
        i = _skip_ws(s, i)
        if i >= len(s):
            raise ParseError("unclosed param list")
        if s[i] == "]":
            return params, i + 1
        if s[i] in ",;":
            i += 1
            continue
        raise ParseError("expected ',' or ']' in param list")


def _parse_fn_brackets(s: str, i: int) -> tuple[FnExpr, int]:
    """Parse FN[[params], body] starting at the '[' after FN (D-FB1)."""
    if i >= len(s) or s[i] != "[":
        raise ParseError("FN requires [")
    i += 1
    i = _skip_ws(s, i)
    params, i = _parse_param_list(s, i)
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != ",":
        raise ParseError("FN[[params], body] requires comma before body")
    i += 1
    body, i = _parse_atom(s, i)
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed FN[...]")
    return FnExpr(params=params, body=body, id=generate_id()), i + 1


def _parse_def_brackets(s: str, i: int) -> tuple[DefNode, int]:
    """Parse DEF[name, expr] starting at the '[' after DEF (D-FB2)."""
    if i >= len(s) or s[i] != "[":
        raise ParseError("DEF requires [")
    i += 1
    i = _skip_ws(s, i)
    m = _IDENT.match(s, i)
    if not m:
        raise ParseError("expected name in DEF")
    name = m.group(0)
    i = m.end()
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != ",":
        raise ParseError("DEF[name, expr] requires comma")
    i += 1
    body, i = _parse_atom(s, i)
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed DEF[...]")
    return DefNode(name=name, body=body, id=generate_id()), i + 1


def parse_fn(text: str) -> FnExpr:
    """Parse canonical FN[[params], body] (D-FB1)."""
    if text is None or not str(text).strip():
        raise ParseError("empty fn")
    s = str(text).strip()
    i = _skip_ws(s, 0)
    if not s[i:].upper().startswith("FN"):
        raise ParseError("expected FN")
    i += 2
    i = _skip_ws(s, i)
    node, i = _parse_fn_brackets(s, i)
    i = _skip_ws(s, i)
    if i < len(s):
        raise ParseError(f"trailing input: {s[i:]!r}")
    return node


def parse_def(text: str) -> DefNode:
    """Parse canonical DEF[name, expr] (D-FB2)."""
    if text is None or not str(text).strip():
        raise ParseError("empty def")
    s = str(text).strip()
    i = _skip_ws(s, 0)
    if not s[i:].upper().startswith("DEF"):
        raise ParseError("expected DEF[name, expr] (legacy name=expr removed from canonical)")
    i += 3
    i = _skip_ws(s, i)
    node, i = _parse_def_brackets(s, i)
    i = _skip_ws(s, i)
    if i < len(s):
        raise ParseError(f"trailing input: {s[i:]!r}")
    return node
