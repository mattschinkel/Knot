"""Pretty printer: AST -> human-readable F(...) / infix view (phase1_spec §5).

Canonical source is bracket notation; this is a view only. Never emit `[` `]`.
"""
from __future__ import annotations

from golem.ast import (
    CallExpr,
    CondExpr,
    DefNode,
    DerefExpr,
    FieldAccess,
    FnExpr,
    HoleExpr,
    IdentExpr,
    IfExpr,
    LetExpr,
    LitExpr,
    MatchExpr,
    ModelDecl,
    ModuleDecl,
    OpExpr,
    ParExpr,
    RefExpr,
    SeqExpr,
    ToolDecl,
    TypedLit,
    UnitExpr,
    UnsafeExpr,
    WithExpr,
    ErrExpr,
)

_INFIX = {
    "ADD": "+",
    "SUB": "-",
    "MUL": "*",
    "DIV": "/",
    "MOD": "%",
    "EQ": "==",
    "NE": "!=",
    "LT": "<",
    "LE": "<=",
    "GT": ">",
    "GE": ">=",
    "AND": "and",
    "OR": "or",
}

_UNARY = {
    "NEG": "-",
    "NOT": "not ",
}


def print_ast(node) -> str:
    """Pretty-print an AST node or a list of nodes (program)."""
    if node is None:
        return ""
    if isinstance(node, (list, tuple)):
        return "\n".join(print_ast(n) for n in node)
    return _print(node)


def _print(node) -> str:
    if isinstance(node, DefNode):
        return _print_def(node)
    if isinstance(node, FnExpr):
        return _print_fn(node)
    if isinstance(node, OpExpr):
        return _print_op(node)
    if isinstance(node, FieldAccess):
        return _print_field(node)
    if isinstance(node, CallExpr):
        args = ", ".join(_print(a) for a in node.args)
        return _print(node.fn) + "(" + args + ")"
    if isinstance(node, IfExpr):
        return (
            "if "
            + _print(node.cond)
            + " then "
            + _print(node.then_branch)
            + " else "
            + _print(node.else_branch)
        )
    if isinstance(node, CondExpr):
        return "cond(" + _print(node.cond) + ")"
    if isinstance(node, MatchExpr):
        arms = ", ".join(
            "case "
            + c.tag
            + (("(" + c.binding + ")" if c.binding else ""))
            + " => "
            + _print(c.body)
            for c in node.cases
        )
        return "match " + _print(node.scrutinee) + " { " + arms + " }"
    if isinstance(node, ModuleDecl):
        body = "; ".join(_print(b) for b in node.body)
        ex = ", ".join(node.exports) if node.exports else ""
        return "module " + str(node.name) + " { " + body + (" export " + ex if ex else "") + " }"
    if isinstance(node, ParExpr):
        return "par(" + ", ".join(_print(b) for b in node.branches) + ")"
    if isinstance(node, SeqExpr):
        return "seq(" + ", ".join(_print(s) for s in node.steps) + ")"
    if isinstance(node, RefExpr):
        return "ref@" + str(node.region) + "(" + _print(node.expr) + ")"
    if isinstance(node, DerefExpr):
        return "deref(" + _print(node.expr) + ")"
    if isinstance(node, UnsafeExpr):
        caps = ", ".join(node.caps)
        return "unsafe[" + caps + "](" + _print(node.body) + ")"
    if isinstance(node, ModelDecl):
        return "model " + str(node.name)
    if isinstance(node, ToolDecl):
        return "tool " + str(node.name)
    if isinstance(node, LetExpr):
        return _print_let(node)
    if isinstance(node, WithExpr):
        return _print_with(node)
    if isinstance(node, HoleExpr):
        if node.label:
            return "?:" + str(node.label)
        return "?"
    if isinstance(node, ErrExpr):
        path = "[" + ", ".join(str(p) for p in node.path) + "]"
        fixes = "".join(", " + _print(f) for f in node.fixes)
        return (
            "err("
            + str(node.code)
            + ", "
            + path
            + ", "
            + str(node.expected)
            + ", "
            + str(node.actual)
            + fixes
            + ")"
        )
    if isinstance(node, TypedLit):
        return _lit_text(node.value) + ":" + str(node.type_name)
    if isinstance(node, LitExpr):
        return _lit_text(node.value)
    if isinstance(node, IdentExpr):
        return str(node.id)
    if isinstance(node, UnitExpr):
        return "unit"
    # Fallback: unknown node types
    return str(node)


def _lit_text(value) -> str:
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"
    return str(value)


def _print_param(param) -> str:
    if isinstance(param, (list, tuple)) and len(param) >= 1:
        name = param[0]
        typ = param[1] if len(param) > 1 else None
        if typ:
            return str(name) + ": " + str(typ)
        return str(name)
    return _print(param)


def _print_fn(node: FnExpr, name: str | None = None) -> str:
    params = ", ".join(_print_param(p) for p in node.params)
    body = _print(node.body)
    if name is not None:
        return "fn " + name + "(" + params + ") { " + body + " }"
    return "fn(" + params + ") { " + body + " }"


def _print_def(node: DefNode) -> str:
    if isinstance(node.body, FnExpr):
        return _print_fn(node.body, name=node.name)
    return node.name + " = " + _print(node.body)


def _print_field(node: FieldAccess) -> str:
    base = node.id
    if hasattr(base, "__class__") and not isinstance(base, (str, int, float, bool)):
        base_s = _print(base)
    else:
        base_s = str(base)
    return base_s + "." + str(node.field_name)


def _print_op(node: OpExpr) -> str:
    op = str(node.op).upper()
    kids = list(node.children)

    # Field sugar: GET[obj, field] -> obj.field
    if op == "GET" and len(kids) == 2:
        field = kids[1]
        field_name = field.id if isinstance(field, IdentExpr) else _print(field)
        return _print(kids[0]) + "." + str(field_name)

    if op in _UNARY and len(kids) == 1:
        return _UNARY[op] + _print(kids[0])

    if op in _INFIX and len(kids) == 2:
        return _print(kids[0]) + " " + _INFIX[op] + " " + _print(kids[1])

    if op == "IF" and len(kids) == 3:
        return (
            "if "
            + _print(kids[0])
            + " then "
            + _print(kids[1])
            + " else "
            + _print(kids[2])
        )

    # F(...) shorthand — never brackets
    args = ", ".join(_print(c) for c in kids)
    return op + "(" + args + ")"


def _print_let(node: LetExpr) -> str:
    return "LET(" + str(node.id) + ")"


def _print_with(node: WithExpr) -> str:
    return "WITH(" + str(node.id) + ")"
