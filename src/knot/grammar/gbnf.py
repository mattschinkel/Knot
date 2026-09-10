"""GBNF grammar for Knot AIR constrained decoding (D-FB1–D-FB5 / 10/10 LLM bar).

Canonical form is ONE shape: NAME[ARGS] (+ atoms). No field-access sugar,
no `name = expr`, no FN[params] body juxta-position — those are pretty-only.
No numeric node IDs in the grammar (§21).
"""
from __future__ import annotations

import re

# --- Named productions ---

Program = r'program ::= def*'

Def = r'def ::= "DEF[" ident "," expr "]"'

Expr = (
    r'expr ::= lit | ident | get | set | op-expr | if-expr | '
    r'cond-expr | match-expr | let-expr | with-expr | hole | fn-expr | '
    r'def | call | unit | err'
)

Lit = r'lit ::= number | string | bool | nil | typed-lit'

Ident = r'ident ::= identifier'

# Pretty-only; not part of canonical expr (kept for documentation / tooling)
FieldAccess = r'field-access ::= ident "." ident   # PRETTY-ONLY; canonical uses GET'

Get = r'get ::= "GET[" expr "," ident "]"'

Set = r'set ::= "SET[" expr "," ident "," expr "]"'

Op = r'op ::= "ADD" | "SUB" | "MUL" | "DIV" | "MOD" | "NEG"'

Comparison = r'comparison ::= "EQ" | "NE" | "LT" | "LE" | "GT" | "GE"'

Logic = r'logic ::= "AND" | "OR" | "NOT"'

Control = r'control ::= "IF" | "COND" | "MATCH"'

Access = r'access ::= "GET" | "SET" | "FIELD"'

Collection = (
    r'collection ::= "MAP" | "FILTER" | "REDUCE" | "FOLD" | "LEN" | "AT" | '
    r'"APPEND" | "CONCAT"'
)

Binding = r'binding ::= "DEF" | "WITH"'

Hole = r'hole ::= "?" | "?:" type'

Function = r'fn-expr ::= "FN[" "[" param-list "]" "," body "]"'

ParamList = r'param-list ::= param ("," param)*'

Param = r'param ::= ident | ident ":" type'

Body = r'body ::= expr'

Unit = r'unit ::= "UNIT"'

Err = (
    r'err ::= "ERR[" ident "," path "," type "," type ("," fix)* "]" | '
    r'"ERROR[" arg-list "]"'
)

_SUPPORT = [
    r'op-expr ::= (op | comparison | logic | control | access | collection | binding) "[" arg-list "]"',
    r'if-expr ::= "IF[" expr "," expr "," expr "]"',
    r'cond-expr ::= "COND[" arg-list "]"',
    r'match-expr ::= "MATCH[" arg-list "]"',
    r'let-expr ::= "LET[" arg-list "]"   # legacy; prefer DEF',
    r'with-expr ::= "WITH[" arg-list "]"',
    r'call ::= ident "[" arg-list "]"',
    r'arg-list ::= expr ("," expr)*',
    r'typed-lit ::= lit-atom ":" type',
    r'type ::= identifier ("@" identifier)?',
    r'path ::= "[" (ident | number) ("," (ident | number))* "]"',
    r'fix ::= expr',
    r'lit-atom ::= number | string | bool | nil',
    r'number ::= "-"? [0-9]+ ("." [0-9]+)?',
    r'string ::= "\'" [^\'\\]* ("\\" . [^\'\\]*)* "\'"',
    r'bool ::= "true" | "false"',
    r'nil ::= "nil"',
    r'identifier ::= [A-Za-z_][A-Za-z0-9_]*',
    r'ws ::= [ \t\n]*',
]

RULES: dict[str, str] = {
    "Program": Program,
    "Def": Def,
    "Expr": Expr,
    "Lit": Lit,
    "Ident": Ident,
    "FieldAccess": FieldAccess,
    "Get": Get,
    "Set": Set,
    "Op": Op,
    "Comparison": Comparison,
    "Logic": Logic,
    "Control": Control,
    "Access": Access,
    "Collection": Collection,
    "Binding": Binding,
    "Hole": Hole,
    "Function": Function,
    "ParamList": ParamList,
    "Param": Param,
    "Body": Body,
    "Unit": Unit,
    "Err": Err,
}


def grammar_text() -> str:
    """Full GBNF text suitable for constrained decoding."""
    parts = list(RULES.values()) + list(_SUPPORT)
    return "\n".join(parts) + "\n"


def has_numeric_node_ids(text: str | None = None) -> bool:
    """True if grammar text appears to allow authored numeric node IDs."""
    src = grammar_text() if text is None else text
    if re.search(r"(?i)\b(node[_-]?id|numeric[_-]?id)\b\s*::=", src):
        return True
    if re.search(r'(?i)\bid\s*::=\s*\[0-9\]', src):
        return True
    if re.search(r'(?i)"@"\s*[0-9]', src):
        return True
    return False


def uses_paren_shorthand(text: str | None = None) -> bool:
    """True if grammar allows F(...) call/op shorthand (forbidden in GBNF)."""
    src = grammar_text() if text is None else text
    return bool(re.search(r'"(?:ADD|SUB|MUL|FN|GET|SET)"\s*"\("', src))
