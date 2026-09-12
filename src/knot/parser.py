"""Canonical bracket-notation parser for Knot (phase1_spec Γö¼┬║4).

Input form: OP[arg1, arg2, ...]  (the only canonical form; F(...) is not).
Also parses bare literals, identifiers, UNIT, and holes (? / ?:Type).
"""
from __future__ import annotations

import re

from knot.addressing import generate_id
from knot.ast import (
    HoleExpr,
    IdentExpr,
    LitExpr,
    OpExpr,
    UnitExpr,
    TypedLit,
    DefNode,
    FnExpr,
    ErrExpr,
    InlineTest,
    InlineCase,
    PropertyDecl,
    ModuleDecl,
    ImportDecl,
    DependsDecl,
    ExportList,
    ModelDecl,
    ToolDecl,
    InvokeExpr,
    ParExpr,
    SeqExpr,
    RefExpr,
    DerefExpr,
    UnsafeExpr,
    MatchExpr,
    MatchCase,
)

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
        if tok.upper() == "ERR":
            return _parse_err_brackets(s, i)
        if tok.upper() == "TEST":
            return _parse_test_brackets(s, i)
        if tok.upper() == "PROPERTY":
            return _parse_property_brackets(s, i)
        if tok.upper() == "MODULE":
            return _parse_module_brackets(s, i)
        if tok.upper() == "IMPORT":
            return _parse_import_brackets(s, i)
        if tok.upper() == "DEPENDS":
            return _parse_depends_brackets(s, i)
        if tok.upper() == "EXPORT":
            return _parse_export_brackets(s, i)
        if tok.upper() == "MODEL":
            return _parse_model_brackets(s, i)
        if tok.upper() == "TOOL":
            return _parse_tool_brackets(s, i)
        if tok.upper() == "INVOKE":
            return _parse_invoke_brackets(s, i)
        if tok.upper() == "PAR":
            return _parse_par_brackets(s, i)
        if tok.upper() == "SEQ":
            return _parse_seq_brackets(s, i)
        if tok.upper() == "REF":
            return _parse_ref_brackets(s, i)
        if tok.upper() == "DEREF":
            return _parse_deref_brackets(s, i)
        if tok.upper() == "UNSAFE":
            return _parse_unsafe_brackets(s, i)
        if tok.upper() == "MATCH":
            return _parse_match_brackets(s, i)
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
    # identifier — may be a type atom with @dim (e.g. f64@meters in CONVERT)
    i2 = _skip_ws(s, i)
    if i2 < len(s) and s[i2] == "@":
        i2 += 1
        m2 = _IDENT.match(s, i2)
        if not m2:
            raise ParseError("expected dimension after '@'")
        tok = tok + "@" + m2.group(0)
        i = m2.end()
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


def _parse_path_list(s: str, i: int) -> tuple[list, int]:
    """Parse structural path `[seg,...]` (idents or numbers)."""
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "[":
        raise ParseError("ERR path must be [...]")
    i += 1
    segs: list = []
    i = _skip_ws(s, i)
    if i < len(s) and s[i] == "]":
        return segs, i + 1
    while True:
        i = _skip_ws(s, i)
        m = _NUM.match(s, i)
        if m:
            tok = m.group(0)
            segs.append(int(tok) if "." not in tok else float(tok))
            i = m.end()
        else:
            m = _IDENT.match(s, i)
            if not m:
                raise ParseError("expected path segment")
            segs.append(m.group(0))
            i = m.end()
        i = _skip_ws(s, i)
        if i >= len(s):
            raise ParseError("unclosed path '['")
        if s[i] == "]":
            return segs, i + 1
        if s[i] in ",;":
            i += 1
            continue
        raise ParseError(f"expected ',' or ']' in path at {i}")


