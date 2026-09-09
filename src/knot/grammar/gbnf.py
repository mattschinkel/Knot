"""GBNF grammar for Knot AIR constrained decoding (phase1_spec §7).

Exports named production strings plus a full grammar text. Bracket notation
only; no F(...) shorthand; no numeric node IDs in the grammar (D5 / §21).
"""
from __future__ import annotations

import re

# --- Named productions (identifiers match phase1_tasks T24 / phase1_spec §7) ---

Program = r'program ::= def*'

Def = r'def ::= ident "=" expr'

Expr = (
    r'expr ::= lit | ident | field-access | get | set | op-expr | if-expr | '
    r'cond-expr | match-expr | let-expr | with-expr | hole | fn-expr | call | unit'
)

Lit = r'lit ::= number | string | bool | nil | typed-lit'

Ident = r'ident ::= identifier'

FieldAccess = r'field-access ::= ident "." ident'

Get = r'get ::= "GET[" ident "," ident "]"'

Set = r'set ::= "SET[" ident "," ident "," expr "]"'

Op = r'op ::= "ADD" | "SUB" | "MUL" | "DIV" | "MOD" | "NEG"'

Comparison = r'comparison ::= "EQ" | "NE" | "LT" | "LE" | "GT" | "GE"'

Logic = r'logic ::= "AND" | "OR" | "NOT"'

Control = r'control ::= "IF" | "COND" | "MATCH"'

Access = r'access ::= "GET" | "SET" | "FIELD"'

Collection = (
    r'collection ::= "MAP" | "FILTER" | "REDUCE" | "FOLD" | "LEN" | "AT" | '
    r'"APPEND" | "CONCAT"'
)

Binding = r'binding ::= "LET" | "WITH"'

Hole = r'hole ::= "?" | "?:" ident'

Function = r'fn-expr ::= "FN[" param-list "]" body'

ParamList = r'param-list ::= param ("," param)*'

Param = r'param ::= ident | ident ":" ident'

Body = r'body ::= expr'

Unit = r'unit ::= "UNIT"'

# Supporting terminals / composites used above
_SUPPORT = [
    r'op-expr ::= op "[" arg-list "]"',
    r'if-expr ::= "IF[" expr "," expr "," expr "]"',
    r'cond-expr ::= "COND[" arg-list "]"',
    r'match-expr ::= "MATCH[" arg-list "]"',
    r'let-expr ::= "LET[" arg-list "]"',
    r'with-expr ::= "WITH[" arg-list "]"',
    r'call ::= ident "[" arg-list "]"',
    r'arg-list ::= expr ("," expr)*',
    r'typed-lit ::= lit-atom ":" ident',
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
}


def grammar_text() -> str:
    """Full GBNF text suitable for constrained decoding."""
    parts = list(RULES.values()) + list(_SUPPORT)
    return "\n".join(parts) + "\n"


def has_numeric_node_ids(text: str | None = None) -> bool:
    """True if grammar text appears to allow authored numeric node IDs.

    Detects ID/node-id style rules that consume bare integers as addresses.
    Literal digit tokens inside keywords (none) and number literals for values
    are fine; forbidding `id ::= [0-9]+` / `node-id` productions is the goal.
    """
    src = grammar_text() if text is None else text
    if re.search(r"(?i)\b(node[_-]?id|numeric[_-]?id)\b\s*::=", src):
        return True
    if re.search(r'(?i)\bid\s*::=\s*\[0-9\]', src):
        return True
    # Bracket form must not include a free-standing integer ID slot like OP[123, ...]
    # as a grammar alternative for addressing.
    if re.search(r'(?i)"@"\s*[0-9]', src):
        return True
    return False


def uses_paren_shorthand(text: str | None = None) -> bool:
    """True if grammar allows F(...) call/op shorthand (forbidden in GBNF)."""
    src = grammar_text() if text is None else text
    # Disallow productions that open ops/calls with '(' instead of '['
    return bool(re.search(r'"(?:ADD|SUB|MUL|FN|GET|SET)"\s*"\("', src))