def _parse_err_brackets(s: str, i: int) -> tuple[ErrExpr, int]:
    """Parse ERR[code, path, expected, actual, fix*] starting at '['."""
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "[":
        raise ParseError("expected '[' after ERR")
    i += 1
    i = _skip_ws(s, i)
    m = _IDENT.match(s, i)
    if not m:
        raise ParseError("ERR expects code ident")
    code = m.group(0)
    i = m.end()
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] not in ",;":
        raise ParseError("ERR expects ',' after code")
    i += 1
    path, i = _parse_path_list(s, i)
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] not in ",;":
        raise ParseError("ERR expects ',' after path")
    i += 1
    expected, i = _parse_type(s, i)
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] not in ",;":
        raise ParseError("ERR expects ',' after expected type")
    i += 1
    actual, i = _parse_type(s, i)
    fixes = []
    i = _skip_ws(s, i)
    while i < len(s) and s[i] in ",;":
        i += 1
        i = _skip_ws(s, i)
        if i < len(s) and s[i] == "]":
            break
        fix, i = _parse_atom(s, i)
        fixes.append(fix)
        i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed ERR[...]")
    return (
        ErrExpr(
            code=code,
            path=path,
            expected=expected,
            actual=actual,
            fixes=fixes,
            id=generate_id(),
        ),
        i + 1,
    )


def parse_err(text: str) -> ErrExpr:
    """Parse canonical ERR[code, path, expected, actual, fixes*]."""
    node = parse_expr(text)
    if not isinstance(node, ErrExpr):
        raise ParseError("expected ERR[...]")
    return node


def _parse_test_brackets(s: str, i: int) -> tuple[InlineTest, int]:
    """Parse TEST[name, CASE[in,out], ...] starting at '['."""
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "[":
        raise ParseError("expected '[' after TEST")
    i += 1
    i = _skip_ws(s, i)
    m = _IDENT.match(s, i)
    if not m:
        raise ParseError("TEST expects name")
    name = m.group(0)
    i = m.end()
    cases = []
    i = _skip_ws(s, i)
    while i < len(s) and s[i] in ",;":
        i += 1
        i = _skip_ws(s, i)
        if i < len(s) and s[i] == "]":
            break
        # CASE[in, out] or bare pair via CASE
        i2 = _skip_ws(s, i)
        if s[i2:].upper().startswith("CASE"):
            i = i2 + 4
            i = _skip_ws(s, i)
            if i >= len(s) or s[i] != "[":
                raise ParseError("expected CASE[...]")
            args, i = _parse_arglist(s, i)
            if len(args) != 2:
                raise ParseError("CASE needs in, out")
            cases.append(InlineCase(args[0], args[1]))
        else:
            raise ParseError("TEST cases must be CASE[in,out]")
        i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed TEST[...]")
    return InlineTest(name=name, cases=cases, id=generate_id()), i + 1


def _parse_property_brackets(s: str, i: int) -> tuple[PropertyDecl, int]:
    """Parse PROPERTY[name, [[x:T,...], body]] starting at '['."""
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "[":
        raise ParseError("expected '[' after PROPERTY")
    i += 1
    i = _skip_ws(s, i)
    m = _IDENT.match(s, i)
    if not m:
        raise ParseError("PROPERTY expects name")
    name = m.group(0)
    i = m.end()
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] not in ",;":
        raise ParseError("PROPERTY expects ',' after name")
    i += 1
    i = _skip_ws(s, i)
    # [[params], body] — same shape as FN body section
    if i >= len(s) or s[i] != "[":
        raise ParseError("PROPERTY expects [[params],body]")
    # Reuse FN bracket parse: fake by calling internal that expects [[params],body]
    # _parse_fn_brackets expects to start at '[' of FN[...]. Here we have [[params],body]
    # which is the inside of FN. Parse param list then body.
    i += 1  # consume outer '[' of [[params], body]
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "[":
        raise ParseError("PROPERTY params must be [[...],body]")
    params, i = _parse_param_list(s, i)
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] not in ",;":
        raise ParseError("PROPERTY expects ',' after params")
    i += 1
    body, i = _parse_atom(s, i)
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed PROPERTY params/body group")
    i += 1
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed PROPERTY[...]")
    return PropertyDecl(name=name, params=params, body=body, id=generate_id()), i + 1



def _parse_ident_list_args(s: str, i: int) -> tuple[list[str], int]:
    """Parse remaining comma-separated idents until ']' (does not consume ']')."""
    names: list[str] = []
    i = _skip_ws(s, i)
    if i < len(s) and s[i] == "]":
        return names, i
    while True:
        i = _skip_ws(s, i)
        m = _IDENT.match(s, i)
        if not m:
            raise ParseError("expected ident")
        names.append(m.group(0))
        i = m.end()
        i = _skip_ws(s, i)
        if i >= len(s) or s[i] == "]":
            return names, i
        if s[i] in ",;":
            i += 1
            continue
        raise ParseError("expected ',' or ']'")


def _parse_export_brackets(s: str, i: int) -> tuple[ExportList, int]:
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "[":
        raise ParseError("expected '[' after EXPORT")
    i += 1
    names, i = _parse_ident_list_args(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed EXPORT[...]")
    return ExportList(names=names, id=generate_id()), i + 1


def _parse_module_brackets(s: str, i: int) -> tuple[ModuleDecl, int]:
    """MODULE[name, items..., EXPORT[...]]"""
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "[":
        raise ParseError("expected '[' after MODULE")
    i += 1
    i = _skip_ws(s, i)
    m = _IDENT.match(s, i)
    if not m:
        raise ParseError("MODULE expects name")
    name = m.group(0)
    i = m.end()
    body = []
    exports: list[str] = []
    version = "0"
    i = _skip_ws(s, i)
    while i < len(s) and s[i] in ",;":
        i += 1
        i = _skip_ws(s, i)
        if i < len(s) and s[i] == "]":
            break
        # optional VERSION[1.2]
        if s[i:].upper().startswith("VERSION"):
            i2 = i + 7
            i2 = _skip_ws(s, i2)
            if i2 >= len(s) or s[i2] != "[":
                raise ParseError("VERSION expects [...]")
            args, i = _parse_arglist(s, i2)
            if len(args) != 1 or not isinstance(args[0], (LitExpr, IdentExpr)):
                raise ParseError("VERSION expects one atom")
            version = str(args[0].value if isinstance(args[0], LitExpr) else args[0].id)
            i = _skip_ws(s, i)
            continue
        node, i = _parse_atom(s, i)
        if isinstance(node, ExportList):
            exports = list(node.names)
        else:
            body.append(node)
        i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed MODULE[...]")
    return ModuleDecl(
        name=name, body=body, exports=exports, version=version, id=generate_id()
    ), i + 1


def _parse_import_brackets(s: str, i: int) -> tuple[ImportDecl, int]:
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "[":
        raise ParseError("expected '[' after IMPORT")
    i += 1
    i = _skip_ws(s, i)
    m = _IDENT.match(s, i)
    if not m:
        raise ParseError("IMPORT expects module name")
    mod = m.group(0)
    i = m.end()
    i = _skip_ws(s, i)
    names: list[str] = []
    if i < len(s) and s[i] in ",;":
        i += 1
        names, i = _parse_ident_list_args(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed IMPORT[...]")
    return ImportDecl(module=mod, names=names, id=generate_id()), i + 1


def _parse_depends_brackets(s: str, i: int) -> tuple[DependsDecl, int]:
    """DEPENDS[mod, version] or DEPENDS[mod, version, CAPS[a,b]]"""
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "[":
        raise ParseError("expected '[' after DEPENDS")
    i += 1
    i = _skip_ws(s, i)
    m = _IDENT.match(s, i)
    if not m:
        raise ParseError("DEPENDS expects module name")
    mod = m.group(0)
    i = m.end()
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] not in ",;":
        raise ParseError("DEPENDS expects version")
    i += 1
    i = _skip_ws(s, i)
    # version: number or ident or string
    ver_node, i = _parse_atom(s, i)
    if isinstance(ver_node, LitExpr):
        version = str(ver_node.value)
    elif isinstance(ver_node, IdentExpr):
        version = str(ver_node.id)
    else:
        raise ParseError("DEPENDS version must be atom")
    caps: list[str] = []
    i = _skip_ws(s, i)
    if i < len(s) and s[i] in ",;":
        i += 1
        i = _skip_ws(s, i)
        if s[i:].upper().startswith("CAPS"):
            i = i + 4
            i = _skip_ws(s, i)
            if i >= len(s) or s[i] != "[":
                raise ParseError("CAPS expects [...]")
            # CAPS may use dotted names like net.request — parse as idents with dots?
            i += 1
            caps, i = _parse_cap_names(s, i)
            if i >= len(s) or s[i] != "]":
                raise ParseError("unclosed CAPS[...]")
            i += 1
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed DEPENDS[...]")
    return DependsDecl(module=mod, version=version, caps=caps, id=generate_id()), i + 1


def _parse_cap_names(s: str, i: int) -> tuple[list[str], int]:
    """Parse capability names allowing dots: net.request, fs.read."""
    names: list[str] = []
    i = _skip_ws(s, i)
    if i < len(s) and s[i] == "]":
        return names, i
    while True:
        i = _skip_ws(s, i)
        m = _IDENT.match(s, i)
        if not m:
            raise ParseError("expected capability name")
        name = m.group(0)
        i = m.end()
        while i < len(s) and s[i] == ".":
            i += 1
            m2 = _IDENT.match(s, i)
            if not m2:
                raise ParseError("expected name after '.' in capability")
            name = name + "." + m2.group(0)
            i = m2.end()
        names.append(name)
        i = _skip_ws(s, i)
        if i >= len(s) or s[i] == "]":
            return names, i
        if s[i] in ",;":
            i += 1
            continue
        raise ParseError("expected ',' or ']' in CAPS")


def _parse_type_bracket(s: str, i: int, label: str) -> tuple[str, int]:
    """Parse IN[type] or OUT[type] starting at IN/OUT token end (at '[')."""
    if i >= len(s) or s[i] != "[":
        raise ParseError(label + " expects [...]")
    i += 1
    typ, i = _parse_type(s, i)
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed " + label + "[...]")
    return typ, i + 1


def _parse_conf_bracket(s: str, i: int) -> tuple[bool, int]:
    """Parse CONF[true|false] starting at '[' after CONF."""
    if i >= len(s) or s[i] != "[":
        raise ParseError("CONF expects [...]")
    i += 1
    i = _skip_ws(s, i)
    m = _IDENT.match(s, i)
    if not m:
        raise ParseError("CONF expects true or false")
    tok = m.group(0).lower()
    i = m.end()
    if tok not in ("true", "false"):
        raise ParseError("CONF expects true or false")
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed CONF[...]")
    return tok == "true", i + 1


def _parse_effects_bracket(s: str, i: int) -> tuple[list[str], int]:
    """Parse EFFECTS[a,b] starting at '[' after EFFECTS."""
    if i >= len(s) or s[i] != "[":
        raise ParseError("EFFECTS expects [...]")
    i += 1
    names, i = _parse_cap_names(s, i)
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed EFFECTS[...]")
    return names, i + 1


def _expect_comma(s: str, i: int) -> int:
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != ",":
        raise ParseError("expected ','")
    return i + 1


def _parse_model_brackets(s: str, i: int) -> tuple[ModelDecl, int]:
    """MODEL[name,IN[T],OUT[U],CONF[bool],EFFECTS[...]]"""
    if i >= len(s) or s[i] != "[":
        raise ParseError("expected '[' after MODEL")
    i += 1
    i = _skip_ws(s, i)
    m = _IDENT.match(s, i)
    if not m:
        raise ParseError("MODEL expects name")
    name = m.group(0)
    i = m.end()
    i = _expect_comma(s, i)
    i = _skip_ws(s, i)
    if not s[i:].upper().startswith("IN"):
        raise ParseError("MODEL expects IN[...]")
    i += 2
    in_t, i = _parse_type_bracket(s, i, "IN")
    i = _expect_comma(s, i)
    i = _skip_ws(s, i)
    if not s[i:].upper().startswith("OUT"):
        raise ParseError("MODEL expects OUT[...]")
    i += 3
    out_t, i = _parse_type_bracket(s, i, "OUT")
    i = _expect_comma(s, i)
    i = _skip_ws(s, i)
    if not s[i:].upper().startswith("CONF"):
        raise ParseError("MODEL expects CONF[...]")
    i += 4
    conf, i = _parse_conf_bracket(s, i)
    i = _expect_comma(s, i)
    i = _skip_ws(s, i)
    if not s[i:].upper().startswith("EFFECTS"):
        raise ParseError("MODEL expects EFFECTS[...]")
    i += 7
    effects, i = _parse_effects_bracket(s, i)
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed MODEL[...]")
    return (
        ModelDecl(
            name=name,
            in_type=in_t,
            out_type=out_t,
            confidence=conf,
            effects=effects,
            id=generate_id(),
        ),
        i + 1,
    )


def _parse_tool_brackets(s: str, i: int) -> tuple[ToolDecl, int]:
    """TOOL[name,IN[T],OUT[U],EFFECTS[...]]"""
    if i >= len(s) or s[i] != "[":
        raise ParseError("expected '[' after TOOL")
    i += 1
    i = _skip_ws(s, i)
    m = _IDENT.match(s, i)
    if not m:
        raise ParseError("TOOL expects name")
    name = m.group(0)
    i = m.end()
    i = _expect_comma(s, i)
    i = _skip_ws(s, i)
    if not s[i:].upper().startswith("IN"):
        raise ParseError("TOOL expects IN[...]")
    i += 2
    in_t, i = _parse_type_bracket(s, i, "IN")
    i = _expect_comma(s, i)
    i = _skip_ws(s, i)
    if not s[i:].upper().startswith("OUT"):
        raise ParseError("TOOL expects OUT[...]")
    i += 3
    out_t, i = _parse_type_bracket(s, i, "OUT")
    i = _expect_comma(s, i)
    i = _skip_ws(s, i)
    if not s[i:].upper().startswith("EFFECTS"):
        raise ParseError("TOOL expects EFFECTS[...]")
    i += 7
    effects, i = _parse_effects_bracket(s, i)
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed TOOL[...]")
    return (
        ToolDecl(name=name, in_type=in_t, out_type=out_t, effects=effects, id=generate_id()),
        i + 1,
    )


def _parse_invoke_brackets(s: str, i: int) -> tuple[InvokeExpr, int]:
    """INVOKE[name,arg...]"""
    if i >= len(s) or s[i] != "[":
        raise ParseError("expected '[' after INVOKE")
    i += 1
    i = _skip_ws(s, i)
    m = _IDENT.match(s, i)
    if not m:
        raise ParseError("INVOKE expects name")
    name = m.group(0)
    i = m.end()
    args = []
    i = _skip_ws(s, i)
    while i < len(s) and s[i] != "]":
        if s[i] != ",":
            raise ParseError("expected ',' or ']' in INVOKE")
        i += 1
        arg, i = _parse_atom(s, i)
        args.append(arg)
        i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed INVOKE[...]")
    return InvokeExpr(name=name, args=args, id=generate_id()), i + 1


def _parse_par_brackets(s: str, i: int) -> tuple[ParExpr, int]:
    """PAR[e1,e2,...]"""
    args, i = _parse_arglist(s, i)
    return ParExpr(branches=args, id=generate_id()), i


def _parse_seq_brackets(s: str, i: int) -> tuple[SeqExpr, int]:
    """SEQ[e1,e2,...]"""
    args, i = _parse_arglist(s, i)
    return SeqExpr(steps=args, id=generate_id()), i


def _parse_ref_brackets(s: str, i: int) -> tuple[RefExpr, int]:
    """REF[region,expr]"""
    if i >= len(s) or s[i] != "[":
        raise ParseError("expected '[' after REF")
    i += 1
    i = _skip_ws(s, i)
    m = _IDENT.match(s, i)
    if not m:
        raise ParseError("REF expects region name")
    region = m.group(0)
    i = m.end()
    i = _expect_comma(s, i)
    expr, i = _parse_atom(s, i)
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed REF[...]")
    return RefExpr(region=region, expr=expr, id=generate_id()), i + 1


def _parse_deref_brackets(s: str, i: int) -> tuple[DerefExpr, int]:
    """DEREF[expr]"""
    if i >= len(s) or s[i] != "[":
        raise ParseError("expected '[' after DEREF")
    i += 1
    expr, i = _parse_atom(s, i)
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed DEREF[...]")
    return DerefExpr(expr=expr, id=generate_id()), i + 1


def _parse_unsafe_brackets(s: str, i: int) -> tuple[UnsafeExpr, int]:
    """UNSAFE[CAPS[cap...],body]"""
    if i >= len(s) or s[i] != "[":
        raise ParseError("expected '[' after UNSAFE")
    i += 1
    i = _skip_ws(s, i)
    if not s[i:].upper().startswith("CAPS"):
        raise ParseError("UNSAFE expects CAPS[...]")
    i += 4
    if i >= len(s) or s[i] != "[":
        raise ParseError("CAPS expects [...]")
    i += 1
    caps, i = _parse_cap_names(s, i)
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed CAPS[...]")
    i += 1
    i = _expect_comma(s, i)
    body, i = _parse_atom(s, i)
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed UNSAFE[...]")
    return UnsafeExpr(caps=caps, body=body, id=generate_id()), i + 1


def _parse_match_brackets(s: str, i: int) -> tuple[MatchExpr, int]:
    """MATCH[scrutinee, CASE[tag, body]|CASE[tag, name, body], ...]"""
    if i >= len(s) or s[i] != "[":
        raise ParseError("expected '[' after MATCH")
    i += 1
    scrutinee, i = _parse_atom(s, i)
    cases: list[MatchCase] = []
    i = _skip_ws(s, i)
    while i < len(s) and s[i] != "]":
        if s[i] != ",":
            raise ParseError("expected ',' or ']' in MATCH")
        i += 1
        i = _skip_ws(s, i)
        if not s[i:].upper().startswith("CASE"):
            raise ParseError("MATCH arms must be CASE[...]")
        i += 4
        if i >= len(s) or s[i] != "[":
            raise ParseError("CASE expects [...]")
        i += 1
        i = _skip_ws(s, i)
        # tag: ident or 'string'
        if i < len(s) and s[i] in "'\"":
            tag_node, i = _parse_atom(s, i)
            from knot.ast import LitExpr

            if not isinstance(tag_node, LitExpr) or not isinstance(tag_node.value, str):
                raise ParseError("CASE tag must be ident or string")
            tag = tag_node.value
        else:
            m = _IDENT.match(s, i)
            if not m:
                raise ParseError("CASE expects tag")
            tag = m.group(0)
            i = m.end()
        i = _expect_comma(s, i)
        # either body, or binding, body
        first, i = _parse_atom(s, i)
        i = _skip_ws(s, i)
        binding = None
        body = first
        if i < len(s) and s[i] == ",":
            # first was binding ident
            from knot.ast import IdentExpr

            if not isinstance(first, IdentExpr):
                raise ParseError("CASE binding must be ident")
            binding = str(first.id)
            i += 1
            body, i = _parse_atom(s, i)
            i = _skip_ws(s, i)
        if i >= len(s) or s[i] != "]":
            raise ParseError("unclosed CASE[...]")
        i += 1
        cases.append(MatchCase(tag=tag, body=body, binding=binding))
        i = _skip_ws(s, i)
    if i >= len(s) or s[i] != "]":
        raise ParseError("unclosed MATCH[...]")
    return MatchExpr(scrutinee=scrutinee, cases=cases, id=generate_id()), i + 1
